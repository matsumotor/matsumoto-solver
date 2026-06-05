from flask import Flask, request, jsonify
import requests
import time
import os
import traceback

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY")

print("🔑 Key carregada:", API_KEY[:15] + "..." if API_KEY and len(API_KEY) > 10 else "SEM KEY!")

@app.route('/')
def home():
    return "✅ MatsumotoSolver Online v2 - Use /createTask"

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    print("🔥 [REQUEST] Yummy chamou o solver")
    
    try:
        # Pegar dados
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        print(f"📨 Dados: {data}")

        if not API_KEY or len(API_KEY) < 10:
            return jsonify({"error": "invalid_or_missing_api_key"}), 400

        # Task
        task = {
            "type": "FunCaptchaTask",
            "websiteURL": data.get("websiteURL") or "https://www.roblox.com",
            "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
            "websiteSubdomain": "roblox-api.arkoselabs.com"
        }

        if data.get("proxy"):
            task["proxy"] = data.get("proxy")

        payload = {"clientKey": API_KEY, "task": task}

        # Create Task
        resp = requests.post("https://api.funbypass.com/createTask", json=payload, timeout=25)
        print(f"FunBypass Status: {resp.status_code}")

        create_data = resp.json()

        if create_data.get("errorId") != 0:
            err = create_data.get("errorCode") or str(create_data)
            print(f"❌ FunBypass Error: {err}")
            return jsonify({"error": err}), 400

        task_id = create_data.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id"}), 400

        print(f"✅ Task criada: {task_id} - Polling...")

        # Polling
        for i in range(140):
            result = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20).json()
            
            if result.get("status") == "ready":
                print("🎉 CAPTCHA RESOLVIDO COM SUCESSO!")
                return jsonify({"success": True, "solution": {"token": result["solution"]["token"]}})

            if result.get("errorId", 0) != 0:
                return jsonify({"error": result.get("errorCode", "solve_failed")}), 400

            if i % 25 == 0:
                print(f"⏳ Aguardando solução... ({i*0.65:.0f}s)")
            time.sleep(0.65)

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        print(f"💥 ERRO INTERNO: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "internal_server_error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 MatsumotoSolver v2 rodando")
    app.run(host="0.0.0.0", port=port)
