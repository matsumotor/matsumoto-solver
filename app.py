from flask import Flask, request, jsonify
import requests
import time
import os

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY")

@app.route('/')
def home():
    return "✅ MatsumotoSolver - FunBypass vFinal"

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    try:
        data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict()

        payload = {
            "clientKey": API_KEY,
            "task": {
                "type": "FunCaptchaTask",
                "websiteURL": "https://www.roblox.com/games/3475397644",
                "websitePublicKey": "476068BF-9607-4799-B53D-966BE98E2B81",
                "websiteSubdomain": "roblox-api.arkoselabs.com"
            }
        }

        if data.get("proxy"):
            payload["task"]["proxy"] = data.get("proxy")

        # Create Task
        resp = requests.post("https://api.funbypass.com/createTask", json=payload, timeout=30)
        create_data = resp.json()

        if create_data.get("errorId") != 0:
            return jsonify({"error": create_data.get("errorCode", "error")}), 400

        task_id = create_data["taskId"]

        # Polling
        for _ in range(120):
            time.sleep(0.7)
            result = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20).json()
            
            if result.get("status") == "ready":
                return jsonify({"success": True, "solution": result["solution"]})

            if result.get("errorId") != 0:
                return jsonify({"error": result.get("errorCode", "failed")}), 400

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
