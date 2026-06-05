from flask import Flask, request, jsonify
import requests
import time
import os

app = Flask(__name__)

API_KEY = os.getenv("CAPSOLVER_KEY") or "CAP-308921334338B7605DD7406889B147F7"

@app.route('/createTask', methods=['POST', 'GET'])
def create_task():
    try:
        data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict()

        payload = {
            "clientKey": API_KEY,
            "task": {
                "type": "FunCaptchaTask",
                "websiteURL": data.get("websiteURL") or "https://www.roblox.com",
                "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
                "websiteSubdomain": "roblox-api.arkoselabs.com"
            }
        }

        if data.get("proxy"):
            payload["task"]["proxy"] = data.get("proxy")

        # Create Task
        r = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=30)
        create = r.json()

        if create.get("errorId") != 0:
            return jsonify({"error": create.get("errorCode", "error")}), 400

        task_id = create.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id"}), 400

        # Polling
        for _ in range(120):
            time.sleep(0.7)
            result = requests.post("https://api.capsolver.com/getTaskResult", 
                                 json={"clientKey": API_KEY, "taskId": task_id}, timeout=20).json()
            
            if result.get("status") == "ready":
                return jsonify({"success": True, "solution": result.get("solution")})
            
            if result.get("errorId") != 0:
                return jsonify({"error": "solve_failed"}), 400

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "✅ CapSolver Wrapper Online"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
