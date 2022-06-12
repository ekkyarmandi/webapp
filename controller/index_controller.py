from flask import render_template, Blueprint

from model.user import User
from model.user_admin import Admin

from lib.helper import datetime

index_page = Blueprint("index_page", __name__)
model_user = User()

@index_page.route("/")
def index():

    # check the class variable User.current_login_user
    context = {}
    if User.current_login_user:
        user = User.current_login_user
        context['current_user_role'] = user.role

    # manually register an admin account when open index page
    else:
        if not model_user.check_username_exist("ekkyarmandi"):
            admin = Admin(
                username="admin",
                password="admin",
                register_time=datetime.now().timestamp()
            )
            admin.register_admin()
    return render_template("01index.html", **context)