from flask import Flask, request, jsonify
import requests
import time
import os
import traceback

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY")

print("🔑 Key carregada:", API_KEY[:15] + "..." if API_KEY else "NENHUMA KEY")

@app.route('/')
def home():
    return "✅ MatsumotoSolver Online! Use /createTask"

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    print("🔥 [NEW REQUEST] Third-party solver chamado")
    
    try:
        # Captura dados
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        print(f"📨 Dados do Yummy: {data}")

        if not API_KEY or "FUN-" not in API_KEY:
            return jsonify({"error": "invalid_api_key"}), 400

        task = {
            "type": "FunCaptchaTask",
            "websiteURL": data.get("websiteURL") or "https://www.roblox.com",
            "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
            "websiteSubdomain": "roblox-api.arkoselabs.com"
        }

        if data.get("proxy"):
            task["proxy"] = data.get("proxy")

        payload = {"clientKey": API_KEY, "task": task}

        # Chamada para FunBypass com tratamento
        resp = requests.post("https://api.funbypass.com/createTask", json=payload, timeout=30)
        print(f"Status FunBypass Create: {resp.status_code}")

        try:
            create_data = resp.json()
        except:
            print("❌ Resposta createTask não é JSON:", resp.text[:300])
            return jsonify({"error": "bad_response_from_funbypass"}), 500

        print(f"Create Response: {create_data}")

        if create_data.get("errorId") != 0:
            err = create_data.get("errorCode") or create_data.get("error") or "unknown"
            return jsonify({"error": err}), 400

        task_id = create_data.get("taskId")
        if not task_id:
            return jsonify({"error": "no_task_id"}), 400

        # Polling
        for i in range(140):
            try:
                result_resp = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20)
                result = result_resp.json()
            except:
                time.sleep(0.7)
                continue

            if result.get("status") == "ready":
                print("✅ CAPTCHA RESOLVIDO!")
                return jsonify({"success": True, "solution": {"token": result["solution"]["token"]}})

            if result.get("errorId", 0) != 0:
                return jsonify({"error": result.get("errorCode", "solve_failed")}), 400

            if i % 25 == 0:
                print(f"⏳ Aguardando... ({i*0.65:.0f}s)")
            time.sleep(0.65)

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        error_msg = str(e)
        print(f"💥 ERRO CRÍTICO: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"error": error_msg}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 MatsumotoSolver rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
