from app import app, db
from applications.models import *
from flask import render_template
from flask import redirect
from flask import session
from flask import request
from flask import flash
from flask import url_for
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import date, timedelta

tables=['patients']
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method=='GET':
        return render_template('admin_login.html')
    elif request.method=='POST':
        password=request.form.get('password')
        if password=='P@ssword':
            return redirect('/admin/dashboard')
        else:
            flash('Invalid credentials','error')
            return redirect('/admin_login')

@app.route("/patient_login", methods=["GET","POST"])
def patient_login():
    if request.method=='GET':
        return render_template('patient_login.html')
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        #check for empty details
        if not username or not password:
            flash('username and password are required','error')
            return render_template('patient_login.html')
        
        user=patients.query.filter_by(username=username).first()
        #check for valid username and password
        if user and check_password_hash(user.password, password):
            session['username']=user.username
            flash('Login Succesful!', 'success')
            return redirect(f"/patient/dashboard/{user.patient_name}")
        else:
            flash('Invalid credentials','error')
            return render_template('patient_login.html')
    
@app.route("/doctor_login", methods=["GET","POST"])
def doctor_login():
    if request.method=='GET':
        return render_template('doctor_login.html')
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        #check for empty details
        if not username or not password:
            flash('username and password are required','error')
            return render_template('doctor_login.html')
        
        user=doctors.query.filter_by(username=username).first()
        #check for valid username and password
        if user and check_password_hash(user.password, password):
            session['username']=user.username
            flash('Login Succesful!', 'success')
            return redirect(f"/doctor/dashboard/{user.doctor_name}")
        else:
            flash('Invalid credentials','error')
            return render_template('doctor_login.html')


@app.route("/patient_register", methods=["GET","POST"])
def patient_register():
    if request.method=='GET':
        return render_template('patient_register.html')
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        patient_name=request.form.get('full_name')
        doctor_name=request.form.get('doctor_name')
        contact_number=request.form.get('contact_number')
        #check if all details are entered
        if not all([username,password,confirm_password,patient_name,doctor_name,contact_number]):
            flash('All fields are required','error')
            return render_template('patient_register.html')
        #check if password matches confirm password
        if password!=confirm_password:
            flash('Passwords do not match','error')
            return render_template('patient_register.html')
        if len(password)<6:
            flash('Password should be atleast 6 character long','error')
            return render_template('patient_register.html')
        if len(contact_number)<10 or len(contact_number)>10:
            flash('Invalid contact number','error')
            return render_template('patient_register.html')

        existing_patient=patients.query.filter_by(username=username).first()
        if existing_patient:
            flash('Username already exists', 'error')
            return render_template('patient_register.html')
        try:
            hashed_password=generate_password_hash(password)
            doc=doctors.query.filter_by(doctor_name=doctor_name).first()
            new_patient=patients(
                username=username,
                password=hashed_password,
                patient_name=patient_name,
                doctor_name=doctor_name,
                contact_number=contact_number,
                doc_id=doc.id
                )
            db.session.add(new_patient)
            db.session.commit()
            flash('Registration Succesful!, Please Login!','success')
            return redirect('/patient_login')
        except Exception as e:
            db.session.rollback()
            flash('Registration failed, Please Try again!', 'error')
            return render_template('patient_register.html')

@app.route("/admin/dashboard",methods=["GET"])
def admin_dashboard():
    try:
        total_doctors = doctors.query.count()
        total_patients = patients.query.count()
        upcoming_appointments = appointment.query.filter_by(Status='Scheduled').count() 
        
        summary_data = {
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'upcoming_appointments': upcoming_appointments
        }
        return render_template('admin_home.html', summary=summary_data)
    except Exception as e:
        app.logger.error(f"Database error in admin_home: {e}")
        flash('Could not load dashboard data.', 'error')
        return render_template('admin_home.html', summary={}, doctors=[], patients=[], appointments=[])

@app.route("/admin/doctors", methods=["GET","POST"])
def admin_doctors():
    doctors_list=doctors.query.all()
    if request.method=="GET":
        return render_template('admin_doctors.html', doctors_list=doctors_list)
    elif request.method=="POST":
        search=request.form.get("search")
        if search:
            search_pattern = f"%{search}%"
            doctors_list = doctors.query.filter(
                doctors.doctor_name.like(search_pattern)
            ).all()
            if not doctors_list:
                flash(f"No doctors found with the name '{search}'", 'error')
            return render_template('admin_doctors.html', doctors_list=doctors_list)
        else:
            doctors_list=doctors.query.all()
            return render_template('admin_doctors.html', doctors_list=doctors_list)
