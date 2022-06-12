from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy
import json
import os
import re

from lib.helper import course_data_path, course_json_files_path, read_courses, paginate, read_users, figure_save_path

class Course:

    def __init__(
            self,
            category_title:str="",
            subcategory_id:int=-1,
            subcategory_title:str="",
            subcategory_description:str="",
            subcategory_url:str="",
            course_id:int=-1,
            course_title:str="",
            course_url:str="",
            num_of_subscribers:int=-1,
            avg_rating:float=0.0,
            num_of_reviews:int=0
        ):
        '''Course constructor'''
        
        self.category_title=category_title
        self.subcategory_id=str(subcategory_id)
        self.subcategory_title=subcategory_title
        self.subcategory_description=subcategory_description
        self.subcategory_url=subcategory_url
        self.course_id=str(course_id)
        self.course_title=course_title
        self.course_url=course_url
        self.num_of_subscribers=str(num_of_subscribers)
        self.avg_rating=str(avg_rating)
        self.num_of_reviews=str(num_of_reviews)

    def __str__(self) -> str:
        course = [
            self.category_title,
            self.subcategory_id,
            self.subcategory_title,
            self.subcategory_url,
            self.subcategory_description,
            self.course_id,
            self.course_title,
            self.course_url,
            self.num_of_subscribers,
            self.avg_rating,
            self.num_of_reviews
        ]
        return ";;;".join(course)

    def get_courses(self):
        '''Get course from the source data'''

        def write_courses(path:str) -> None:

            # read the json file
            data = json.load(open(path,encoding="utf-8"))
            data = data['unitinfo']

            # find the course category
            category = re.search("(?<=category_)(.*?)(?=\\\)|(?<=category_)(.*?)(?=/)",path).group()
            sub_categories = data['source_objects']
            for sub in sub_categories:
                if sub['type'] == "sub-category":
                    
                    # find course sub-category
                    entry = dict(
                        subcategory_id=sub['id'],
                        subcategory_title=sub['title'],
                        subcategory_description=sub['description'],
                        subcategory_url=sub['url']
                    )

            # find the courses
            with open(course_data_path,"a",encoding="utf-8") as file:
                items = data['items']
                for item in items:
                    if item['_class'] == "course":
                        entry.update(dict(
                            course_id=item['id'],
                            course_title=item['title'],
                            course_url=item['url'],
                            course_num_of_subscribers=item['num_subscribers'],
                            course_avg_rating=item['avg_rating'],
                            course_num_of_reviews=item['num_reviews']
                        ))
                        strings = [
                            category,
                            entry['subcategory_id'],
                            entry['subcategory_title'],
                            entry['subcategory_description'],
                            entry['subcategory_url'],
                            entry['course_id'],
                            entry['course_title'],
                            entry['course_url'],
                            entry['course_num_of_subscribers'],
                            entry['course_avg_rating'],
                            entry['course_num_of_reviews']
                        ]
                        file.write(";;;".join([str(a) for a in strings])+"\n")

        # clear the course.txt
        self.clear_course_data()
        
        # read all json files from source_course_files folder
        for root,_,files in os.walk(course_json_files_path):
            for file in files:
                if file.endswith("json"):
                    file_path = os.path.join(root,file)
                    write_courses(file_path)

    def clear_course_data(self) -> None:
        '''Clear the course.txt'''

        # write an empty string
        with open(course_data_path,"w",encoding="utf-8") as file:
            file.write("")

    def generate_page_num_list(self, page:int or str, total_pages: int or str) -> list:
        '''Keep the page number list always in 9 column/pages with format [1,2,3,4,5,6,7,8,9]'''
        
        # convert input into integer value
        page, total_pages = int(page), int(total_pages)

        # calculate the postition
        start,end = (1,9)
        if page > 5 and total_pages != 0:
            start,end = (page-4,page+4)
        return [i for i in range(start,end+1)]

    def get_courses_by_page(self, page:int or str) -> tuple:
        '''Get courses by page number.'''

        # convert page input into integer
        page = int(page)

        # get courses as a list and count for total courses
        courses = read_courses()
        total_num = len(courses)

        # turn the courses list into pagination and count for total pages
        courses = paginate(courses,20)
        total_pages = len(courses)

        # if page not in total pages, return None
        if page <= total_pages:

            # get courses by page
            one_page_course_list = courses[page-1]

            # return the course list, total pages, and total courses as a tuple
            return one_page_course_list, total_pages, total_num

        else:
            return None, 0, 0

    def delete_course_by_id(self, temp_course_id:int) -> bool:
        
        # define the dictionary keys
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
        
        # read course.txt and look for course id
        found = False
        courses = read_courses()
        self.clear_course_data()

        # remove the course from the list if found
        for course in courses:
            if course['course_id'] == temp_course_id: 
                found = True
            else:
                # reappend the list to the course.txt
                with open(course_data_path,"a",encoding="utf-8") as file:
                    file.write(";;;".join([str(course[k]) for k in keys])+"\n")

        if found:
            return True
        else:
            return False

    def get_course_by_course_id(self, temp_course_id:int) -> tuple:

        # read course.txt and look for course id
        for course in read_courses():
            if course['course_id'] == temp_course_id:
                return course,None

    def get_course_by_instructor_id(self, instructor_id:int):
        
        # read user.txt and filter it by instructor id
        for instructor in read_users("instructor"):
            if instructor['uid'] == instructor_id:
                course_list = instructor['course_id_list'].split("--")
                course_list = list(map(int,course_list))
                course_list = list(map(self.get_course_by_course_id,course_list))
                course_list = [item for item,_ in course_list]
                course_list = course_list if len(course_list) < 20 else course_list[:20]
                return course_list, len(course_list)

    def generate_course_figure1(self):
        
        # read and convert courses data into DataFrame format
        courses = DataFrame(read_courses())
        subcribers = courses[['subcategory_title','num_of_subscribers']].groupby('subcategory_title').sum()
        subcribers = subcribers.sort_values('num_of_subscribers',ascending=False)
        subcribers = subcribers.reset_index()
        subcribers = subcribers[:10].sort_values('num_of_subscribers')

        # plot the data
        ax = subcribers.plot.barh(
            x="subcategory_title",
            y="num_of_subscribers",
            color="orange",
            legend=False,
            figsize=(15,9),
            fontsize=12
        )
        plt.title("Top 10 course subcategories with most subscribers")
        plt.xlabel("Number of Subscribers")
        plt.ylabel("Course Subcategory")
        xticks = {x:f"{round(x/1e6)}M" for x in plt.xticks()[0]}
        plt.xticks(
            list(xticks.keys()),
            list(xticks.values())
        )

        offset = 1e5
        for b in ax.patches:
            box = b.get_bbox()
            x = box.x1
            y = box.y0 + (box.y1-box.y0)/2
            ax.annotate(
                f"{int(x):,d}",
                (x+offset,y)
            )
        plt.savefig(figure_save_path+"course_figure1.png")
        return "explanation1"

    def generate_course_figure2(self):

        # local function
        def rename(text):
            words = text.split(" ")
            if len(words) > 3:
                text = " ".join(words[:3]) + "..."
            return text

        # read and convert courses data into DataFrame format
        courses = DataFrame(read_courses())
        reviews = courses[courses['num_of_reviews'] >= 5e4]
        reviews = reviews.sort_values('avg_rating')
        reviews = reviews.iloc[:10,[6,9]].sort_values('avg_rating',ascending=False)
        reviews['course_title'] = reviews['course_title'].apply(lambda x: rename(x))
        reviews['avg_rating'] = round(reviews['avg_rating'],2)

        # plot the data
        ax = reviews.plot(
            kind="barh",
            x="course_title",
            y="avg_rating",
            legend=False,
            fontsize=12,
            figsize=(15,9)
        )
        plt.xlim(right=5)
        plt.title("Top 10 course average ratings with more than 50K Reviews")
        plt.xlabel('Average Rating')
        plt.ylabel('Course Title')

        offset = 0.025
        for b in ax.patches:
            box = b.get_bbox()
            x = box.x1
            y = box.y0 + (box.y1-box.y0)/2
            ax.annotate(
                str(round(x,2)),
                (x+offset,y)
            )
        plt.savefig(figure_save_path+"course_figure2.png")
        return "explanation2"

    def generate_course_figure3(self):

        # read and convert courses data into DataFrame format
        courses = DataFrame(read_courses())
        data3 = courses[courses['num_of_subscribers'] >= 1e4]
        data3 = data3[data3['num_of_subscribers'] <= 1e5]
        
        # plot the data
        data3.plot.scatter(
            'num_of_subscribers',
            'avg_rating',
            color='orange',
            ylabel="Average Rating",
            xlabel="Number of Subscribers",
            figsize=(15,9),
            fontsize=13
        )
        plt.title("10K-100K Course Subscribers Average Rating Distribution")
        plt.ylim(0.0,5.5)
        plt.xlim(1e4,1e5)
        plt.grid()
        plt.savefig(figure_save_path+"course_figure3.png")
        return "explanation3"

    def generate_course_figure4(self):

        # read and convert courses data into DataFrame format
        courses = DataFrame(read_courses())
        category = courses[['category_title','course_id']].groupby('category_title').count()
        category = category.sort_values('course_id')
        values = [i[0] for i in category.values.tolist()]
        explode = [0.2 if i == 2 else 0.0 for i in range(len(values))]
        total = category.values.sum()

        # plot the values
        category.plot.pie(
            y="course_id",
            labels=None,
            explode=explode,
            autopct=lambda x: f"{int(total*x):,d} ({x:.2f} %)",
            frame=True,
            figsize=(15,11),
            fontsize=12
        )
        plt.title("Categories number of course pie chart")
        plt.xlabel("")
        plt.ylabel("")
        plt.xticks([])
        plt.yticks([])
        plt.savefig(figure_save_path+"course_figure4.png")
        return "explanation4"

    def generate_course_figure5(self):

        # read and convert courses data into DataFrame format
        courses = DataFrame(read_courses())
        courses['has_reviews'] = courses['num_of_reviews'].apply(lambda x: True if x > 0 else False)
        has_reviews = courses['has_reviews'].value_counts() # the output type is Pandas Series
        has_reviews.index = ['Has Reviews','No Reviews']

        # plot the data
        plt.figure(figsize=(15,9))
        ax = plt.bar(
            ['Course that Has Reviews','Course with No Reviews'],
            has_reviews,
            width=0.5
        )
        plt.title("Number of Courses that has Reviews and Not")
        plt.ylabel("Number of Reviews")
        plt.ylim(top=25000)
        offset = 200
        for p in ax.patches:
            box = p.get_bbox()
            y = box.y1
            x = box.x0 + (box.x1-box.x0)/2
            plt.annotate(
                f"{round(y):,d}",
                (x,y+offset),
                ha="center",
                fontsize=14
            )
        plt.savefig(figure_save_path+"course_figure5.png")
        return "explanation5"

    def generate_course_figure6(self):

        # local function
        def rename(text):
            words = text.split(" ")
            if len(words) > 3:
                text = " ".join(words[:3]) + "..."
            return text

        # read and convert courses data into DataFrame format
        courses = DataFrame(read_courses())
        subcategories = courses[['subcategory_title','course_id']]
        subcategories = subcategories.groupby('subcategory_title').count()
        subcategories = subcategories.sort_values('course_id')
        subcategories = subcategories.iloc[0:10].reset_index()
        subcategories['subcategory_title'] = subcategories['subcategory_title'].apply(lambda x: rename(x))

        # plot fig
        ax = subcategories.plot.barh(
            x="subcategory_title",
            y="course_id",
            legend=False,
            figsize=(15,8)
        )
        plt.title("Top 10 subcategories with least courses")
        plt.xlabel('Number of Courses')
        plt.ylabel('Subcategory Title')
        offset = 2
        for p in ax.patches:
            box = p.get_bbox()
            x = box.x1
            y = box.y0 + (box.y1-box.y0)/2
            ax.annotate(
                str(int(x)),
                (x+offset,y)
            )
        plt.savefig(figure_save_path+"course_figure6.png")
        return "explanation6"