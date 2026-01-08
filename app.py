from flask import Flask
from applications.models import db, doctors, patients, appointment, treatment, availability
import os

app=Flask(__name__)
app.secret_key="P@ssword"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.getcwd()) + '/database/database.sqlite3'
db.init_app(app)
with app.app_context():
    db.create_all()
from applications.controllers import*
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