@app.route("/admin/doctors/add_doctor", methods=["GET","POST"])
def add_doctor():
    if request.method=="GET":
        return render_template('add_doctor.html')
    elif request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        doctor_name=request.form.get('doctor_name')
        department=request.form.get('department')
        experience=request.form.get('experience')
        if not all([username,password,doctor_name,department,experience]):
            flash('All fields are required','error')
            return render_template('add_doctor.html')
        if len(password)<6:
            flash('Password should be atleast 6 character long','error')
            return render_template('add_doctor.html')
        existing_doctor=doctors.query.filter_by(username=username).first()
        if existing_doctor:
            flash('Username already exists', 'error')
            return render_template('add_doctor.html')
        try:
            hashed_password=generate_password_hash(password)
            new_doctor=doctors(
                username=username,
                password=hashed_password,
                doctor_name=doctor_name,
                department=department,
                experience=experience
                )
            db.session.add(new_doctor)
            db.session.commit()
            flash('Registration Succesful!','success')
            return redirect('/admin/doctors')
        except Exception as e:
            db.session.rollback()
            flash('Registration failed, Please Try again!', 'error')
            return render_template('add_doctor.html')

@app.route("/admin/doctors/<string:username>", methods=["GET"])
def delete_doctor(username):
    doctor=doctors.query.filter_by(username=username).first()
    db.session.delete(doctor)
    db.session.commit()
    flash("Doctor deleted succesfully","success")
    return redirect("/admin/doctors")

@app.route("/admin/doctors/edit/<string:username>", methods=["GET","POST"])
def edit_doctor(username):
    doctor=doctors.query.filter_by(username=username).first()
    if request.method=="GET":
        return render_template("edit_doctor.html", doctor=doctor)
    elif request.method=="POST":
        username=request.form.get('username')
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('Confirm_password')
        doctor_name=request.form.get('doctor_name')
        department=request.form.get('department')
        experience=request.form.get('experience')
        if new_password and confirm_password:
            if new_password==confirm_password:
                if len(new_password)<6:
                    flash('Password should be atleast 6 character long','error')
                    return render_template('edit_doctor.html', doctor=doctor)
            else:
                flash("Passwords do not match", 'error')
                return render_template('edit_doctor.html', doctor=doctor)
            hashed_password=generate_password_hash(new_password)
            doctor.password=hashed_password
        doctor.username=username
        doctor.doctor_name=doctor_name
        doctor.department=department
        doctor.experience=experience
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect('/admin/doctors')
    
@app.route("/admin/patients", methods=["GET","POST"])
def admin_patients():
    patient_list=patients.query.all()
    if request.method=="GET":
        return render_template('admin_patient.html', patient_list=patient_list)
    elif request.method=="POST":
        search=request.form.get("search")
        if search:
            search_pattern = f"%{search}%"
            patient_list = patients.query.filter(
                patients.patient_name.like(search_pattern)
            ).all()
            if not patient_list:
                flash(f"No patients found with the name '{search}'", 'error')
            return render_template('admin_patient.html', patient_list=patient_list)
        else:
            patient_list=patients.query.all()
            return render_template('admin_patient.html', patient_list=patient_list)

@app.route("/admin/patients/<string:username>", methods=["GET"])
def delete_patient(username):
    patient=patients.query.filter_by(username=username).first()
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted succesfully","success")
    return redirect("/admin/patients")

@app.route("/admin/patients/edit/<string:username>", methods=["GET","POST"])
def edit_patient(username):
    patient=patients.query.filter_by(username=username).first()
    if request.method=="GET":
        return render_template("edit_patient.html", patient=patient)
    elif request.method=="POST":
        username=request.form.get('username')
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('Confirm_password')
        patient_name=request.form.get('patient_name')
        contact_number=request.form.get('contact_number')
        if new_password and confirm_password:
            if new_password==confirm_password:
                if len(new_password)<6:
                    flash('Password should be atleast 6 character long','error')
                    return render_template('edit_patient.html', patient=patient)
            else:
                flash("Passwords do not match", 'error')
                return render_template('edit_patient.html', patient=patient)
            hashed_password=generate_password_hash(new_password)
            patient.password=hashed_password
        if len(contact_number)==10:
            patient.contact_number=contact_number
        else:
            flash("Invalid contact number", "error")
            return render_template('edit_patient.html', patient=patient)
        patient.username=username
        patient.patient_name=patient_name
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect('/admin/patients')

