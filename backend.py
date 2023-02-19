"""
1. Connect to the cloud MongoDB database "HealthMS"
    a. if table name "stress" does not exist, create with schema {userId:int, stressLevel:int, date:str, notes:str}
    b. if table name "mood" does not exist, create with schema {userId:int, mood:str, date:str, notes:str}
    c. if table name "food" does not exist, create with schema {userId:int, name:str, calories:int, cuisine:str, time:str, type:str, notes:str, date:str}
2. Create a flask API that will take in data from the following endpoints and upload it to our database.
    a. /stress -- table name "stress", {userId:int, stressLevel:int, date:str, notes:str}
    b. /mood -- table name "mood", {userId:int, mood:str, date:str, notes:str}
    c. /food -- table name "food", {userId:int, name:str, calories:int, cuisine:str, time:str, type:str, notes:str, date:str}
3. Create a method called filter_data(userId, start, end, tables) to access values filtered by userId:int and between the dates start:string and end:string from our DB connection for a list of table names and return it in the form {table_name:[str,str,str], table_name:[str,str,str]}
4. Create an API endpoint that will take in data of the following structure, feed it into the filter_data method, and return that result
    a. /patterns {categories:[str,...,str], symptom:str, start:string, end:string}
"""
import os

import openai
import pymongo
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
conn_str = os.getenv("HEALTHMS_IJEFFERS")
client = pymongo.MongoClient(conn_str)
db = client.HealthMS

openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route('/drugsalcohol', methods=['POST'])
def drugsalcohol():
    print("uploaded to drugsalcohol!")
    data = request.get_json()
    userId = data['userID']
    type = data['type']
    quantity = data['quantity']
    unit = data['unit']
    date = data['date']
    notes = data['notes']
    print(userId, type, quantity, unit, date, notes)
    db.drugsalcohol.insert_one({'userId':userId, 'type':type, 'quantity':quantity, 'unit':unit, 'date':date, 'notes':notes})
    return jsonify({'success':True})


@app.route('/allergies', methods=['POST'])
def allergies():
    print("uploaded to allergies!")
    data = request.get_json()
    userId = data['userID']
    type = data['type']
    category = data['category']
    intensity = data['intensity']
    date = data['date']
    notes = data['notes']
    print(userId, type, intensity, date, notes)
    db.allergies.insert_one({'userId':userId, 'category':category, 'type':type, 'intensity':intensity, 'date':date, 'notes':notes})
    return jsonify({'success':True})


@app.route('/illnesses', methods=['POST'])
def illnesses():
    print("uploaded to illnesses!")
    data = request.get_json()
    userId = data['userID']
    type = data['type']
    name = data['name']
    date = data['date']
    notes = data['notes']
    print(userId, type, name, date, notes)
    db.illnesses.insert_one({'userId':userId, 'type':type, 'name':name, 'date':date, 'notes':notes})
    return jsonify({'success':True})

@app.route('/ailyssa', methods=['POST'])
def ailyssa():
    print("Generating ailyssa's response!")
    data = request.get_json()
    userID = data["userID"]
    prompt = data["prompt"]
    print(userID, prompt)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.6,
        max_tokens=128
    )
    return {"text":response}


@app.route('/patterns', methods=['POST'])
def patterns():
    print("identifying patterns!")
    data = request.get_json()
    categories = data['categories']
    symptom = data['symptom'].lower()
    start = data['start']
    end = data['end']
    userId = data['userId']
    print(userId, symptom, categories, start, end)
    result = {}
    result[symptom] = []
    for entry in list(db.symptom.find({'userId': userId, 'symptom':symptom, 'date': {'$gte': start, '$lte': end}})):
        result[symptom].append(str(entry['date']))

    for category in categories:
        result[category] = []
        print(result[category])
        for entry in list(db[category.lower()].find({'userId':userId, 'date':{'$gte':start, '$lte':end}})):
            result[category].append(entry['date'])
    return jsonify(result)

