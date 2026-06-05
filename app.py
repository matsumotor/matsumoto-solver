from flask import Flask, request, jsonify
import requests
import time
import os

app = Flask(__name__)

API_KEY = os.getenv("CAPSOLVER_KEY") or "CAP-308921334338B7605DD7406889B147F7"

@app.route('/')
def home():
    return "✅ MatsumotoSolver (CapSolver) - v8 Online"

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    try:
        # Receber dados
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        print(f"[YUMMY REQUEST] Dados: {data}")

        payload = {
            "clientKey": API_KEY,
            "task": {
                "type": "FunCaptchaTask",
                "websiteURL": data.get("websiteURL") or "https://www.roblox.com/games/3475397644",
                "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
                "websiteSubdomain": "roblox-api.arkoselabs.com"
            }
        }

        if data.get("proxy"):
            payload["task"]["proxy"] = data.get("proxy")

        print(f"[SENDING TO CAPSOLVER] {payload}")

        # Create Task
        resp = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=30)
        print(f"CapSolver Status: {resp.status_code} | Response: {resp.text[:500]}")

        create_data = resp.json()

        if create_data.get("errorId") != 0:
            error = create_data.get("errorCode") or create_data.get("error") or str(create_data)
            print(f"❌ CapSolver Error: {error}")
            return jsonify({"error": error}), 400

        task_id = create_data.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id"}), 400

        # Polling
        for i in range(120):
            time.sleep(0.7)
            result = requests.post("https://api.capsolver.com/getTaskResult", 
                                 json={"clientKey": API_KEY, "taskId": task_id}, 
                                 timeout=20).json()

            if result.get("status") == "ready":
                print("🎉 CAPTCHA RESOLVIDO!")
                return jsonify({"success": True, "solution": result.get("solution")})

            if result.get("errorId") != 0:
                return jsonify({"error": result.get("errorCode", "solve_failed")}), 400

            if i % 20 == 0:
                print(f"⏳ Aguardando solução... ({i*0.7:.0f}s)")

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        print(f"💥 ERRO INTERNO: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