@app.route("/admin/appointments", methods=["GET"])
def appointments():
    appointment_list=appointment.query.filter_by(Status="Scheduled").all()
    for i in appointment_list:
        patient=patients.query.get(i.patient_id)
        doctor=doctors.query.get(patient.doc_id)
        i.patient_name=patient.patient_name
        i.doctor_name=patient.doctor_name
        i.department=doctor.department
        i.contact_number=patient.contact_number
    return render_template("admin_appointments.html", appointment_list=appointment_list)

@app.route("/admin/appointments/patient_history/<string:patient_name>", methods=["GET"])
def admin_patient_history(patient_name):
    patient=patients.query.filter_by(patient_name=patient_name).first()
    doctor=doctors.query.get(patient.doc_id)
    treatment_list=treatment.query.filter_by(patient_id=patient.id).all()
    return render_template("admin_patient_history.html", patient_name=patient.patient_name, treatment_list=treatment_list, doctor_name=doctor.doctor_name, department=doctor.department)

@app.route("/doctor/dashboard/<string:doctor_name>", methods=["GET"])
def doctor_dashboard(doctor_name):
        try:
            total_patients = patients.query.filter_by(doctor_name=doctor_name).count()
            upcoming_appointments = appointment.query.filter_by(Status='Scheduled').count() 
            
            summary_data = {
                'total_patients': total_patients,
                'upcoming_appointments': upcoming_appointments
            }
            return render_template('doctor_home.html', summary=summary_data, doctor_name=doctor_name)
        except Exception as e:
            app.logger.error(f"Database error in admin_home: {e}")
            flash('Could not load dashboard data.', 'error')
            return render_template('doctor_home.html', summary={}, doctors=[], patients=[], appointments=[])

@app.route("/doctor/dashboard/<string:doctor_name>/availability", methods=["GET","POST"])
def doctor_availability(doctor_name):
    doctor=doctors.query.filter_by(doctor_name=doctor_name).first()
    if request.method=="GET":
        start_date=date.today()
        availability_list=[]
        for i in range(7):
            current_date=start_date+timedelta(days=i)
            data=availability.query.filter_by(doc_id=doctor.id, Date=current_date).first()
            morning=data.Morning if data else True
            evening=data.Evening if data else True
            availability_list.append({
            'date': current_date.strftime("%Y-%m-%d"),
            'display_date': current_date.strftime("%b %d"),
            'morning_available': morning,
            'evening_available': evening
            })
        return render_template("doctor_availability.html", availability_list=availability_list, doctor_name=doctor_name)
    elif request.method=="POST":
        start_date=date.today()
        for i in range(7):
            current_date=start_date+timedelta(days=i)
            date_key= current_date.strftime("%Y-%m-%d")
            data=availability.query.filter_by(doc_id=doctor.id, Date=current_date).first()
            # Check if the checkboxes were submitted (only submitted if checked)
            morning= request.form.get(f'morning_{date_key}') == 'on'
            evening= request.form.get(f'evening_{date_key}') == 'on'
            if data:
                data.Morning=morning
                data.Evening=evening
            else:
                new_availability=availability(
                    doc_id=doctor.id,
                    Date=current_date, 
                    Morning=morning, 
                    Evening=evening
                )
                db.session.add(new_availability)
        db.session.commit()
        return redirect("/doctor/dashboard/"+doctor_name)

@app.route("/doctor/<string:doctor_name>/patients", methods=["GET"])
def doctor_patients(doctor_name):
    patient_list=patients.query.filter_by(doctor_name=doctor_name).all()
    return render_template("doctor_patient.html", patient_list=patient_list, doctor_name=doctor_name)

@app.route("/doctor/<string:doctor_name>/patients/patient_history/<string:patient_name>", methods=["GET"])
def view_patient(patient_name, doctor_name):
    patient=patients.query.filter_by(patient_name=patient_name, doctor_name=doctor_name).first()
    doctor=doctors.query.filter_by(doctor_name=doctor_name).first()
    treatment_list=treatment.query.filter_by(patient_id=patient.id).all()
    return render_template("doctor_patient_history.html", patient_name=patient.patient_name, treatment_list=treatment_list, doctor_name=doctor.doctor_name, department=doctor.department)

