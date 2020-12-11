from medical_app import app, admin, db, utils, login
from flask import render_template, redirect, request
from medical_app.models import User, UserRole
from flask_login import login_user, current_user
from medical_app.admin import *
import hashlib, os


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dailypatients")
def daily_patients():
    return render_template("daily_patients.html")


@app.route("/medicalform")
def medical_form():
    return render_template("medical_form.html")


@app.route("/bill")
def bill():
    return render_template("bill.html")


@app.route("/patientlist")
def patient_list():
    return render_template("patient_list.html")


@app.route("/salesreport")
def sales_report():
    return render_template("sales_report.html")


@app.route("/drugsreport")
def drugs_report():
    return render_template("drugs_report.html")


@app.route('/register', methods=['get', 'post'])
def register():
    err_msg = ''
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        user_role = request.form.get('user_role')
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if password == confirm_password:
            avatar = request.files["avatar"]
            avatar_path = 'images/upload/%s' % avatar.filename
            avatar.save(os.path.join(app.config['ROOT_PROJECT_PATH'],
                                     'static/', avatar_path))

            if utils.add_user(email=email, username=username,
                              password=password, avatar=avatar_path):
                return redirect('/admin')
        else:
            err_msg = "Mật khẩu KHÔNG khớp!"

    return render_template("auth/register.html", err_msg=err_msg, UserRole=UserRole)


@app.route("/login", methods=['post', 'get'])
def login_usr():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '')
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        user = User.query.filter(username == username,
                                 password == password).first()

        if user:
            login_user(user=user)
            return redirect('/admin')

    return render_template('auth/login.html')


@login.user_loader
def get_user(user_id):
    return User.query.get(user_id)


# if __name__ == "__main__":
#     app.run(port=50000, debug=True)
