from flask import Flask, send_from_directory, render_template, request, session, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_salt = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    user = db.relationship('User', backref='student')
    graduation_year = db.Column(db.Integer, nullable=False)
    in_school_hours = db.Column(db.Integer, nullable=False)
    out_of_school_hours = db.Column(db.Integer, nullable=False)
    required_hours = db.Column(db.Integer, nullable=False)
    service_records = db.relationship('ServiceRecord', backref='student')

class ServiceRecord(db.Model):
    __tablename__ = 'service_records'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.user_id'), nullable=False)
    dates = db.Column(db.ARRAY(db.String(100)), nullable=False)
    organization_name = db.Column(db.String(1000), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    proof_of_service = db.Column(db.String(1000), nullable=False)
    is_in_school = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(100), nullable=False)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    dates = db.Column(db.ARRAY(db.String(100)), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    organization_name = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    hours_offered = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    is_in_school = db.Column(db.Boolean, nullable=False)



#TODO: add automatic rescraping of faculty list for the new school year

with open("faculty_list.json", "r") as f:
    faculty_list = json.load(f)

current_date = datetime.now()
if 6 <= current_date.month <= 12:
    senior_grad_year = current_date.year + 1
else:
    senior_grad_year = current_date.year

#TODO: add password hashing and salt
def check_user_credentials(email, password):
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return False
    return user.password_hash == password

#decorator to check if user is logged in and has the correct role
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        user = db.session.query(User).filter_by(email=session['user']).first()
        if user.role == 'admin':
            return f(user=user, *args, **kwargs)
        elif user.role == 'student':
            student = db.session.query(Student).filter_by(user_id=user.id).first()
            return f(user=user, student=student, *args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        get_flashed_messages()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if check_user_credentials(email, password):
            session['user'] = email
            user = db.session.query(User).filter_by(email=email).first()
            if user.role == 'student':
                return redirect(url_for('student_portal'))
            elif user.role == 'admin':
                return redirect(url_for('admin_portal'))
            else:
                return redirect('/')
        else:
            flash('Invalid email or password. If you do not have an account, please register.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        get_flashed_messages()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        graduation_year = request.form['graduation_year']
        role = 'student'
        first_name = request.form['student_first_name']
        last_name = request.form['student_last_name']
        #TODO: add password hashing and salt
        user = User(
            email=email, 
            password_hash=password, 
            password_salt=password, 
            role=role,
            first_name=first_name,
            last_name=last_name,
        )
        with app.app_context():
            try:
                db.session.add(user)
                db.session.commit()
                print(f"User {email} registered successfully")
                session['user'] = email
                if role == 'student':
                    student = Student(
                        user_id=user.id,
                        graduation_year=graduation_year,
                        in_school_hours=0,
                        out_of_school_hours=0,
                        service_records=[],
                        required_hours=40.0,
                    )
                    try:
                        db.session.add(student)
                        db.session.commit()
                        print(f"Student {email} registered successfully")
                    except Exception as e:
                        flash("Error registering student. Please try again.", "error")
                        print(f"Error adding student: {e}")
                        db.session.rollback()
                        return render_template('register.html')
                    return redirect(url_for('student_portal'))
                elif role == 'admin':
                    return redirect(url_for('admin_portal'))
            except Exception as e:
                flash("Error registering user. If you already have an account, please login.", "error")
                print(f"Error adding user: {e}")
                db.session.rollback()
                return render_template('register.html')
    return render_template('register.html', senior_grad_year=senior_grad_year)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/student_portal')
@user_required
def student_portal(user, student):
    events = db.session.query(Event).all()
    return render_template('student_portal.html', student=student, events=events, faculty_list=faculty_list)

@app.route('/student_portal/form', methods=['GET', 'POST'])
@user_required
def student_form(user, student):
    in_school = request.args.get('in_school')
    if request.method == 'POST':
        dates = []
        for i in range(int(request.form['num_dates'])):
            dates.append(request.form['service_date_input_' + str(i)])
        if request.form['in_school'] == 'true':
            service_record = ServiceRecord(
                student_id=student.user_id,
                dates=dates,
                organization_name='Dexter Southfield',
                event_name=request.form['event_name'],
                contact_name=request.form['school_contact_name_hidden'],
                contact_email=request.form['school_contact_email'],
                hours=request.form['hours'],
                description=request.form['description'],
                proof_of_service=request.form['proof_of_service'],
                is_in_school=True,
                status='pending'
            )
        elif request.form['in_school'] == 'false':
            service_record = ServiceRecord(
                student_id=student.user_id,
                dates=dates,
                organization_name=request.form['external_organization_name'],
                event_name=request.form['event_name'],
                contact_name=request.form['external_contact_first_name'] + ' ' + request.form['external_contact_last_name'],
                contact_email=request.form['external_contact_email'],
                hours=request.form['hours'],
                description=request.form['description'],
                proof_of_service=request.form['proof_of_service'],
                is_in_school=False,
                status='pending'
            )
        try:
            db.session.add(service_record)
            db.session.commit()
            print(f"Service record added successfully")
        except Exception as e:
            flash("Error adding service record. Please try again.", "error")
            print(f"Error adding service record: {e}")
            db.session.rollback()
            return render_template('student_form.html', senior_grad_year=senior_grad_year, faculty_list=faculty_list, in_school=in_school, student=student)
        return redirect(url_for('student_portal'))
    return render_template('student_form.html', senior_grad_year=senior_grad_year, faculty_list=faculty_list, in_school=in_school, student=student)

@app.route('/student_portal/events')
@user_required
def student_events(user, student):
    events = db.session.query(Event).all()
    if request.method == 'POST':
        dates = []
        for i in range(int(request.form['num_dates'])):
            dates.append(request.form['service_date_input_' + str(i)])
        if request.form['in_school'] == 'true':
            event = Event(
                student_id=student.user_id,
                dates=dates,
                organization_name='Dexter Southfield',
                event_name=request.form['event_name'],
                contact_name=request.form['school_contact_name_hidden'],
                contact_email=request.form['school_contact_email'],
                hours_offered=request.form['hours'],
                description=request.form['description'],
                is_in_school=True,
            )
        elif request.form['in_school'] == 'false':
            event = Event(
                student_id=student.user_id,
                dates=dates,
                organization_name=request.form['external_organization_name'],
                event_name=request.form['event_name'],
                contact_name=request.form['external_contact_first_name'] + ' ' + request.form['external_contact_last_name'],
                contact_email=request.form['external_contact_email'],
                hours_offered=request.form['hours'],
                description=request.form['description'],
                is_in_school=False,
            )
        try:
            db.session.add(event)
            db.session.commit()
            print(f"Event added successfully")
        except Exception as e:
            flash("Error adding event. Please try again.", "error")
            print(f"Error adding event: {e}")
            db.session.rollback()
            return render_template('student_events.html', events=events, faculty_list=faculty_list)
    return render_template('student_events.html', events=events, faculty_list=faculty_list)

@app.route('/admin_portal')
@user_required
def admin_portal(user):
    return render_template('admin_portal.html')

@app.route('/admin_portal/students')
@user_required
def admin_students(user):
    students = db.session.query(Student).all()
    return render_template('admin_student_db.html', students=students)

@app.route('/admin_portal/events')
@user_required
def admin_events(user):
    events = db.session.query(Event).all()
    return render_template('admin_events.html', events=events, faculty_list=faculty_list)


if __name__ == '__main__':
    app.run(debug=True)
