from flask import Flask, request, jsonify
import requests
import time
import os
import traceback

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY") or "FUN-sua_chave_aqui"

@app.route('/createTask', methods=['POST', 'GET'])
def create_task():
    try:
        print("🔥 [REQUEST RECEBIDA]")  # Log visível no Render
        
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        print(f"📨 Dados recebidos: {data}")

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
        create_data = resp.json()
        print(f"📥 Resposta createTask: {create_data}")

        if create_data.get("errorId") != 0:
            error_msg = create_data.get("errorCode") or create_data.get("error") or str(create_data)
            print(f"❌ Erro no createTask: {error_msg}")
            return jsonify({"error": error_msg}), 400

        task_id = create_data.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id"}), 400

        print(f"⏳ Task criada: {task_id} - Aguardando solução...")

        for attempt in range(130):
            result = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20).json()
            
            if result.get("status") == "ready":
                token = result["solution"]["token"]
                print("✅ CAPTCHA RESOLVIDO COM SUCESSO!")
                return jsonify({"success": True, "solution": {"token": token}})
            
            if result.get("errorId", 0) != 0:
                error = result.get("errorCode") or "unknown"
                print(f"❌ Erro no solve: {error}")
                return jsonify({"error": error}), 400
                
            if attempt % 20 == 0:
                print(f"   ⏳ Tentativa {attempt}...")
            time.sleep(0.65)

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"💥 ERRO INTERNO (HTTP 500): {str(e)}")
        print(error_trace)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 MatsumotoSolver iniciado na porta {port}")
    app.run(host="0.0.0.0", port=port)