@app.route('/getSymptoms', methods=['POST'])
def getSymptoms():
    print("Finding Symptoms!")
    # data = request.get_json()
    # userId = data['userID']
    # symptoms = db.symptom.find({'userId': userId})
    # return jsonify({'success': True, 'symptoms': dumps(list(symptoms))})
    data = request.get_json()
    userId = data['userID']
    print(userId)
    symptoms = db.symptom.find({'userId': userId})
    symptom_names = list(set([s['symptom'] for s in symptoms]))
    return jsonify({'success': True, 'symptoms': symptom_names})

@app.route('/symptom', methods=['POST'])
def symptom():
    print("uploaded to symptom!")
    data = request.get_json()
    userId = data['userID']
    symptom = data['symptom']
    description = data['description']
    category = data['category']
    date = data['date']
    notes = data['notes']
    print(userId, symptom, description, category, date, notes)
    db.symptom.insert_one({'userId':userId, 'description':description, 'category':category, 'symptom':symptom, 'date':date, 'notes':notes})
    return jsonify({'success':True})


@app.route('/medication', methods=['POST'])
def medication():
    print("uploaded to medication!")
    data = request.get_json()
    userId = data['userID']
    medication = data['medication']
    dosage = data['dosage']
    date = data['date']
    notes = data['notes']
    print(userId, medication, dosage, date, notes)
    db.medication.insert_one({'userId':userId, 'dosage':dosage, 'medication':medication, 'date':date, 'notes':notes})
    return jsonify({'success':True})


@app.route('/exercise', methods=['POST'])
def exercise():
    print("uploaded to exercise!")
    data = request.get_json()
    userId = data['userID']
    exercise = data['exercise']
    volume = data['volume']
    date = data['date']
    notes = data['notes']
    print(userId, exercise, date, notes)
    db.exercise.insert_one({'userId':userId, 'volume':volume, 'exercise':exercise, 'date':date, 'notes':notes})
    return jsonify({'success':True})


@app.route('/sleep', methods=['POST'])
def sleep():
    print("uploaded to sleep!")
    data = request.get_json()
    userId = data['userID']
    sleepHours = data['sleepHours']
    date = data['date']
    notes = data['notes']
    print(userId, sleepHours, date, notes)
    db.sleep.insert_one({'userId':userId, 'sleepHours':sleepHours, 'date':date, 'notes':notes})
    return jsonify({'success':True})


@app.route('/stress', methods=['POST'])
def stress():
    print("uploaded to stress!")
    data = request.get_json()
    userId = data['userID']
    stressLevel = data['stressLevel']
    date = data['date']
    notes = data['notes']
    print(userId, stressLevel, date, notes)
    db.stress.insert_one({'userId':userId, 'stressLevel':stressLevel, 'date':date, 'notes':notes})
    return jsonify({'success':True})

@app.route('/mood', methods=['POST'])
def mood():
    print("Uploaded to mood!")
    data = request.get_json()
    userId = data['userID']
    mood = data['mood']
    date = data['date']
    notes = data['notes']
    print(userId,mood,date,notes)
    db.mood.insert_one({'userId':userId, 'mood':mood, 'date':date, 'notes':notes})
    return jsonify({'success':True})

@app.route('/food', methods=['POST'])
def food():
    print("Uploaded to food!")
    data = request.get_json()
    userId = data['userID']
    name = data['name']
    calories = data['calories']
    cuisine = data['cuisine']
    time = data['time']
    type = data['type']
    notes = data['notes']
    date = data['date']
    print(userId, name, calories, cuisine, time, type, date, notes)
    db.food.insert_one({'userId':userId, 'name':name, 'calories':calories, 'cuisine':cuisine, 'time':time, 'type':type, 'notes':notes, 'date':date})
    return jsonify({'success':True})

if __name__ == '__main__':
    app.run(debug=True)
