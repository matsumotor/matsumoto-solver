from flask import Flask, request, jsonify
import requests
import time
import os

app = Flask(__name__)

API_KEY = os.getenv("FUNBYPASS_KEY")

print("🔑 FUNBYPASS_KEY carregada:", 
      API_KEY[:10] + "..." + API_KEY[-6:] if API_KEY else "NENHUMA KEY!")

if not API_KEY or API_KEY == "FUN-sua_chave_aqui":
    print("❌ ERRO: FUNBYPASS_KEY não configurada!")

@app.route('/createTask', methods=['GET', 'POST'])
def create_task():
    print("🔥 REQUEST RECEBIDA - 404 resolvido!")
    
    try:
        # Captura os dados enviados pelo Yummy
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
        else:
            data = request.args.to_dict()

        print(f"Dados recebidos: {data}")

        # Monta a task
        task = {
            "type": "FunCaptchaTask",
            "websiteURL": data.get("websiteURL") or "https://www.roblox.com",
            "websitePublicKey": data.get("websitePublicKey") or "476068BF-9607-4799-B53D-966BE98E2B81",
            "websiteSubdomain": "roblox-api.arkoselabs.com"
        }

        if data.get("proxy"):
            task["proxy"] = data.get("proxy")

        payload = {
            "clientKey": API_KEY,
            "task": task
        }

        # Chama FunBypass
        resp = requests.post("https://api.funbypass.com/createTask", json=payload, timeout=30)
        create_data = resp.json()

        if create_data.get("errorId") != 0:
            return jsonify({"error": create_data.get("errorCode", "create_error")}), 400

        task_id = create_data["taskId"]

        # Polling
        for _ in range(130):
            result = requests.get(f"https://api.funbypass.com/getTaskResult/{task_id}", timeout=20).json()
            
            if result.get("status") == "ready":
                return jsonify({
                    "success": True,
                    "solution": {"token": result["solution"]["token"]}
                })
            
            if result.get("errorId", 0) != 0:
                return jsonify({"error": result.get("errorCode", "solve_error")}), 400
                
            time.sleep(0.65)

        return jsonify({"error": "timeout"}), 408

    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Rota de teste
@app.route('/')
def home():
    return "✅ MatsumotoSolver está online! Use /createTask"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
