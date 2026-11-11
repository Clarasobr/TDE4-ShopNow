import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Porta recebida por argumento (ex: python server.py 8001)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

class ShopNowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "port": PORT}).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            resposta = {
                "mensagem": "Bem-vindo à ShopNow (Black Friday)",
                "servidor_porta": PORT
            }
            self.wfile.write(json.dumps(resposta).encode("utf-8"))

def run():
    servidor = HTTPServer(("127.0.0.1", PORT), ShopNowHandler)
    print(f"[Servidor ShopNow] Rodando na porta {PORT}...")
    servidor.serve_forever()

if __name__ == "__main__":
    run()