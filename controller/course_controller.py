from flask import Blueprint, render_template, request, redirect, url_for
from lib.helper import render_result, render_err_result, user_data_path, read_courses
from model.user import User
from model.course import Course
from model.user_instructor import Instructor
from pandas import DataFrame

from flask import render_template, Blueprint

course_page = Blueprint("course_page", __name__)

model_course = Course()
model_instructor = Instructor()
model_user = User()

@course_page.route("/reset-database", methods=["POST"])
def reset_database():
    '''Clear all data from user.txt and course.txt'''

    if request.method == "POST":
        if User.current_login_user.role == "admin":
            User.current_login_user = None
            model_course.clear_course_data()
            with open(user_data_path,"w",encoding="utf-8") as file:
                file.write("")
            return render_result(msg="database cleared successfully")
        else:
            return render_err_result(msg="you have no permission for doing this")

@course_page.route("/course-list")
def course_list():
    
    # check current login user
    if User.current_login_user:
        page = int(request.args.get("page",1))
        popup = False

        # get values for one_page_course_list, total_pages, total_num
        one_page_course_list, total_pages, total_num = model_course.get_courses_by_page(page)

        # check one_page_course_list, make sure this variable not be None, if None, assign it to []
        if not one_page_course_list:
            one_page_course_list = []
        if page > total_pages:
            popup = True
            page = 1

        # get values for page_num_list
        page_num_list = model_course.generate_page_num_list(page,total_pages)

        context = dict(
            one_page_course_list=one_page_course_list,
            total_pages=total_pages,
            page_num_list=page_num_list,
            current_page=page,
            total_num=total_num,
            current_user_role=User.current_login_user.role,
            popup=popup
        )
        return render_template("02course_list.html", **context)

    else:
        return redirect(url_for("index_page.index",current_user_role=None))

@course_page.route("/process-course", methods=["POST"])
def process_course():
    try:
        model_course.get_courses()
    except Exception as e:
        print(e)
        return render_err_result(msg="error in process course")
    return render_result(msg="process course finished successfully")

@course_page.route("/course-details")
def course_details():
    context = {}
    if User.current_login_user:
        course_id = int(request.args.get("id",-1))

        if course_id == -1:
            course = None
        else:
            course, overall_comment = model_course.get_course_by_course_id(course_id)

        if not course:
            context["course_error_msg"] = "Error, cannot find course"
        else:
            context['course'] = course
            context['overall_comment'] = overall_comment
        context['current_user_role'] = User.current_login_user.role

    return render_template("03course_details.html", **context)


@course_page.route("/course-delete")
def course_delete():
    course_id = int(request.args.get("id",-1))
    if course_id == -1:
        return render_err_result(msg="course cannot find")
    else:
        result = model_course.delete_course_by_id(course_id)
        if result:
            return redirect(url_for("course_page.course_list"))
        else:
            return render_err_result(msg="course delete error")

@course_page.route("/course-analysis")
def course_analysis():
    
    # check current login user
    if User.current_login_user:
        courses = DataFrame(read_courses())
        if courses.shape[0] == 0:
            return render_err_result(msg="no courses in datafile")
        else:
            context = dict(
                explain1=model_course.generate_course_figure1(),
                explain2=model_course.generate_course_figure2(),
                explain3=model_course.generate_course_figure3(),
                explain4=model_course.generate_course_figure4(),
                explain5=model_course.generate_course_figure5(),
                explain6=model_course.generate_course_figure6(),
                current_user_role=User.current_login_user.role
            )
            return render_template("04course_analysis.html", **context)
    else:
        return redirect(url_for("index_page.index", current_user_role=None))