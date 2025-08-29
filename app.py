from flask import Flask, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/community-service-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/form')
def form():
    # get the senior's graduation year to fill out the form options automatically
    current_date = datetime.now()
    if 6 <= current_date.month <= 12:
        senior_grad_year = current_date.year + 1
    else:
        senior_grad_year = current_date.year
    return render_template('form.html', senior_grad_year=senior_grad_year)

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
