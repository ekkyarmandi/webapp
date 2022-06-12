from model.user import User

class Admin(User):
    def __init__(self, uid:int=-1, username:str="", password:str="", register_time:str="yyyy-MM-dd_HH:mm:ss.SSS", role:str="admin") -> None:
        '''Admin constructor'''

        self.uid=uid
        self.username=username
        self.password=self.encrypt_password(password)
        self.register_time=self.date_conversion(register_time)
        self.role=role

    def register_admin(self) -> None:
        '''Register new admin. Inherit admin registration from User method.'''

        self.register_user(
            username=self.username,
            password=self.password,
            register_time=self.register_time,
            role=self.role
        )

    def __str__(self) -> str:
        user = [
            str(self.uid),
            self.username,
            self.password,
            self.register_time,
            self.role
        ]
        return ";;;".join(user)