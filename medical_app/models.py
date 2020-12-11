from sqlalchemy import Boolean, Enum, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from medical_app import db
from flask_login import UserMixin
from enum import Enum as UserEnum


class Patient(db.Model):
    __tablename__ = "patient"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(String(100))
    dob = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    gender = Column(String(6))
    medicalForm = relationship("MedicalForm", backref='patient', lazy=True)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.name


class Prescription(db.Model):
    __tablename__ = "prescription"
    medicine_id = Column(Integer, ForeignKey('medicine.id'), primary_key=True)
    medicalform_id = Column(Integer, ForeignKey('medical_form.id'), primary_key=True)
    amount = Column(Integer, nullable=False)
    usage = Column(String(200), nullable=False)

    def __str__(self):
        return "Đơn thuốc cho Phiếu khám bệnh số: " + str(self.medicalform_id)


class MedicalForm(db.Model):
    __tablename__ = "medical_form"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, server_default=func.now())
    symptom = Column(String(200), nullable=False)
    disease_prediction = Column(String(100), nullable=False)
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)
    prescriptions = relationship("Prescription", backref='medical_form', lazy=True)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return "Phiếu khám bệnh số: " + str(self.id)


class Medicine(db.Model):
    __tablename__ = "medicine"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    date_of_manufacture = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    unit = Column(String(10), nullable=False)
    number_of_product = Column(Integer, nullable=False)
    prescriptions = relationship("Prescription", backref="medicine", lazy=True)
    employee_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.name


class Bill(db.Model):
    __tablename__ = "bill"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, server_default=func.now())
    drug_money = Column(Float, nullable=False)
    exam_money = Column(Float, nullable=False)
    medicalform_id = Column(Integer, ForeignKey('medical_form.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return "Mã hoá đơn số: " + str(self.id)


class Configuration(db.Model):
    __tablename__ = "configuration"
    id = Column(Integer, primary_key=True, default=0)
    max_patient_per_day = Column(Integer)
    desease_type = Column(JSON)
    drug_unit = Column(JSON)
    drug_usage = Column(JSON)
    exam_money = Column(Float)

    def __str__(self):
        return self.__tablename__


class UserRole(UserEnum):
    USER = 1
    ADMIN = 2


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50))
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100))
    is_active = Column(Boolean, default=True)
    joined_date = Column(DateTime, server_default=func.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    patients = relationship("Patient", backref="creator")
    medicalForms = relationship("MedicalForm", backref="creator")
    bill = relationship("Bill", backref="creator")
    medicines = relationship("Medicine", backref="employee")


if __name__ == "__main__":
    db.create_all()




