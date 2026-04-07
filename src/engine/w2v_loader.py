import os
import numpy as np
from gensim.models import KeyedVectors, Word2Vec
from src.config import settings


class W2VLoader:
    _instance = None
    _ready = False

    # Armazena os dois modelos
    custom_vectors = None
    nilc_vectors = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(W2VLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        try:
            model_path_config = settings.nlp.model_path
        except AttributeError:
            model_path_config = settings.nlp['model_path']

        model_dir = model_path_config
        custom_path = os.path.join(model_dir, "descrEVE_w2v.model")
        nilc_path = os.path.join(model_dir, "cbow_s300.txt")

        print(f"W2VLoader: Iniciando Arquitetura Híbrida...")

        # 1. Carrega CUSTOM
        if os.path.exists(custom_path):
            try:
                print(f"Carregando Especialista (Custom): {custom_path}")
                full_model = Word2Vec.load(custom_path)
                self.custom_vectors = full_model.wv
                del full_model
                print("Especialista pronto!")
            except Exception as e:
                print(f"Erro no Custom: {e}")

        # 2. Carrega NILC (Generalista)
        if os.path.exists(nilc_path):
            try:
                print(f"Carregando (NILC): {nilc_path}")
                print("Isso pode levar alguns segundos...")
                self.nilc_vectors = KeyedVectors.load_word2vec_format(
                    nilc_path)
                print("NILC pronto!")
            except Exception as e:
                print(f"Erro no NILC: {e}")

        if self.custom_vectors is not None or self.nilc_vectors is not None:
            self._ready = True
        else:
            print("CRÍTICO: Nenhum modelo foi carregado.")

    def get_vector(self, word: str):

        # 1. Busca no CUSTOM
        if self.custom_vectors and word in self.custom_vectors:
            return self.custom_vectors[word]

        # 2. Busca no NILC
        if self.nilc_vectors and word in self.nilc_vectors:
            return self.nilc_vectors[word]

        # 3. Retorna vetor vazio (300 dimensões)
        return np.zeros(300)

    def is_ready(self):
        return self._ready
