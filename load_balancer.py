from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json
import itertools
import threading
import time

# Nossos servidores backend disponíveis
SERVERS = [
    {"url": "http://127.0.0.1:8001", "port": 8001, "conexoes": 0},
    {"url": "http://127.0.0.1:8002", "port": 8002, "conexoes": 0},
    {"url": "http://127.0.0.1:8003", "port": 8003, "conexoes": 0},
]

# Algoritmo 1: Round Robin (iterador circular)
round_robin_iter = itertools.cycle(SERVERS)

def escolher_servidor_round_robin():
    return next(round_robin_iter)

# Algoritmo 2: Least Connections (menor número de conexões ativas)
def escolher_servidor_least_connections():
    return min(SERVERS, key=lambda s: s["conexoes"])

def monitorar_servidores():
    while True:
        for servidor in SERVERS:
            try:
                res = requests.get(f"{servidor['url']}/health", timeout=1.0)
                if res.status_code == 200:
                    servidor["ativo"] = True
                else:
                    servidor["ativo"] = False
            except:
                servidor["ativo"] = False
        time.sleep(3) # Checa a cada 3 segundos

# Inicia o monitoramento em background
threading.Thread(target=monitorar_servidores, daemon=True).start()

def escolher_servidor():
    # Pega apenas os servidores que estão ativos (tolerância a falhas)
    ativos = [s for s in SERVERS if s["ativo"]]
    if not ativos:
        return None
    # Algoritmo Least Connections entre os ativos
    return min(ativos, key=lambda s: s["conexoes"])

class LoadBalancerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        servidor = escolher_servidor_round_robin()
        
        servidor["conexoes"] += 1
        try:
            # Repassa a requisição para o servidor escolhido
            resposta = requests.get(servidor["url"] + self.path, timeout=2.0)
            
            self.send_response(resposta.status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(resposta.content)
        except requests.exceptions.RequestException:
            # Se o servidor falhou ao responder
            self.send_response(502)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"erro": f"Servidor da porta {servidor['port']} esta fora do ar!"}).encode("utf-8"))
        finally:
            servidor["conexoes"] -= 1

def run():
    servidor = HTTPServer(("127.0.0.1", 8000), LoadBalancerHandler)
    print("[Balanceador de Carga] Rodando na porta 8000...")
    servidor.serve_forever()

if __name__ == "__main__":
    run()