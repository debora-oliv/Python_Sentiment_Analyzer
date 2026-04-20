# Sumário

- ### [Sobre o Projeto](#sobre-o-projeto)

- ### [Estrutura](#estrutura)

- ### [Serviços](#serviços)

- ### [Fluxo de Dados](#fluxo-de-dados)

- ### [Execução e Teste](#execução-e-teste)


# Sobre o Projeto

Este é um sistema distribuído de análise de sentimentos construído com uma arquitetura de microsserviços. O projeto utiliza **Python** e **FastAPI** para a camada de aplicação, **Redis** como intermediário de mensagens assíncronas e **PostgreSQL** para armazenamento persistente. O foco principal é demonstrar o uso de containers Docker para criar um ambiente de desenvolvimento isolado, escalável e resiliente.

# Estrutura
```
sentiment-analyzer/
├── api/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile            # Build da imagem da api
├── worker/
│   ├── worker.py
│   ├── requirements.txt
│   └── Dockerfile            # Build da imagem do worker
├── db/
│   └── init.sh               # Script de inicialização do Banco de Dados
├── docker-compose.yml        # Orquestração dos serviços: redis, db, worker, api
├── config.py                 # Configuração para leitura das variáveis de ambiente
└── .env.example              # Template de variáveis de ambiente
```
# Serviços

```redis```: Imagem oficial do Redis para atuar como broker de mensagens.

```db```: Imagem oficial PostgreSQL para persistência dos resultados.

```api```: App FastAPI com Dockerfile próprio que recebe um texto e o envia para uma fila (Redis).

```worker```: Script com Dockerfile próprio que consome as mensagens do Redis, processa o texto usando a biblioteca TextBlob e salva o resultado no banco de dados.

# Fluxo de Dados

O fluxo de uma informação dentro do sistema segue o seguinte caminho:

- **Ingestão:** A API recebe uma frase via requisição HTTP POST.

- **Mensageria:** A frase é encapsulada em um JSON e enviada para uma fila no Redis. A API responde imediatamente ao usuário, garantindo baixa latência.

- **Processamento:** O Worker (que pode ter múltiplas instâncias) monitora a fila constantemente. Ao detectar uma nova mensagem, ele a retira da fila e utiliza a biblioteca TextBlob para calcular a polaridade do texto.

- **Persistência:** O resultado da análise (texto, score e classificação) é gravado de forma estruturada no PostgreSQL.

- **Ciclo de Vida:** Graças aos volumes do Docker, os dados permanecem salvos mesmo que todos os containers sejam removidos.

# Execução e Teste

### Pré-requisitos
- Docker
- Docker Compose

## 1. Configurar variáveis de ambiente
```
cp .env.example .env
```
Lembre de atualizar o arquivo ```.env``` com valores coesos.

## 2. Subir aplicação
```
docker compose up --build
```
O Docker vai baixar as imagens (Python, Redis, Postgres), rodar os Dockerfiles, criar o volume postgres_data e executar o init.sql.

## 3. Testar aplicação
### 3.1 Testar pelo navegador
- Abra o navegador em ```http://localhost:8000/docs```.

- Clique no método **POST /analyze**, depois em **Try it out**.

- No corpo do JSON, digite algo como: ```{"content": "I love learning Docker and Python!"}```
  
- Clique em **Execute**.

- Vá para o terminal e confira os logs do worker:
  
  ```
  docker compose logs -f worker
  ```
### 3.2 Testar pelo terminal
- Abra o seu terminal (fora do container)
  
- Envie uma requisição do tipo **POST** para o endpoint **/analyze**, passando o conteúdo no formato JSON:
  
  ```
  curl -X POST http://localhost:8000/analyze \
       -H "Content-Type: application/json" \
       -d '{"content": "I love learning Docker and Python!"}'
  ```
- Confira os logs do worker:
  
  ```
  docker compose logs -f worker
  ```
  
## 4. Testar persistência
- Valide se os dados foram realmente salvos no volume do Postgres:
  
  ```
  docker exec -it sentiment_db psql -U [seu_usuario] -d [seu_banco_de_dados] -c "SELECT * FROM sentiments;
  ```
- Derrube a aplicação:
  
  ```
  docker compose down
  ```
- Suba a aplicação novamente:
  
  ```
  docker compose up -d
  ```
- Valide se os dados persistem no banco de dados:
  
  ```
  docker exec -it sentiment_db psql -U [seu_usuario] -d [seu_banco_de_dados] -c "SELECT * FROM sentiments;
  ```

## 5. Testar escalabilidade
- Suba múltiplas instâncias do Worker:
  
  ```
  docker compose up -d --scale worker=3
  ```
- Use um loop para enviar [10] requisições e ver os workers trabalhando juntos:
  
  ```
  for i in {1..10}; do
  curl -X POST http://localhost:8000/analyze \
       -H "Content-Type: application/json" \
       -d "{\"content\": \"Teste de carga número $i\"}";
  done
  ```
- Abra os logs do worker para ver a divisão de tarefas:
  
  ```
  docker compose logs -f worker
  ```
  

## 6. Testar Live Reload
- Acesse ```http://localhost:8000/``` no navegador.
  
- Com o container rodando, abra o arquivo ```api/main.py``` e altere a mensagem do endpoint raiz (/).

- Salve o arquivo e confira novamente ```http://localhost:8000/```.