@app.route("/doctor/<string:doctor_name>/appointments", methods=["GET"])
def doctor_appointments(doctor_name):
    doctor=doctors.query.filter_by(doctor_name=doctor_name).first()
    upcoming_appointments = appointment.query.filter_by(Status='Scheduled', doc_id=doctor.id).all()
    appointment_list=[]
    for i in upcoming_appointments:
        patient=patients.query.get(i.patient_id)
        i.patient_name=patient.patient_name
    return render_template("doctor_appointments.html", appointment_list=upcoming_appointments, doctor_name=doctor_name)

@app.route("/doctor/<string:doctor_name>/appointments/<int:appointment_id>/<string:patient_name>", methods=["GET","POST"])
def update_history(patient_name, appointment_id, doctor_name):
    doctor=doctors.query.filter_by(doctor_name=doctor_name).first()
    patient=patients.query.filter_by(patient_name=patient_name, doctor_name=doctor_name).first()
    appointments=appointment.query.filter_by(patient_id=patient.id, doc_id=doctor.id, Status='Scheduled').first()
    if request.method=="GET":
        return render_template("update_history.html", patient=patient , appointments=appointments, doctor=doctor)
    elif request.method=="POST":
        test=request.form.get('tests')
        diagnosis=request.form.get('diagnosis')
        prescription=request.form.get('prescription')
        medicine=request.form.get('medicine')
        new_treatment=treatment(
            patient_id=patient.id,
            appointment_id=appointment_id,
            tests=test,
            Diagnosis=diagnosis,
            Prescription=prescription,
            Medicines=medicine
        )
        db.session.add(new_treatment)
        db.session.commit()
        flash('Patient history updated successfully', 'success')
        return redirect("/doctor/"+doctor_name+"/appointments")


@app.route("/doctor/<string:doctor_name>/appointments/cancel/<int:appointment_id>", methods=["GET"])
def cancel_appointment(appointment_id, doctor_name):
    curr=appointment.query.get(appointment_id)
    data=availability.query.filter_by(doc_id=curr.doc_id,Date=curr.Date).first()
    if curr.Time=="09:00-1:00pm":
        data.Morning=True
    else:
        data.Evening=True
    db.session.delete(curr)
    db.session.commit()
    flash("Appointment Canceled","success")
    return redirect("/doctor/"+doctor_name+"/appointments")

@app.route("/doctor/<string:doctor_name>/appointments/<int:appointment_id>", methods=["GET"])
def mark_as_completed(appointment_id, doctor_name):
    curr=appointment.query.get(appointment_id)
    curr.Status='Completed'
    data=availability.query.filter_by(doc_id=curr.doc_id,Date=curr.Date).first()
    if curr.Time=="09:00-1:00pm":
        data.Morning=True
    else:
        data.Evening=True
    db.session.commit()
    flash('Appointment Completed', 'success')
    return redirect("/doctor/"+doctor_name+"/appointments")

@app.route("/patient/dashboard/<string:patient_name>", methods=["GET"])
def patient_dashboard(patient_name):
    patient=patients.query.filter_by(patient_name=patient_name).first()
    doctor=doctors.query.filter_by(doctor_name=patient.doctor_name).first()
    upcoming=appointment.query.filter_by(patient_id=patient.id, doc_id=doctor.id, Status='Scheduled').all()
    appointment_list=[]
    for i in upcoming:
        appointment_list.append({
            "id": i.id,
            "doctor_name": doctor.doctor_name,
            "department": doctor.department,
            "date": i.Date,
            "time": i.Time
        })
    return render_template("patient_home.html", patient_name=patient_name, doctor=doctor, appointment_list=appointment_list)

@app.route("/patient/dashboard/<string:patient_name>/history", methods=["GET"])
def patient_history(patient_name):
    patient=patients.query.filter_by(patient_name=patient_name).first()
    doctor=doctors.query.filter_by(doctor_name=patient.doctor_name).first()
    treatment_list=treatment.query.filter_by(patient_id=patient.id).all()
    return render_template("patient_history.html", patient_name=patient.patient_name, treatment_list=treatment_list, doctor_name=doctor.doctor_name, department=doctor.department)

