from flask import Flask, send_from_directory, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/community-service-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    in_school_hours = db.Column(db.Integer, nullable=False)
    out_of_school_hours = db.Column(db.Integer, nullable=False)
    service_records = db.relationship('ServiceRecord', backref='student')

class ServiceRecord(db.Model):
    __tablename__ = 'service_records'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    dates = db.Column(db.Date, nullable=False)
    organization_name = db.Column(db.String(1000), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    proof_of_service = db.Column(db.String(1000), nullable=False)

#TODO: add automatic rescraping of faculty list for the new school year

with open("faculty_list.json", "r") as f:
    faculty_list = json.load(f)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/form', methods=['GET', 'POST'])
def form():
    # get the senior's graduation year to fill out the form options automatically
    in_school = request.args.get('in_school')
    current_date = datetime.now()
    if 6 <= current_date.month <= 12:
        senior_grad_year = current_date.year + 1
    else:
        senior_grad_year = current_date.year
    return render_template('form.html', senior_grad_year=senior_grad_year, faculty_list=faculty_list, in_school=in_school)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student_portal')
def student_portal():
    return render_template('student_portal.html')

@app.route('/admin_portal')
def admin_portal():
    return render_template('admin_portal.html')


if __name__ == '__main__':
    app.run(debug=True)
