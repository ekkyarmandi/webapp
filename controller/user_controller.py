from flask import Blueprint, render_template, request, redirect, url_for
from lib.helper import render_result, render_err_result, course_data_path, user_data_path
from model.course import Course
from model.user import User
from model.user_admin import Admin
from model.user_instructor import Instructor
from model.user_student import Student
import re

user_page = Blueprint("user_page", __name__)

model_user = User()
model_course = Course()
model_student = Student()

def generate_user(username):
    
    # read user.txt and look for the mathces username
    with open(user_data_path,encoding="utf-8") as file:
        users_str = file.read().split("\n")
        username_role = [";;;".join([line.split(";;;")[1],line.split(";;;")[4]]) for line in users_str if line!=""]
        for i,line in enumerate(username_role):
            if username == line.split(";;;")[0]:
                role = line.split(";;;")[-1]
                login_user_str = users_str[i].split(";;;")
                if role == "admin":
                    user = Admin(
                        uid=int(login_user_str[0]),
                        username=login_user_str[1],
                        password="".join(re.findall("[A-Za-z0-9]+",login_user_str[2])),
                        register_time=login_user_str[3],
                        role=login_user_str[4]
                    )
                elif role == "instructor":
                    user = Instructor(
                        uid=int(login_user_str[0]),
                        username=login_user_str[1],
                        password="".join(re.findall("[A-Za-z0-9]+",login_user_str[2])),
                        register_time=login_user_str[3],
                        role=login_user_str[4],
                        email=login_user_str[5],
                        display_name=login_user_str[6],
                        job_title=login_user_str[7],
                        course_id_list=login_user_str[8]
                    )
                elif role == "student":
                    user = Student(
                        uid=int(login_user_str[0]),
                        username=login_user_str[1],
                        password="".join(re.findall("[A-Za-z0-9]+",login_user_str[2])),
                        register_time=login_user_str[3],
                        role=login_user_str[4],
                        email=login_user_str[5]
                    )
                model_user.current_login_user = user
                return user

@user_page.route("/logout")
def logout():
    '''Logout current login user'''

    # logout and assign None value into User.current_login_user
    User.current_login_user = None
    return render_template("01index.html")

@user_page.route("/login", methods=["GET"])
def login():
    '''Render the Login Page'''
    return render_template("00login.html")

@user_page.route("/login", methods=["POST"])
def login_post():
    '''Make a POST request for login into the app'''

    # get username and password from AJAX request
    username = request.form.get("username")
    password = request.form.get("password")

    # authenticate username and password
    if model_user.authenticate_user(username,password):
        User.current_login_user = generate_user(username)
        return render_result(msg="login successful")
    elif not model_user.check_username_exist(username):
        return render_err_result(msg=f"{username} username does not exists in the system")
    else:
        return render_err_result(msg="make sure you type the correct password")

@user_page.route("/register", methods=["GET"])
def register():
    '''Render the Register Page'''
    return render_template("00register.html")

@user_page.route("/register", methods=["POST"])
def register_post():
    
    # get request values from register form
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    role = request.form.get("role")
    register_time = request.form.get("register_time")

    # register new user
    if not model_user.check_username_exist(username):

        trues = [
            model_user.validate_username(username),
            model_user.validate_password(password),
            model_user.validate_email(email)
        ]
    
        if all(trues):
            model_user.register_user(
                username=username,
                password=model_user.encrypt_password(password,sign="&",rep=2),
                email=email,
                register_time=float(register_time),
                role=role
            )
            return render_result(msg=f"new user registered as {role}")
        
        else:
            # validate the username
            if not trues[0]:
                msg = f"{username} is not a valid username"
                return render_err_result(msg=msg)

            # validate the password
            elif not trues[1]:
                msg = f"not a valid password combination"
                return render_err_result(msg=msg)

            # validate email
            elif not trues[2]:
                msg = f"{email} is not a valid email format"
                return render_err_result(msg=msg)
    else:
        msg = f"'{username}' have been registered"
        return render_err_result(msg=msg)

@user_page.route("/student-list")
def student_list():

    # check current login user
    if User.current_login_user.role == "admin":

        # get page number from the parameter
        page = int(request.args.get("page",1))
        popup = False

        # get values for one_page_student_list, total_pages, total_num
        one_page_student_list, total_pages, total_num = model_student.get_students_by_page(page)

        # check one_page_course_list, make sure this variable not be None, if None, assign it to []
        if not one_page_student_list:
            one_page_student_list = []
        if page > total_pages and total_pages != 0:
            popup = True
            page = 1

        # get values for page_num_list
        page_num_list = model_course.generate_page_num_list(page,total_pages)

        context = dict(
            current_page=page,
            one_page_user_list=one_page_student_list,
            total_num=total_num,
            page_num_list=page_num_list,
            total_pages=total_pages,
            current_user_role=User.current_login_user.role,
            popup=popup
        )

    else:
        return redirect(url_for("index_page.index"))
    return render_template("10student_list.html", **context)

@user_page.route("/student-info")
def student_info():
    if User.current_login_user:
        id_ = request.args.get("id")
        id_ = User.current_login_user.uid if not id_ else id_
        context = model_student.get_student_by_id(id_)
        role = User.current_login_user.role
        previous_page = "Home" if role == "student" else "Student List"
        context.update({
            "current_user_role": role,
            "previous_page": previous_page
        })
        return render_template("11student_info.html", **context)
    else:
        return redirect(url_for("index_page.index"))


@user_page.route("/student-delete")
def student_delete():
    id_ = request.args.get("id")
    if id_:
        model_student.delete_student_by_id(id_)
        return redirect(url_for("user_page.student_list"))
    else:
        return redirect(url_for("index_page.index"))