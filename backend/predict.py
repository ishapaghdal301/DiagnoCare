from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
import pickle
from config.database import collection_name1, collection_name2

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Adjust the origin based on your React app's URL

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key directly in the client constructor
client = OpenAI(api_key=OPENAI_API_KEY)

# Model1 : Alzheimer
# Model2 : Brain Tumor
# classifier1 : Diabetes
# classifier2 : Lung Cancer
model1 = tf.keras.models.load_model('../Models/alzheimer2.h5')
model2 = tf.keras.models.load_model('../Models/BrainTumor3.h5')

# Load trained Diabetes model
with open("./pklFiles/Diabetes.pkl", "rb") as f:
    classifier1 = pickle.load(f)

with open("pklFiles/LungCancer.pkl", "rb") as f:
    classifier2 = pickle.load(f)



def generate_report(predicted_category,disease):
    prompt_Symtoms = f"You are a medical practictioner and an expert working for a very reputed hospital.Give Symptoms for the disease:{disease} of the category: {predicted_category}."
    prompt_Cause = f"You are a medical practictioner and an expert working for a very reputed hospital.Give Cause for the disease:{disease} of the category: {predicted_category}."
    prompt_Treatment = f"You are a medical practictioner and an expert working for a very reputed hospital.Give Treatment for the disease:{disease} of the category: {predicted_category}."
    prompt_Recommendation = f"You are a medical practictioner and an expert working for a very reputed hospital.Give Recommendation for the disease:{disease} of the category: {predicted_category}."

    Symptoms = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
           {"role": "system", "content": "Answer the question in less than 20 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user","content": prompt_Symtoms}
        ],
        # max_tokens=70
    )

    Cause = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
           {"role": "system", "content": "Answer the question in less than 20 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user","content": prompt_Cause}
        ],
        # max_tokens=70
    )

    Treatment = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
           {"role": "system", "content": "Answer the question in less than 30 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user","content": prompt_Treatment}
        ],
        # max_tokens=70
    )

    Recommendation = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
           {"role": "system", "content": "Answer the question in less than 40 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user","content": prompt_Recommendation}
        ],
        # max_tokens=70
    )

    # print(response.choices[0].message)
    # medical_report = parse_medical_report(response.choices[0].message.content)
    return {'Symptoms' : Symptoms.choices[0].message.content, 'predicted_category' : predicted_category, 'Treatment' : Treatment.choices[0].message.content, 'Recommendation' : Recommendation.choices[0].message.content}

def predict_alzheimer():
    try:
        file = request.files['file']

        img_bytes = file.read()

        img = image.load_img(io.BytesIO(img_bytes), target_size=(150, 150))
        img_array = image.img_to_array(img)
        image_array = img_array.reshape(1, 150, 150, 3)

        prediction = model1.predict(image_array)

        categories = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
        predicted_category = categories[np.argmax(prediction)]

        print(predicted_category)
        medical_report = generate_report(predicted_category,"alzheimer")

        return jsonify(medical_report), 200

    except Exception as e:
        print(e)
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

def predict_braintumor():
    try:
        file = request.files['file']

        img_bytes = file.read()

        img = image.load_img(io.BytesIO(img_bytes), target_size=(150, 150)) 
        img_array = image.img_to_array(img)
        image_array = img_array.reshape(1, 150, 150, 3)

        prediction = model2.predict(image_array)

        categories = ["Glioma Tumor", "Meningioma Tumor", "No Tumor", "Pituitary Tumor"]
        predicted_category = categories[np.argmax(prediction)]

        print(predicted_category)
        medical_report = generate_report(predicted_category,"braintumor")
        print(medical_report)

        return jsonify(medical_report), 200

    except Exception as e:
        print(e)
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500


def predict_diabetes():
    try:
        data = request.json
        HighBP = int(data['HighBP'])
        HighChol = int(data['HighChol'])
        CholCheck = int(data['CholCheck'])
        BMI = float(data['BMI'])
        Stroke = int(data['Stroke'])
        HeartDiseaseorAttack = int(data['HeartDiseaseorAttack'])
        Sex = int(data['Sex'])
        Age = int(data['Age'])
        prediction = classifier1.predict([[HighBP, HighChol, CholCheck, BMI, Stroke, HeartDiseaseorAttack, Sex, Age]])
        categories = ["No Diabetes" , "Pre Diabetes", "Diabetes"]
        if prediction[0] == 0:
            predicted_category = categories[0]
        
        elif prediction[0] == 1:
            predicted_category = categories[1]

        else:
            predicted_category = categories[2]
        
        print(predicted_category)
        
        data['Result'] = predicted_category

        collection_name1.insert_one(data)
        medical_report = generate_report(predicted_category,"diabetes")
        print("Data of Diabetes stored successfully!")
        print(medical_report)
        return jsonify(medical_report), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": f"Error while predicting Diabetes: {str(e)}"}), 500



def predict_lungcancer():
    data = request.json
    print(data)
    Age = data['Age']
    Gender = data['Gender']
    AirPollution = data['AirPollution']
    Smoking = data['Smoking']
    Fatigue = data['Fatigue']
    WeightLoss = data['WeightLoss']
    ShortnessofBreath = data['ShortnessofBreath']
    Wheezing = data['Wheezing']
    SwallowingDifficulty = data['SwallowingDifficulty']
    ClubbingofFingerNails = data['ClubbingofFingerNails']
    FrequentCold = data['FrequentCold']
    DryCough = data['DryCough']
    prediction = classifier2.predict([[Age, Gender, AirPollution, Smoking, Fatigue, WeightLoss, ShortnessofBreath,
                                        Wheezing, SwallowingDifficulty, ClubbingofFingerNails, FrequentCold, DryCough]])
    
    categories = ["Low" , "Medium" , "High"]
    if prediction[0] == 0:
         predicted_category = categories[0]
    elif prediction[0] == 1:
         predicted_category = categories[1]
    else:
         predicted_category = categories[2]

    data['Result'] = predicted_category
    collection_name2.insert_one(data)
    medical_report = generate_report(predicted_category,"lung cancer")
    print("Data of Lung Cancer stored successfully!")
    print(medical_report)
    return jsonify(medical_report), 200
