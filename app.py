from flask import Flask, request, jsonify
import requests
import time
import os
import traceback

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY")

print("🔑 Key:", API_KEY[:15] + "..." if API_KEY else "SEM KEY")

@app.route('/')
def home():
    return "✅ MatsumotoSolver Online v3 - Use /createTask"

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    print("🔥 [REQUEST RECEBIDA DO YUMMY]")
    
    try:
        # Dados do Yummy
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        print(f"📨 Dados recebidos: {data}")

        if not API_KEY or len(API_KEY) < 15:
            return jsonify({"error": "missing_or_invalid_funbypass_key"}), 400

        task = {
            "type": "FunCaptchaTask",
            "websiteURL": data.get("websiteURL") or "https://www.roblox.com",
            "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
            "websiteSubdomain": "roblox-api.arkoselabs.com"
        }

        if data.get("proxy"):
            task["proxy"] = data.get("proxy")

        payload = {"clientKey": API_KEY, "task": task}

        print("📤 Enviando para FunBypass...")
        resp = requests.post("https://api.funbypass.com/createTask", json=payload, timeout=30)
        
        print(f"Status Code: {resp.status_code} | Response: {resp.text[:400]}")

        try:
            create_data = resp.json()
        except:
            return jsonify({"error": "funbypass_returned_invalid_json"}), 500

        if create_data.get("errorId") != 0:
            err = create_data.get("errorCode") or create_data.get("error") or str(create_data)
            print(f"❌ FunBypass Error: {err}")
            return jsonify({"error": err}), 400

        task_id = create_data.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id_received"}), 400

        print(f"✅ Task ID: {task_id} - Iniciando polling")

        for i in range(140):
            try:
                result = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20).json()
                
                if result.get("status") == "ready":
                    print("🎉 CAPTCHA RESOLVIDO!")
                    return jsonify({"success": True, "solution": {"token": result["solution"]["token"]}})
                
                if result.get("errorId", 0) != 0:
                    return jsonify({"error": result.get("errorCode", "solve_error")}), 400

            except:
                pass

            if i % 20 == 0:
                print(f"⏳ Aguardando... ({i*0.65:.0f}s)")
            time.sleep(0.65)

        return jsonify({"error": "timeout"}), 
