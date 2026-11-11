# ShopNow - Balanceador de Carga para E-Commerce

Este projeto consiste em uma solução de infraestrutura e balanceamento de carga para a startup de e-commerce ShopNow. O objetivo do sistema é suportar altos volumes de acessos simultâneos (como em promoções de Black Friday), distribuindo o tráfego entre múltiplas instâncias de backend e garantindo alta disponibilidade.

## Arquitetura do Sistema

A arquitetura é composta por 3 servidores rodando em portas distintas e 1 balanceador de carga atuando como porta de entrada.

- Balanceador de Carga (load_balancer.py): Escuta na porta 8000. Recebe as requisições HTTP do cliente e as repassa para os servidores ativos.

- Instâncias Backend (server.py): Escutam nas portas 8001, 8002 e 8003. Processam as requisições e respondem com payload JSON.

##  Funcionalidades Implementadas

1 - Múltiplas Instâncias de Backend: Capacidade de subir $N$ instâncias independentes da aplicação ShopNow.

2 - Algoritmos de Balanceamento de Carga: 
- Round Robin: Distribuição circular alternada entre as instâncias disponíveis.

- Least Connections: Redirecionamento da requisição para o servidor que possui o menor número de conexões ativas no momento.

3 - Health Check e Failover Ativo:
- Uma thread em segundo plano realiza verificações de saúde (Health Check) a cada 3 segundos na rota /health de cada servidor.

- Em caso de queda abrupta de um servidor, ele é marcado automaticamente como inativo, e as novas requisições são redirecionadas instantaneamente para as instâncias remanescentes.

- Mecanismo de Retry em caso de falha durante o trânsito da requisição.

4 - Teste de Carga: 
- Integração com a ferramenta Apache Benchmark (ab) para medição de vazão (RPS) e latência.

## Como Executar o Projeto

### Pré-requisitos

Certifique-se de ter o Python instalado e instale a dependência de requisições HTTP:

- python -m pip install requests

Instalando o Apache Benchmark - ab no linux:

- sudo apt update && sudo apt install apache2-utils -y

### Passo 1: Iniciar os Servidores Backend

Abra 3 terminais separados na raiz do projeto e execute um comando em cada um:

- python server.py 8001
- python server.py 8002
- python server.py 8003

### Passo 2: Iniciar o Balanceador de Carga

Abra um quarto terminal e inicie o balanceador na porta 8000:

- python load_balancer.py

### Passo 3: Testar via Navegador

- Acesse http://localhost:8000/ no seu navegador. A cada atualização de página, o balanceador irá encaminhar sua requisição para uma das portas backend (8001, 8002 ou 8003).

## Testes de Carga e Tolerância a Falhas

### Executando o Apache Benchmark (ab)

Em um quinto terminal, execute o teste de estresse simulando 100 requisições com concorrência de 10 usuários simultâneos:

- ab -n 100 -c 10 http://localhost:8000/


### Métricas Avaliadas no Relatório:

- Requests per second (RPS): Quantidade de requisições atendidas por segundo.

- Failed requests: Quantidade de falhas (deve indicar 0 em condições normais).

- Time per request: Latência média da resposta em milissegundos.

### Demonstrando o Failover (Simulação de Quedas)

Com todos os servidores e o balanceador rodando, vá até o Terminal 1 (Porta 8001) e interrompa o processo pressionando Ctrl + C.

Execute novamente o Apache Benchmark:

- ab -n 100 -c 10 http://localhost:8000/


Resultado: O balanceador identificará a falha automaticamente e distribuirá 100% das requisições entre as portas 8002 e 8003, mantendo a aplicação 100% disponível (Failed requests: 0).


