from model.user import User
from lib.helper import user_data_path, read_users, paginate

class Student(User):
    def __init__(self, uid:int=-1, username:str="", password:str="", register_time:str="yyyy-MM-dd_HH:mm:ss.SSS", role="student", email:str="") -> None:
        '''Student constructor'''

        self.uid=uid
        self.username=username
        self.password=self.encrypt_password(password)
        self.register_time=self.date_conversion(register_time)
        self.role=role
        self.email=email

    def __str__(self) -> str:
        student = [
            str(self.uid),
            self.username,
            self.password,
            self.register_time,
            self.role,
            self.email
        ]
        return ";;;".join(student)

    def get_students_by_page(self, page:int) -> tuple:
        '''Get students by page. Retrieve all the student information from user.txt file'''

        # convert page value type into integer
        page = int(page)

        # read user.txt and filter it by student role
        students = read_users("student")
        total_num = len(students)

        # turn the list into pagination and count for total pages
        students = paginate(students,20)
        total_pages = len(students)

        # if page not in total pages return None
        if page <= total_pages:

            # get student list by page
            one_page_student_list = students[page-1]

            # return the student list, total pages, and total student as a tuple
            return one_page_student_list, total_pages, total_num

        else:
            return None, 0, 0

    def get_student_by_id(self, uid:int):
        '''Get student user by user id'''
        
        # read user.txt and look for student by id
        for student in read_users("student"):
            if student['uid'] == uid:
                return student
        
    def delete_student_by_id(self, id_:int):
        
        # read the user.txt
        with open(user_data_path,"r",encoding="utf-8") as file:
            users = file.read().split("\n")

        # rewrite the user.txt
        with open(user_data_path,"w",encoding="utf-8") as file:
            for user in users: # look for user id
                if user.split(";;;")[0] != str(id_): # if true, skip user with the id by being rewritten
                    file.write(user+"\n")