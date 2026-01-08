from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()
class doctors(db.Model):
    __tablename__='doctors'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    username=db.Column(db.String, unique=True, nullable=False)
    password=db.Column(db.String, nullable=False)
    doctor_name=db.Column(db.String, nullable=False)
    department=db.Column(db.String, nullable=False)
    experience=db.Column(db.Integer, nullable=False)

class patients(db.Model):
    __tablename__='patients'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    username=db.Column(db.String, unique=True, nullable=False)
    password=db.Column(db.String, nullable=False)
    patient_name=db.Column(db.String, nullable=False)
    doctor_name=db.Column(db.String, nullable=False)
    contact_number=db.Column(db.String, nullable=False)
    doc_id=db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)

class availability(db.Model):
    __tablename__='availability'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    doc_id=db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    Date=db.Column(db.Date, nullable=False)
    Morning=db.Column(db.Boolean, default=True, nullable=False)
    Evening=db.Column(db.Boolean, default=True, nullable=False)

class appointment(db.Model):
    __tablename__='appointment'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    patient_id=db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doc_id=db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    Date=db.Column(db.Date, nullable=False)
    Time=db.Column(db.String, nullable=False)
    Status=db.Column(db.String, nullable=False)

class treatment(db.Model):
    __tablename__='treatment'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    patient_id=db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id=db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    tests=db.Column(db.String, nullable=False)
    Diagnosis=db.Column(db.String, nullable=False)
    Prescription=db.Column(db.String, nullable=False)
    Medicines=db.Column(db.String, nullable=False)



    





    