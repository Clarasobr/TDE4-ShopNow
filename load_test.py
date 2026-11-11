import concurrent.futures
import requests
import time

URL = "http://127.0.0.1:8000/"
TOTAL_REQUISICOES = 100
CONCORRENCIA = 10

def fazer_requisicao(i):
    inicio = time.time()
    try:
        res = requests.get(URL, timeout=3.0)
        duracao = time.time() - inicio
        porta = res.json().get("servidor_porta")
        return res.status_code, porta, duracao
    except Exception as e:
        return 500, None, 0

print(f"Iniciando teste de carga na ShopNow: {TOTAL_REQUISICOES} requisicoes...")
inicio_total = time.time()

sucessos = 0
distribuicao = {}

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCORRENCIA) as executor:
    resultados = list(executor.map(fazer_requisicao, range(TOTAL_REQUISICOES)))

tempo_total = time.time() - inicio_total

for status, porta, _ in resultados:
    if status == 200:
        sucessos += 1
        if porta:
            distribuicao[porta] = distribuicao.get(porta, 0) + 1

print("\n=== RESULTADO DO TESTE DE CARGA ===")
print(f"Tempo total: {tempo_total:.2f} segundos")
print(f"Requisições com sucesso: {sucessos}/{TOTAL_REQUISICOES}")
print(f"Taxa (RPS): {TOTAL_REQUISICOES / tempo_total:.2f} req/s")
print(f"Como o balanceador dividiu o trafego entre os servidores: {distribuicao}")
print("===================================\n")