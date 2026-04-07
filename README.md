#  Descritor teste

**Sistema de Recuperação de Dados de Eventos de Fogo utilizando Processamento de Linguagem Natural (PLN)**

##  Sobre o Projeto
O **DescrEVE Fogo** é um assistente virtual (chatbot) desenvolvido para otimizar a recuperação de informações geoespaciais sobre eventos de queimadas. O sistema recebe consultas em texto livre (linguagem natural) e devolve respostas claras e estruturadas, convertendo a intenção do usuário em comandos SQL direcionados a um banco de dados PostGIS. 

Este projeto visa eliminar barreiras técnicas na consulta de dados complexos, servindo como um Sistema de Apoio à Decisão ágil e seguro para a gestão ambiental e ações operacionais.

---

##  Arquitetura e Tecnologias
O projeto fundamenta-se em um *pipeline* de PLN clássico focado na arquitetura Text-to-SQL:
* **Motor NLP Híbrido (Dual-Embedding):** Word2Vec customizado (treinado em corpus de queimadas) + Word2Vec NILC (fallback geral).
* **Extração de Entidades:** Spacy (`pt_core_news_lg`) e expressões regulares.
* **Classificação de Intenções:** Similaridade de Cosseno com trava de segurança (*threshold*).
* **Banco de Dados:** PostgreSQL 17-3.5 com extensão PostGIS.
* **Backend / API:** FastAPI + Uvicorn.
* **Interface:** Streamlit.

---

##  Pré-requisitos
Certifique-se de ter instalado em sua máquina:
* **Docker** e **Docker Compose**
* **Python 3.8+**
* (Recomendado) Ambiente virtual (venv/conda)

---

##  Inicialização e Execução

O projeto é orquestrado através do Docker para o banco de dados e pode ter a API rodando em contêiner ou localmente.

### 1. Subindo o Banco de Dados (PostGIS)
O banco de dados é configurado via Docker Compose, rodando na porta `5433` (mapeada para a 5432 interna). O arquivo espera um dump de backup em `./data/raw/backup.dump` para restauração inicial.

Para inicializar apenas o banco de dados em segundo plano, execute:
```bash
sudo docker compose up -d db
```
## 2. Executando a API (Backend)

Você pode subir a API de duas formas:

### Opção A: Via Docker
Para subir todo o ambiente (Banco + API), execute:

```bash
docker compose up -d
```

**Opção B: Localmente via Uvicorn (Modo Desenvolvimento)**
Caso queira rodar localmente com hot-reload ativo:

```bash
uvicorn src.api.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000
```

### 3. Executando o Dashboard (Interface Visual)
Para iniciar a interface de chat desenvolvida em Streamlit, abra um novo terminal e execute:

```bash
streamlit run dashboard.py
```

###  Comandos Úteis
Abaixo estão os comandos necessários para treinar o modelo, realizar testes e gerar visualizações:

**Treinamento do Modelo NLP:**
```bash
python -m src.pipeline.train_word2vec
```
##  Testes do Sistema

Para rodar os testes, execute os seguintes comandos no terminal:

```bash
python test_db.py
python test_search.py
```

## Geração de Gráficos e Visualizações

Você pode gerar as visualizações dos dados de intenções utilizando os módulos abaixo:

```bash
# Visualizar o dendrograma das intenções
python -m src.pipeline.visualize_dendrogram

# Visualizar a matriz/distribuição de intenções
python -m data.models.visualize_intents
```

##  Acesso aos Serviços

Após a inicialização, os serviços estarão disponíveis nos seguintes endereços:

* **Documentação da API (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Endpoint Principal de Chat:** [Acessar Rota](http://localhost:8000/docs#/default/chat_endpoint_api_v1_chat_post)
* **Dashboard (Streamlit):** Geralmente acessível em [http://localhost:8501](http://localhost:8501) *(ou a porta indicada no terminal após o comando `run`)*.

###  Banco de Dados

* **Host:** `localhost` *(ou `db` via docker network)*
* **Porta:** `5433` (Externa) / `5432` (Interna)
