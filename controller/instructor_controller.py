from flask import Blueprint, render_template, request, redirect, url_for
from lib.helper import render_result, render_err_result, read_users
from model.user import User
from model.course import Course
from pandas import DataFrame

from flask import render_template, Blueprint

from model.user_instructor import Instructor

instructor_page = Blueprint("instructor_page", __name__)

model_instructor = Instructor()
model_course = Course()

@instructor_page.route("/instructor-list")
def instructor_list():
    
    # check current login user
    if User.current_login_user:

        # get page value from request parameter, return 1 if None
        page = int(request.args.get("page",1))
        popup = False

        # get values for one_page_instructor_list, total_pages, total_num
        one_page_instructor_list, total_pages, total_num = model_instructor.get_instructors_by_page(page)

        # get values for page_num_list
        page_num_list = model_course.generate_page_num_list(page,total_pages)

        # check one_page_instructor_list, make sure this variable not be None, if None, assign it to []
        if not one_page_instructor_list:
            one_page_instructor_list = []
        if page > total_pages:
            popup = True
            page = 1

        # define context variable
        context = dict(
            one_page_instructor_list=one_page_instructor_list,
            total_pages=total_pages,
            page_num_list=page_num_list,
            current_page=page,
            total_num=total_num,
            current_user_role=User.current_login_user.role, # add "current_user_role" to context
            popup=popup
        )

    else:
        
        # return to home page if no login user
        return redirect(url_for("index_page.index"))

    # render instructor list html
    return render_template("07instructor_list.html", **context)

@instructor_page.route("/teach-courses")
def teach_courses():

    # check current login user
    if User.current_login_user:

        # get instructor id
        instructor_id = request.args.get("id",None)
        if not instructor_id:
            instructor_id = User.current_login_user.uid

        # get values for course_list, total_num
        course_list, total_num = model_course.get_course_by_instructor_id(int(instructor_id))
        i = 1
        for course in course_list:
            course.update({"index":i})
            i += 1

        # define context variable
        context = dict(
            course_list=course_list,
            total_num=total_num,
            current_user_role=User.current_login_user.role # add "current_user_role" to context
        )

    else:
        return redirect(url_for("index_page.index"))
    return render_template("09instructor_courses.html", **context)

@instructor_page.route("/instructor-analysis")
def instructor_analysis():

    # check current login user
    if User.current_login_user:
        
        # check data
        instructors = DataFrame(read_users("instructor"))
        if instructors.shape[0] == 0:
            return render_err_result(msg="no instructor in datafile")

        # generate figure out of the data
        context = dict(
            explain1=model_instructor.generate_instructor_figure1(),
            current_user_role=User.current_login_user.role
        )
        return render_template("08instructor_analysis.html", **context)

    # if there's no login user, rediret it to the homepage
    else:
        return redirect(url_for("index_page.index"))

@instructor_page.route("/process-instructor", methods=["POST"])
def process_instructor():
    try:
        model_instructor.get_instructors()
    except Exception as e:
        print(e)
        return render_err_result(msg="error in process instructors")
    return render_result(msg="process instructors finished successfully")