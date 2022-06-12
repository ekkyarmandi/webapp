from model.user import User
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np
import json
import os

from lib.helper import read_users, datetime, user_data_path, course_json_files_path, paginate, figure_save_path

class Instructor(User):
    def __init__(self,
        uid:int=-1,
        username:str="",
        password:str="",
        register_time:str="yyyy-MM-dd_HH:mm:ss.SSS",
        role:str="instructor",
        email:str="",
        display_name:str="",
        job_title:str="",
        course_id_list:list=[]
    ):
        '''Instructor constructor'''

        self.uid=str(uid)
        self.username=username
        self.password=self.encrypt_password(password)
        self.register_time=self.date_conversion(register_time)
        self.role=role
        self.email=email
        self.display_name=display_name
        self.job_title=job_title
        self.course_id_list=course_id_list

    def __str__(self):
        instructor = [
            self.uid,
            self.username,
            self.password,
            self.register_time,
            self.role,
            self.email,
            self.display_name,
            self.job_title,
            "--".join(self.course_id_list)
        ]
        return ";;;".join(instructor)

    def get_instructors(self):
        '''Retrive instructor data from source data'''

        def extract(path:str, instructors:dict) -> dict:
            '''Extract instructors from course data'''
            
            # read file
            data = json.load(open(path,encoding="utf-8"))

            # get instructor id, name, and course id list register time use the default value (yyyy-MM-dd_HH:mm:ss.SSS)
            items = data['unitinfo']['items']
            for item in items:

                ## get instrucor id and name
                if item['_class'] == "course":
                    course_id = item['id']
                    for user in item['visible_instructors']:
                        if user['_class'] == "user":
                            instructor_id = str(user['id'])
                            if instructor_id not in instructors:
                                username = user['display_name'].lower().replace(" ","_")
                                instructor = dict(
                                    name=user['display_name'],
                                    username=username,
                                    password=self.encrypt_password(instructor_id,sign="&",rep=2),
                                    email=username+"@gmail.com",
                                    register_time=self.date_conversion(datetime.now().timestamp()),
                                    job_title=user['job_title'],
                                    course_id_list=[course_id]
                                )
                                instructors.update({instructor_id:instructor})
                            else:

                                ## collecting course id into the list
                                if course_id not in instructors[instructor_id]['course_id_list']:
                                    instructors[instructor_id]['course_id_list'].append(course_id)
            return instructors

        # read all json files from source_course_files folder
        instructors = {}
        for root,_,files in os.walk(course_json_files_path):
            for file in files:
                if file.endswith("json"):

                    # get instructors from data
                    file_path = os.path.join(root,file)
                    instructors = extract(path=file_path, instructors=instructors)
        
        # save instructors string into user.txt
        with open(user_data_path,"a",encoding="utf-8") as file:
            for id_ in instructors:
                course_id_list = [str(d) for d in instructors[id_]['course_id_list']]
                string = [
                    id_,
                    instructors[id_]['username'],
                    instructors[id_]['password'],
                    self.register_time,
                    "instructor",
                    instructors[id_]['email'],
                    instructors[id_]['name'],
                    instructors[id_]['job_title'],
                    "--".join(course_id_list)
                ]
                file.write(";;;".join(string)+"\n")

    def get_instructors_by_page(self, page:int or str):

        # convert page value into integer
        page = int(page)
        
        # read user.txt and filter it by instructor role
        instructors = read_users("instructor")
        total_num = len(instructors)

        # turn the list into pagination and count for total pages
        instructors = paginate(instructors,20)
        total_pages = len(instructors)

        # if page not in total pages return None
        if page <= total_pages:

            # get students by page
            one_page_student_list = instructors[page-1]

            # return the student list, total pages, and total students as a tuple
            return one_page_student_list, total_pages, total_num

        else:
            return None, 0, 0

    def generate_instructor_figure1(self):
        
        # read instructors data
        data = DataFrame(read_users("instructor"))
        data['total_course'] = data['course_id_list'].apply(lambda x: len(x.split("--")))
        data.sort_values("total_course",ascending=False,inplace=True)

        # sort the value based on top 10 instructor
        top_10 = data[['display_name','total_course']][:10].sort_values('total_course')
        plot_out = top_10.plot.barh(
            x="display_name",
            y="total_course",
            title="Top 10 Instructors who teach the most courses",
            figsize=(12,7)
        )
        fig = plot_out.get_figure()
        fig.savefig(figure_save_path+'instructor_figure1.png')

        # explain
        explain = "Above are the Top 10 Instructor with the most courses on this webapp."
        return explain