import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()

API_KEY = os.getenv("WATSONX_API_KEY")
DEPLOYMENT_URL = os.getenv("WATSONX_DEPLOYMENT_URL")
IAM_URL = "https://iam.cloud.ibm.com/identity/token"

def get_iam_token():
    response = requests.post(
        IAM_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": API_KEY
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get IAM token: " + response.text)

@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    data = request.json
    destination = data.get('destination', 'Goa')
    days = data.get('days', 3)

    user_prompt = (
        f"Create a {days}-day travel itinerary for {destination}, India. "
        f"Include popular attractions, food spots, and travel tips. Format clearly."
    )

    try:
        token = get_iam_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }

        response = requests.post(DEPLOYMENT_URL, headers=headers, json=payload)
        print("🔎 Watsonx Agent Response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Watsonx Agent Error",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
