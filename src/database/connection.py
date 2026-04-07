import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings


def get_engine():
    db_conf = settings.database

    # Formato: postgresql+psycopg2://user:pass@host:port/dbname
    DATABASE_URL = f"postgresql+psycopg2://{db_conf['user']}:{db_conf['password']}@{db_conf['host']}:{db_conf.get('port', 5432)}/{db_conf['name']}"

    # Configura o search_path para incluir seus schemas (evento_fogo, public, etc.) Isso permite que o banco encontre as tabelas automaticamente.
    schemas = ",".join(db_conf.get('schemas', ['public']))

    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        # Comando para PostgreSQL com múltiplos schemas:
        connect_args={'options': f'-c search_path={schemas}'}
    )
    return engine


# Cria a engine global
engine = get_engine()

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    # Dependência para injetar a sessão do banco nas rotas da API.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
