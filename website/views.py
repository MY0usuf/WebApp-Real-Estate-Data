from flask import Blueprint, render_template, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from .models import Note,Client
from . import db
import search_transaction as st
import search_rental as sr
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note') #Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/clients', methods=['GET', 'POST'])
@login_required
def clients():
    if request.method == 'POST': 
        note = request.form.get('note') #Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_name = Client(name=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_name) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("clients.html", user=current_user)

@views.route('/delete-client', methods=['POST'])
def delete_note():  
    name = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    clientId = name['clientId']
    name = Client.query.get(clientId)
    if name:
        if name.user_id == current_user.id:
            db.session.delete(name)
            db.session.commit()

    return jsonify({})

@views.route('/transaction', methods = ['GET','POST'])
@login_required
def transaction():
        if request.method == "POST":
            transaction_column_name = ['Transaction Type', 'Registration type', 'Project', 'Area', 'Usage', 'Property Type','Property Sub Type', 'Room(s)','Property Size (sq.ft)', 'Property Size (sq.m)','Transaction Date']
            
            transaction_type = request.form["transaction_pTrxType"]
            registration_type = request.form["transaction_pIsOffPlan"]
            Project = request.form["transaction_pProjectId"]
            Area = request.form["transaction_pAreaId"]
            Usage = request.form["transaction_pUsageId"]
            no_of_rooms = request.form["transaction_pRoomsId"]
            Property_type = request.form["transaction_pPropType"]
            property_size_sq_ft = request.form["PropertySizeSqFt"]
            property_size_sq_mt = request.form["PropertySizeSqM"]
            property_sub_type = request.form["transaction_pPropertysubtypeId"]
            start_date = request.form["startDate"]

            print(type(start_date))

            search_value = [transaction_type, registration_type, Project, Area, Usage, Property_type, property_sub_type, no_of_rooms, property_size_sq_ft, property_size_sq_mt, start_date]
            search_value = st.change(search_value)
            print(search_value)
            matching_rows = st.search(search_value, transaction_column_name)
            matching_rows = matching_rows.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
            matching_rows.reset_index(inplace = True)
            matching_rows.drop("index",axis=1,inplace=True)
            print(matching_rows.shape[0])
            print(matching_rows.head(10))
            if not matching_rows.empty:
                transaction_table = matching_rows.to_html(float_format=lambda x: '%10.2f' % x)
                print(type(transaction_table))
                return render_template('transaction_table.html', table = transaction_table, property_sub_type_list = st.property_sub_type_list, area_list = st.area_list, area_length = st.area_length, project_list = st.project_list, project_length = st.project_length, property_sub_type_length = st.property_sub_type_length, no_of_rooms_length = st.no_of_rooms_length, no_of_rooms_list = st.no_of_rooms_list)
            else:
                flash('No Data Available for the current criteria',category='error')
        return render_template('transaction.html', property_sub_type_list = st.property_sub_type_list, area_list = st.area_list, area_length = st.area_length, project_list = st.project_list, project_length = st.project_length, property_sub_type_length = st.property_sub_type_length, no_of_rooms_length = st.no_of_rooms_length, no_of_rooms_list = st.no_of_rooms_list)


@views.route('/rental', methods = ['GET','POST'])
@login_required
def rental():
        if request.method == 'POST':
            rental_column_name = ['Version','Area','Property Type','Usage','Project','Property Size (sq.m)','Property Size (sq.ft)']

            version = request.form["rental_pversion"]
            area = request.form["rental_pAreaId"]
            property_type = request.form["rental_pPropType"]
            usage = request.form["rental_pUsageId"]
            project = request.form["rental_pProjectId"]
            property_size_sq_mt = request.form["PropertySizeSqM"]
            property_size_sq_ft = request.form["PropertySizeSqFt"]
            start_date = request.form["startDate"]
            

            search_value = [version, area, property_type, usage, project, property_size_sq_mt, property_size_sq_ft,start_date]
            search_value = sr.change(search_value)
            print(search_value)
            matching_rows = sr.search(search_value, rental_column_name)
            matching_rows = matching_rows.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
            matching_rows.reset_index(inplace = True)
            matching_rows.drop("index",axis=1,inplace=True)
            print(matching_rows.head(10))
            if not matching_rows.empty:
                rental_table = matching_rows.to_html()
                print(type(rental_table))
                return render_template('rental_table.html', table = rental_table, area_list = sr.area_list, area_length = sr.area_length, project_list = sr.project_list, project_length = sr.project_length)
            else:
                flash('No Data Available for the current criteria',category='error')
        return render_template('rental.html', area_list = sr.area_list, area_length = sr.area_length, project_list = sr.project_list, project_length = sr.project_length)

@views.route('/return_transaction_file')
def return_transaction_file():
    return send_file('C:\\Users\\yousu\\Desktop\\Python Projects\\Flask Website\\transaction_results.csv',as_attachment=True)

@views.route('/return_rental_file')
def return_rental_file():
    return send_file('C:\\Users\\yousu\\Desktop\\Python Projects\\Flask Website\\rental_results.csv',as_attachment=True)