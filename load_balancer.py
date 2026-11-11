from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json
import itertools
import threading
import time

SERVERS = [
    {"url": "http://127.0.0.1:8001", "port": 8001, "conexoes": 0, "ativo": True},
    {"url": "http://127.0.0.1:8002", "port": 8002, "conexoes": 0, "ativo": True},
    {"url": "http://127.0.0.1:8003", "port": 8003, "conexoes": 0, "ativo": True},
]

# Algoritmo 1: Round Robin
current_index = 0

def escolher_servidor_round_robin():
    global current_index
    ativos = [s for s in SERVERS if s["ativo"]]
    if not ativos:
        return None
    
    # Garante que o índice não estoure o tamanho da lista de ativos
    if current_index >= len(ativos):
        current_index = 0
        
    servidor = ativos[current_index]
    current_index = (current_index + 1) % len(ativos)
    return servidor

# Algoritmo 2: Least Connections
def escolher_servidor_least_connections():
    ativos = [s for s in SERVERS if s["ativo"]]
    if not ativos:
        return None
    return min(ativos, key=lambda s: s["conexoes"])

# Health Check
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

threading.Thread(target=monitorar_servidores, daemon=True).start()

class LoadBalancerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        servidor = escolher_servidor_round_robin()
        
        if not servidor:
            self.send_response(503)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"erro": "Todos os servidores estao fora do ar!"}).encode("utf-8"))
            return

        servidor["conexoes"] += 1
        try:
            resposta = requests.get(servidor["url"] + self.path, timeout=2.0)
            
            self.send_response(resposta.status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(resposta.content)
        except requests.exceptions.RequestException:
            servidor["ativo"] = False
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