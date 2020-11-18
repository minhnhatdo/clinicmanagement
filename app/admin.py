from app import admin, db
from flask import redirect
from app.models import User, Patient, Bill, Medicine, MedicalForm, Configuration, Prescription
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(ModelView(Patient, db.session))
admin.add_view(ModelView(Bill, db.session))
admin.add_view(ModelView(Medicine, db.session))
admin.add_view((ModelView(MedicalForm, db.session)))
admin.add_view(ModelView(Prescription, db.session))
admin.add_view(ModelView(Configuration, db.session))
admin.add_view(LogoutView(name="Đăng xuất"))