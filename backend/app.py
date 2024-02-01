from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient

import tensorflow as tf
from PIL import Image
import numpy as np
import io 
# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient('mongodb+srv://dm_37:SWKIOAkzdQgoWn68@cluster0.u4wm1ik.mongodb.net/sdp_backend')
db = client['sdp_backend']
auth_collection = db['auth']

@app.route('/hello' , methods=['GET'])
def sayHello():
    return "Hello User!"

@app.route('/api/login' , methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Give me rest of the code 
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = auth_collection.find_one({'email': email})
    
    if user:
        # For now, let's compare the password directly (insecure, use hashing in production)
        if user['password'] == password:
            # Set user information in the session (you might want to use a more secure way in production)
            session['user'] = {
                'email': user['email'],
                'name': user['name']
            }
            return jsonify({'message': 'Login successful' , 'user' : user})
        else:
            return jsonify({'message': 'Incorrect password'}), 401
    else:
        return jsonify({'message': 'User not found'}), 404


model = tf.keras.models.load_model('../Models/alzheimer2.h5')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']

        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return jsonify({"error": "Invalid file type. Please upload a valid image."}), 400

        image = Image.open(io.BytesIO(file.read())).convert("RGB").resize((150, 150))
        image_array = np.array(image)
        image_array = image_array.reshape(1, 150, 150, 3)

        prediction = model.predict(image_array)

        categories = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
        predicted_category = categories[np.argmax(prediction)]

        report = {
            "prediction_category": "predicted_category",
            "precautions": "Include precautions information based on the predicted category.",
            "medicine": "Include medicine information based on the predicted category.",
            "motivation": "Include motivational message based on the predicted category."
        }

        return jsonify(report), 200

    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500


@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    # password = generate_password_hash(data.get('password'), method='sha256')
    password = data.get('password')

    user = {
        'name': name,
        'email': email,
        'password': password
    }
    # Here Instead of manually getting JSON data from POSTMAN we need to get it from frontend !!
    #For the same in frontend axios url to post data entered by user will be passed to '/api/signup' end point and from there POST Method will be called automatically!

    auth_collection.insert_one(user)
    print("Signup successful")
    return jsonify({'message': 'Signup successful'})


if __name__ == '__main__':
    app.run(debug=True)
