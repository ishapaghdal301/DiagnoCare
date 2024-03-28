from flask import Blueprint, jsonify, request 
from bson import Binary
from pymongo import MongoClient
from bson import ObjectId, json_util
from extension import doctor_collection, auth_collection
from flask_jwt_extended import jwt_required, current_user
import base64
from PIL import Image as PILImage
from io import BytesIO
from datetime import datetime

doctor_bp = Blueprint('p-layout', __name__)

@doctor_bp.route('/add', methods=['POST'])
@jwt_required()
def add_doctor():
     try:
        data = request.form.to_dict(flat=False)  # Parse form data to dictionary

        file = request.files['photo']
        image = PILImage.open(file)
        
        # Fetch existing user document from auth_collection
        user = auth_collection.find_one({'_id': ObjectId(current_user.id)})
        
        img_byte_array = BytesIO()
        image.save(img_byte_array, format=image.format)
        encoded_image = Binary(img_byte_array.getvalue())

        qualifications = []
        experiences = []
        timeslots = []

        # Extract qualifications
        if data.get('qualifications[startDate]'):
            for i in range(len(data.get('qualifications[startDate]'))):
                qualification = {
                    'startDate': datetime.strptime(data.get('qualifications[startDate]')[i], '%Y-%m-%d'),
                    'endDate': datetime.strptime(data.get('qualifications[endDate]')[i], '%Y-%m-%d'),
                    'degree': data.get('qualifications[degree]')[i],
                    'university': data.get('qualifications[university]')[i]
                }
                qualifications.append(qualification)

        # Extract experiences
        if data.get('experiences[startDate]'):
            for i in range(len(data.get('experiences[startDate]'))):
                experience = {
                    'startDate': datetime.strptime(data.get('experiences[startDate]')[i], '%Y-%m-%d'),
                    'endDate': datetime.strptime(data.get('experiences[endDate]')[i], '%Y-%m-%d'),
                    'position': data.get('experiences[position]')[i],
                    'location': data.get('experiences[location]')[i]
                }
                experiences.append(experience)

        # Extract timeslots
        if data.get('timeslots[date]'):
            for i in range(len(data.get('timeslots[date]'))):
                timeslot = {
                    'date': datetime.strptime(data.get('timeslots[date]')[i], '%Y-%m-%d'),
                    'startTime': data.get('timeslots[startTime]')[i],
                    'endTime': data.get('timeslots[endTime]')[i]
                }
                timeslots.append(timeslot)

         # Extract other basic 
        email = data.get('email')[0]
        name = data.get('name')[0]
        password = user.get('password')
        role = user.get('role')
        doctor_id = current_user.id
        photo = encoded_image
        about = data.get('about')[0]
        bio = data.get('bio')[0]
        phone = data.get('phone')[0]
        specialization = data.get('specialization')[0]
        price = data.get('price')[0]
        

        doctor = {
            'doctor_id': doctor_id,
            'name': name,
            'email': email,
            'password' : password,
            'role' : role,
            'phone': phone,
            'bio': bio,
            'specialization': specialization,
            'price': price,
            'about': about,
            'photo': photo,

        }

        # Add qualifications if available
        if qualifications:
            doctor['qualifications'] = qualifications

        # Add experiences if available
        if experiences:
            doctor['experiences'] = experiences

        # Add timeslots if available
        if timeslots:
            doctor['timeslots'] = timeslots
        
        # Update user document with profile information from form
        if user:
            # Update existing fields with form data
            user.update(doctor)
            # Remove name and email fields from form data if they exist in the database
            if 'name' in user:
                del data['name']
            if 'email' in user:
                del data['email']
            # Update profile information in the document
            auth_collection.update_one({'_id': ObjectId(current_user.id)}, {'$set': user})
            # Update name and email from form data (if present)
            auth_collection.update_one({'_id': ObjectId(current_user.id)}, {'$set': doctor})

            return jsonify({'message': 'Profile saved successfully'}), 200
        else:
            return jsonify({'message': 'User profile not found'}), 404
     except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500


# <<<<<<< HEAD

# # Get all patients
# =======
# #Get all doctors
# >>>>>>> 64e4f386753074efe3f4164b7e899c1ee89891bb
@doctor_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_all_doctors():
    try:
        
         doctors = list(doctor_collection.find({}))
        
         doctors = json_util.dumps(doctors)
        
         return doctors, 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500
