# Usa uma imagem leve do Python 3.10
FROM python:3.10-slim

# Instala dependências do sistema necessárias para compilar bibliotecas
# libpq-dev: necessário para psycopg2 (postgres)
# build-essential: compiladores gcc
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (para aproveitar cache do Docker)
COPY requirements.txt .

# Instala as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# Baixa o modelo do Spacy durante o build (evita baixar toda vez que inicia)
RUN python -m spacy download pt_core_news_lg

# Copia todo o código fonte para dentro do container
COPY . .

# Exponhe a porta 8000
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]