@app.route("/patient/dashboard/<string:patient_name>/edit", methods=["GET","POST"])
def edit_profile(patient_name):
    patient=patients.query.filter_by(patient_name=patient_name).first()
    if request.method=="GET":
        return render_template("edit_profile.html", patient=patient)
    elif request.method=="POST":
        username=request.form.get('username')
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('Confirm_password')
        patient_name=request.form.get('patient_name')
        contact_number=request.form.get('contact_number')
        if new_password and confirm_password:
            if new_password==confirm_password:
                if len(new_password)<6:
                    flash('Password should be atleast 6 character long','error')
                    return render_template('edit_patient.html', patient=patient)
            else:
                flash("Passwords do not match", 'error')
                return render_template('edit_profile.html', patient=patient)
            hashed_password=generate_password_hash(new_password)
            patient.password=hashed_password
        if len(contact_number)==10:
            patient.contact_number=contact_number
        else:
            flash("Invalid contact number", "error")
            return render_template('edit_profile.html', patient=patient)
        patient.username=username
        patient.patient_name=patient_name
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect('/patient/dashboard/'+patient_name)

@app.route("/patient/dashboard/<string:patient_name>/check_availability/<string:username>", methods=["GET","POST"])
def check_availability(username,patient_name):
    doctor=doctors.query.filter_by(username=username).first()
    patient=patients.query.filter_by(patient_name=patient_name).first()
    if request.method=="GET":
        start_date=date.today()
        availability_list=[]
        for i in range(7):
            current_date=start_date+timedelta(days=i)
            data=availability.query.filter_by(doc_id=doctor.id, Date=current_date).first()
            morning=data.Morning if data else True
            evening=data.Evening if data else True
            availability_list.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'display_date': current_date.strftime("%b %d"),
                'morning_available': morning,
                'evening_available': evening
            })
        return render_template("check_availability.html", availability_list=availability_list, patient_name=patient_name, username=username)
    
    elif request.method=="POST":
        doctor=doctors.query.filter_by(username=username).first()
        patient=patients.query.filter_by(patient_name=patient_name).first()
        selected_slot = request.form.get('selected_slot') 

        if not selected_slot:
            flash('Please select an available time slot.', 'error')
            return redirect(url_for('check_availability', username=username, patient_name=patient_name))
        
        try:
            date_str, time_slot = selected_slot.split('_')
            appointment_date = date.fromisoformat(date_str)
        except ValueError:
            flash('Invalid slot format selected.', 'error')
            return redirect(url_for('check_availability', username=username, patient_name=patient_name))

        data = availability.query.filter_by(doc_id=doctor.id, Date=appointment_date).first()
        
        if not data:
            flash('Availability record not found for this date. Cannot book.', 'error')
            return redirect(url_for('check_availability', username=username, patient_name=patient_name))

        slot_booked= ""
        slot_success=False

        if time_slot == 'M' and data.Morning:
            data.Morning = False
            slot_booked+="09:00-1:00pm"
            slot_success=True
        elif time_slot == 'E' and data.Evening:
            data.Evening = False
            slot_booked+="04:00-8:00pm"
            slot_success=True

        if slot_success:
            new_appointment = appointment(
                patient_id=patient.id,
                doc_id=doctor.id,
                Date=data.Date,
                Time=slot_booked,
                Status="Scheduled"
            )
            db.session.add(new_appointment)
            db.session.commit()
            
            flash(f"Appointment booked successfully for {date_str} in the {'Morning' if time_slot == 'M' else 'Evening'}!", 'success')
            return redirect(url_for('patient_dashboard', patient_name=patient_name))
        
        flash('Failed to book appointment due to an unexpected error.', 'error')
        return redirect(url_for('check_availability', username=username, patient_name=patient_name))

@app.route("/patient/dashboard/<string:patient_name>/view_details/<string:username>", methods=["GET"])
def view_details(username,patient_name):
    doctor=doctors.query.filter_by(username=username).first()
    return render_template('view_details.html', doctor=doctor, patient_name=patient_name, username=username)
    
@app.route("/patient/dashboard/<string:patient_name>/<int:appointment_id>", methods=["GET"])
def cancel(patient_name, appointment_id):
    curr=appointment.query.get(appointment_id)
    data=availability.query.filter_by(doc_id=curr.doc_id,Date=curr.Date).first()
    if curr.Time=="09:00-1:00pm":
        data.Morning=True
    else:
        data.Evening=True
    db.session.delete(curr)
    db.session.commit()
    flash("Appointment Canceled",'error')
    return redirect("/patient/dashboard/"+patient_name)




        
