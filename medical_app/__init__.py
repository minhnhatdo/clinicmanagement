from flask import Flask, redirect, Blueprint, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456789@localhost/clinic_management?charset=utf8"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['ROOT_PROJECT_PATH'] = app.root_path
app.secret_key = 'ahiahiahiah'


db = SQLAlchemy(app=app)


class UserModelView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.user_role == 'admin'

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for("index"))


admin = Admin(app=app, name="Quản lý phòng mạch", template_mode="bootstrap4", index_view=UserModelView())


login = LoginManager(app=app)



