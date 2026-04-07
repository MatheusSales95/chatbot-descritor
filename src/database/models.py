# src/database/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Interval
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

# --- 1. TABELAS AUXILIARES ---


class Regiao(Base):
    __tablename__ = 'regiao'
    __table_args__ = {"schema": "evento_fogo"}
    id_regiao = Column(Integer, primary_key=True)
    nome_regiao = Column(String)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326))


class Satelite(Base):
    __tablename__ = 'satelite'
    __table_args__ = {"schema": "evento_fogo"}
    sat_nome = Column(String, primary_key=True)

# --- 2. TABELAS DE EVENTOS ---


class EventoFogo(Base):
    __tablename__ = 'evento_fogo'
    __table_args__ = {"schema": "evento_fogo"}

    # Chave Primária
    id_evento = Column(Integer, primary_key=True)

    qtd_frente = Column(Integer)
    duracao = Column(Interval)
    data_min = Column(DateTime)
    data_max = Column(DateTime)
    max_frp = Column(Float)
    risco_medio = Column(Float)
    max_dias_sem_chuva = Column(Integer)
    area_acm = Column(Float)

    geom = Column(Geometry('MULTIPOLYGON', srid=4326))

    # Chaves Estrangeiras
    id_status = Column(Integer)
    id_tipo = Column(Integer)


class FrenteFogo(Base):
    """Tabela com a geometria diária/horária do fogo"""
    __tablename__ = 'frente_fogo'
    __table_args__ = {"schema": "evento_fogo"}

    id_frente = Column(Integer, primary_key=True)
    qtd_focos = Column(Integer)
    data_frente = Column(DateTime)
    id_evento = Column(Integer, ForeignKey(
        "evento_fogo.evento_fogo.id_evento"))
    geom = Column(Geometry('MULTIPOLYGON', srid=4326))


class EventoRegiao(Base):
    __tablename__ = 'evento_regiao'
    __table_args__ = {"schema": "evento_fogo"}
    id_evento = Column(Integer, ForeignKey(
        "evento_fogo.evento_fogo.id_evento"), primary_key=True)
    id_regiao = Column(Integer, ForeignKey(
        "evento_fogo.regiao.id_regiao"), primary_key=True)


class FocosBDQ(Base):
    __tablename__ = 'focos_bdq_c2'
    __table_args__ = {"schema": "evento_fogo"}
    id_foco_bdq = Column(Integer, primary_key=True)
    data_hora_gmt = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    satelite = Column(String)
    pais = Column(String)
    estado = Column(String)
    municipio = Column(String)
    bioma = Column(String)
    geom = Column(Geometry('POINT', srid=4326))
