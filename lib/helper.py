"""
helper file: saves some constant values and util functions
Xinyu Li
30/3/2022
"""
from flask import jsonify
from datetime import datetime
from math import ceil

course_data_path = "data/course.txt"
user_data_path = "data/user.txt"

course_json_files_path = "data/source_course_files"
figure_save_path = "static/img/"


def render_result(code=200, msg="success"):
    resp = {"code": code, "msg": msg}
    return jsonify(resp)


def render_err_result(code=-1, msg="system busy"):
    resp = {"code": code, "msg": msg}
    return jsonify(resp)


def get_day_from_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).day

def paginate(array:list, devider:int) -> list:
    '''Paginate the list.'''

    d = ceil(len(array)/devider)
    if d > 1:
        x = [i*devider if i != d else len(array) for i in range(d+1)]
        array = [array[x[i]:x[i+1]] for i in range(len(x)-1)]
        return array
    elif d == 1:
        return [array]
    elif d == 0:
        return []

def read_users(role:str) -> list:
    '''Read user.txt and filter it by role.'''

    if role == "student":
        keys = [
            "uid",
            "username",
            "password",
            "register_time",
            "role",
            "email"
        ]
    elif role == "instructor":
        keys = [
            "uid",
            "username",
            "password",
            "register_time",
            "role",
            "email",
            "display_name",
            "job_title",
            "course_id_list"
        ]
    index = 1
    users = []
    with open(user_data_path, encoding="utf-8") as file:
        user_data = file.read().split("\n")
        for row in user_data:
            if row != "":
                user = {k:v for k,v in zip(keys,row.split(";;;"))}
                user.update({"index":index})
                user['uid'] = int(user['uid'])
                if user['role'] == role:
                    users.append(user)
                    index += 1
    if len(users) > 0:
        return users
    else:
        return {}
    
def read_courses() -> list:
    '''Read course.txt'''

    keys = [
        "category_title",
        "subcategory_id",
        "subcategory_title",
        "subcategory_description",
        "subcategory_url",
        "course_id",
        "course_title",
        "course_url",
        "num_of_subscribers",
        "avg_rating",
        "num_of_reviews"
    ]
    index = 1
    with open(course_data_path,encoding="utf-8") as file:
        courses = file.read().split("\n")
        for i,row in enumerate(courses):
            if row != "":
                courses[i] = {k:v for k,v in zip(keys,row.split(";;;"))}
                courses[i].update({"index":index})
                courses[i]['subcategory_id'] = int(courses[i]['subcategory_id'])
                courses[i]['course_id'] = int(courses[i]['course_id'])
                courses[i]['avg_rating'] = float(courses[i]['avg_rating'])
                courses[i]['num_of_reviews'] = int(courses[i]['num_of_reviews'])
                courses[i]['num_of_subscribers'] = int(courses[i]['num_of_subscribers'])
                index+=1
    return [c for c in courses if c!=""]