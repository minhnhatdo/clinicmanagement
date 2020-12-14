from medical_app import app, admin, db, utils, login
from flask import render_template, redirect, request, jsonify, Response
from werkzeug.http import HTTP_STATUS_CODES
from medical_app.models import *
from flask_login import current_user


