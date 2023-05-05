import datetime
import json
import os
import pymongo
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv, dotenv_values

load_dotenv()


app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})


openai.api_key = os.environ.get("OPENAI_API_KEY")
conn_str = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(conn_str)
db = client.HealthMS

def insert_data(collection, data):
    db[collection].insert_one(data)
    return jsonify({'success':True})

@app.route('/get_data', methods=['GET'])
def get_data():
    userId = hash(request.args.get('userID'))
    category = request.args.get('category')
    data = list(db[category].find({'userId': userId}))
    for item in data:
        item["_id"] = str(item["_id"])
    print("Returning this data:", data)
    return jsonify(data)

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    user_text = data['text']
    userId = hash(data['userID'])
    example_json = "{'symptom': 'cough', 'notes': 'exercise-related'}"
    example_2_json = "{'exercise': 'pushups', 'notes':'20 pushups'}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Parse the following text for health-related categorical data belonging to these categories (exercise, food, stress, medication, mood, patterns, sleep, symptom, allergies, illnesses) and output it (and only it!) in JSON form. An example is {example_json}. Another example is {example_2_json}. Here is the user text to parse: {user_text}"},
            {"role": "user", "content": user_text}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    parsed_data = response.choices[0].message['content']
    parsed_data = parsed_data.replace("'", "\"")

    try:
        parsed_data_jsons = json.loads(parsed_data)
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Failed to parse the data'})

    if type(parsed_data_jsons) != type([]):
        parsed_data_jsons = [parsed_data_jsons]

    for parsed_data_json in parsed_data_jsons:
        for category, data_value in parsed_data_json.items():
            if category == "notes":
                continue
            data_dict = {'userId': userId, 'type': data_value, 'date': f"{datetime.datetime.now():%Y-%m-%d}"}
            print(category, data_dict)
            insert_data(category, data_dict)

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
