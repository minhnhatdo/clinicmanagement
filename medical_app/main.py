from medical_app import app, admin, db, utils, login, decorator
from flask import render_template, redirect, request, make_response, jsonify, url_for, session
from medical_app.models import User, UserRole
from flask_login import login_user, current_user
from medical_app.admin import *
from werkzeug.http import HTTP_STATUS_CODES
from sqlalchemy import extract, func
import hashlib, os
import datetime, json


@app.route("/")
@decorator.login_required
def index():
    return redirect(url_for('daily_patients'))


@app.route("/dailypatients")
@decorator.login_required
def daily_patients():
    return render_template("daily_patients.html")


@app.route("/medicalform")
@decorator.login_required
def medical_form():
    config = utils.read_data()
    return render_template("medical_form.html", config=config)


@app.route("/bill/<int:medical_form_id>")
@decorator.login_required
def bill(medical_form_id):
    config = utils.read_data()
    medical_form = MedicalForm.query.get_or_404(medical_form_id)
    prescriptions = Prescription.query.filter_by(medicalform_id=medical_form_id).all()
    session['exam_money'] = config['exam_cost']
    session['medicalform_id'] = medical_form_id
    session['creator_id'] = current_user.id
    session['patient_name'] = medical_form.patient.name
    session['drug_money'] = 0
    session['date'] = medical_form.date
    for item in prescriptions:
        session['drug_money'] += item.medicine.price * item.amount
    return render_template("bill.html")


@app.route("/patientlist")
@decorator.login_required
def patient_list():
    return render_template("patient_list.html")


@app.route("/salesreport")
@decorator.login_required
def sales_report():
    return render_template("sales_report.html")


@app.route("/drugsreport")
@decorator.login_required
def drugs_report():
    return render_template("drugs_report.html")


@app.route("/config", methods=['POST', 'GET'])
@decorator.login_required
@decorator.admin_required
def config():
    config = utils.read_data()
    if request.method == 'POST':
        config['max_patients_per_day'] = request.form.get('max_patients_per_day')
        config['exam_cost'] = request.form.get('exam_cost')
        config['drug_usage'] = request.form.get('drug_usage')
        config['drug_unit'] = request.form.get('drug_unit')
        config['desease'] = request.form.get('desease')
        with open('./medical_app/config.json','w') as f:
            json.dump(config, f)
        return redirect(url_for("index"))
    return render_template("config.html", config=config)


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
            return redirect(url_for('index'))

    return render_template('auth/login.html')


@app.route("/logout")
def log_out():
    logout_user()
    return redirect(url_for("index"))


@login.user_loader
def get_user(user_id):
    return User.query.get(user_id)


# if __name__ == "__main__":
#     app.run(port=50000, debug=True)


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = make_response(jsonify(payload), status_code)
    return response


def bad_request(message):
    return error_response(400, message)


@app.route("/api/addPatient", methods=["POST"])
def add_patient():
    now = datetime.date.today()
    patient_in_day = len(Patient.query.filter_by(created_at=now).all())
    if patient_in_day  > 40:
        return make_response(jsonify({'message':'Quá Số Lượng Bệnh Nhân Tối Đa'}))
    data = request.get_json()
    if 'name' not in data or 'yob' not in data: 
        return bad_request('Phải có Tên và Ngày sinh')
    if Patient.query.filter_by(name=data['name']).first():
        return bad_request('Đã có Khách Hàng trong hệ thống')
    data['creator_id'] = current_user.id
    patient = Patient()
    patient.from_dict(data)
    db.session.add(patient)
    db.session.commit()
    response = make_response(jsonify(patient.to_dict()), 201) 
    return response


@app.route("/api/getPatients/<date>", methods=["GET", "POST"])
def get_patients(date):
    date_split = date.split("-")
    compare_date = datetime.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))
    patients = Patient.query.filter_by(created_at=compare_date).all()
    return jsonify(data = [item.to_dict() for item in patients])

@app.route("/api/getPatientsName")
def get_patients_name():
    patients = Patient.query.all()
    return jsonify([str(item) for item in patients])


@app.route("/api/getMedicines")
def get_medicines():
    medicines = Medicine.query.all()
    return make_response(jsonify([item.to_dict() for item in medicines])) 


@app.route('/api/createMedicalForm', methods=['POST'])
def create_medical_form():
    data = request.get_json()
    patient = Patient.query.filter_by(name=data['patient_name']).first()
    data['patient_id'] = patient.id
    data['creator_id'] = current_user.id
    medical_form = MedicalForm()
    medical_form.from_dict(data)
    db.session.add(medical_form)
    db.session.flush()
    for item in data['prescription']:
        item['medicalform_id'] = medical_form.id
        prescription = Prescription()
        prescription.from_dict(item)
        db.session.add(prescription)
        db.session.commit()
    return make_response(jsonify({'url_redirect':'bill/' + str(medical_form.id)}), 201)


@app.route('/bill/api/createBill')
def create_bill():
    bill = Bill()
    bill.from_dict(session)
    db.session.add(bill)
    db.session.commit()
    return make_response(jsonify({'message':'Thành công','url_redirect':'/dailypatients'}), 201)


@app.route('/api/getMedicalforms', methods=['POST', 'GET'])
def get_medical_forms():
    medical_form = MedicalForm.query.all()
    return jsonify(data = [item.to_dict() for item in medical_form])


@app.route('/api/getSalesReport/<int:month>/<int:year>')
def get_sales_report(month, year):
    salesTotal = 0;
    bills = Bill.query.filter(extract('year', Bill.date)==year).filter(extract('month', Bill.date)==month).all()
    for item in bills:
        salesTotal += item.drug_money + item.exam_money
    data = [item.to_dict() for item in bills]
    for item in data:
        item['percent'] = (item['sales'] / salesTotal) * 100
    return make_response(jsonify(data = data))


@app.route('/api/getDrugReport/<int:month>/<int:year>')
def get_drug_report(month, year):
    bills = Bill.query.filter(extract('year', Bill.date)==year).filter(extract('month', Bill.date)==month).all()
    medical_form_ids = []
    for item in bills:
        medical_form_ids.append(item.medicalform_id)
    drugs = Prescription.query.filter(Prescription.medicalform_id.in_(medical_form_ids)).with_entities(Prescription.medicine_id, func.sum(Prescription.amount), func.count(Prescription.amount)).group_by(Prescription.medicine_id).all()
    drugs_report_data = []
    for item in drugs:
        temp = {}
        medicine = Medicine.query.get(item[0])
        temp['name'] = medicine.name
        temp['unit'] = medicine.unit
        temp['amount'] = int(item[1])
        temp['usage_time'] = item[2]
        drugs_report_data.append(temp)
    return make_response(jsonify(data=drugs_report_data), 201)