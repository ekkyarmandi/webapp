import random
import string
import re

from lib.helper import datetime, user_data_path


class User:
    current_login_user = None
    def __init__(self, uid:int=-1, username:str="", password:str="", register_time:str="yyyy-MM-dd_HH:mm:ss.SSS", role:str="") -> None:
        '''User constructor'''

        self.uid=uid
        self.username=username
        self.password=password
        self.register_time=register_time
        self.role=role

    def __str__(self) -> str:
        user_info = [
            self.uid,
            self.username,
            self.password,
            self.register_time,
            self.role
        ]
        return ";;;".join([str(info) for info in user_info])

    def validate_username(self, username:str) -> bool:
        '''Validate user username input. Username should contains letter and underscore only.'''

        f = string.punctuation.replace("_","")
        if any([c in f for c in username]):
            return False
        else:
            return True

    def validate_password(self, password:str) -> bool:
        '''Validate user password input. Password must contain 8 character at least.'''

        if len(password) >= 8:
            return True
        else:
            return False

    def validate_email(self, email:str) -> bool:
        '''Validate user email input. Email must contains "@", end with ".com", and has more than 8 characters.'''

        email_regex = re.search("[A-Za-z0-9_.]+@\w+\.com$",email)
        if email_regex and len(email) >= 8:
            return True
        else:
            return False

    def clear_user_data(self) -> None:
        '''Clear all user data from user.txt'''

        # read and clear entries from user.txt
        with open(user_data_path,"w",encoding="utf-8") as file:
            file.write("")

    def authenticate_user(self, username:str, password:str) -> bool:
        '''Authenticate user by match username and password in user.txt list'''

        def get_username_passwords(string):
            username = string.split(";;;")[1]
            password = string.split(";;;")[2]
            password = re.findall("[A-Za-z0-9]+",password)
            return username+";;;"+"".join(password)

        # read user.txt
        with open(user_data_path,encoding="utf-8") as file:
            users = file.read().split("\n")
            users = [get_username_passwords(line) for line in users if line.strip() != ""]

        # check username and password in the entries
        if username+";;;"+password in users:
            return True
        else:
            return False

    def check_username_exist(self, username:str) -> bool:
        '''Check username existence in user.txt list'''
        
        # read user.txt
        with open(user_data_path,encoding="utf-8") as file:
            users = []
            for line in file.read().split("\n"):
                line = line.split(";;;")
                if len(line) > 1:
                    users.append(line[1])

        # check username in entries
        if username in users:
            return True
        else:
            return False

    def generate_unique_user_id(self) -> str:
        '''Generate 6 digit unique for user id'''

        def random_generate() -> str:
            return "".join([str(random.randint(0,9)) for _ in range(6)])

        # read user.txt
        with open(user_data_path,encoding="utf-8") as file:
            users = file.read().split()
            ids = [u.split(";;;")[0] for u in users]
            
        # generate unique id
        new_id = random_generate()
        while new_id in ids:
            new_id = random_generate()
        return new_id

    def encrypt_password(self, password:str, sign="*", rep=1) -> str:
        '''Encrypt a password'''

        letters = re.findall("[A-Za-z0-9]{"+str(rep)+"}",password)
        if len(letters) < len(password):
            remain = password.replace("".join(letters),"")
            if len(remain) > 0:
                letters.append(remain)
        if len(letters) > 0:
            encrypted = (sign*2) + (sign*4).join(letters) + (sign*2)
            return encrypted
        else:
            return password

    def register_user(self, username:str="", password:str="", email:str="", register_time:float="YYYY-MM-dd_HH:mm:ss.SSS", role:str="") -> None:
        '''Register new user'''

        user = dict(
            uid=self.generate_unique_user_id(),
            username=username,
            password=password,
            register_time=self.date_conversion(register_time),
            role=role,
            email=email
        )
        if role=="admin":
            user.pop("email")
        new_user = ";;;".join(user.values())
        with open(user_data_path,"a",encoding="utf-8") as file:
            file.write(new_user+"\n")

    def date_conversion(self, register_time: float) -> str:
        ''' Convert unix epoch timestamp into YYYY-MM-dd_HH:mm:ss.SSS format '''

        if type(register_time) == float:

            # convert the timestamp using datetime string format
            register_time = register_time/1000 if (register_time/1e12) > 1 else register_time
            register_time = datetime.fromtimestamp(round(register_time,3))
            return register_time.strftime("%Y-%m-%d_%T") + register_time.strftime(".%f")[:4]

        else:
            return register_time