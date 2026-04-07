import os
import json
import pickle
import numpy as np
from src.engine.semantic_search import SemanticSearch


class IntentClassifier:
    def __init__(self, run_mode="inference"):
        """
        run_mode: 'inference' (leve) ou 'train' (pesado)
        """
        self.run_mode = run_mode
        self.semantic_search = SemanticSearch()

        self.raw_path = "data/raw/intents_list.json"
        self.processed_path = "data/processed/trained_intents.pkl"
        self.trained_data = []

        if self.run_mode == "inference":
            self._load_trained_data()

    def _load_trained_data(self):
        if os.path.exists(self.processed_path):
            print(
                f" Carregando inteligência pré-treinada de: {self.processed_path}")
            with open(self.processed_path, "rb") as f:
                self.trained_data = pickle.load(f)
        else:
            print(" Nenhum treinamento encontrado. Execute 'python train_bot.py'.")
            self.trained_data = []

    def train_and_save(self):
        print("  Iniciando treinamento detalhado...")

        # Carrega W2V (Pesado) apenas agora
        loader = self.semantic_search.w2v_loader
        if not loader.is_ready():
            loader._load_model()

        with open(self.raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            intents_list = data["intents"]

        processed_list = []
        preprocessor = self.semantic_search.preprocessor

        for intent_obj in intents_list:
            intent_name = intent_obj['intent']
            print(f"      Processando: {intent_name}...")

            vectors_of_intent = []
            samples_detail = []  # <--- LISTA PARA O GRÁFICO

            for phrase in intent_obj['examples']:
                tokens = preprocessor.tokenize(phrase)
                word_vecs = [loader.get_vector(
                    t) for t in tokens if loader.get_vector(t) is not None]

                if word_vecs:
                    phrase_vec = np.mean(word_vecs, axis=0)
                    vectors_of_intent.append(phrase_vec)

                    # Guarda o detalhe para o gráfico depois
                    samples_detail.append({
                        "phrase": phrase,
                        "vector": phrase_vec
                    })

            if vectors_of_intent:
                centroid = np.mean(vectors_of_intent, axis=0)
                processed_list.append({
                    "intent": intent_name,
                    "centroid_vector": centroid,  # Usado pelo Chatbot
                    "samples": samples_detail    # Usado pelo Gráfico
                })

        with open(self.processed_path, "wb") as f:
            pickle.dump(processed_list, f)

        print(f"    Treinamento salvo com sucesso em: {self.processed_path}")
        self.trained_data = processed_list

    def classify(self, message: str) -> dict:
        if not self.trained_data:
            return {"intent": "fallback", "confidence": 0.0}

        user_vector = self.semantic_search.vectorize(message)
        if user_vector is None:
            return {"intent": "fallback", "confidence": 0.0}

        best_intent = "fallback"
        best_score = -1.0

        for item in self.trained_data:
            intent_vec = item['centroid_vector']
            score = np.dot(user_vector, intent_vec) / (
                np.linalg.norm(user_vector) * np.linalg.norm(intent_vec)
            )
            if score > best_score:
                best_score = score
                best_intent = item['intent']

        if best_score < 0.45:
            return {"intent": "fallback", "confidence": float(best_score)}

        return {"intent": best_intent, "confidence": float(best_score)}
