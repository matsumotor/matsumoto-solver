from flask import Flask, request, jsonify
import requests
import time
import os

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY")

@app.route('/')
def home():
    return "✅ MatsumotoSolver Online - v6"

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        task = {
            "type": "FunCaptchaTask",
            "websiteURL": data.get("websiteURL") or "https://www.roblox.com",
            "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
            "websiteSubdomain": "roblox-api.arkoselabs.com"
        }

        if data.get("proxy"):
            task["proxy"] = data.get("proxy")

        payload = {"clientKey": API_KEY, "task": task}

        resp = requests.post("https://api.funbypass.com/createTask", json=payload, timeout=30)
        create_data = resp.json()

        if create_data.get("errorId") != 0:
            return jsonify({"error": create_data.get("errorCode", "funbypass_error")}), 400

        task_id = create_data.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id"}), 400

        for _ in range(140):
            result = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20).json()
            if result.get("status") == "ready":
                return jsonify({"success": True, "solution": {"token": result["solution"]["token"]}})
            if result.get("errorId", 0) != 0:
                return jsonify({"error": "solve_failed"}), 400
            time.sleep(0.65)

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        return jsonify({"error": "internal_error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
