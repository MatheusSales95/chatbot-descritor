import numpy as np
from src.engine.w2v_loader import W2VLoader
from src.pipeline.preprocessor import Preprocessor


class SemanticSearch:
    def __init__(self):
        """
        Inicializa os componentes de NLP.
        """
        # Carregador de Vetores (Word2Vec)
        self.w2v_loader = W2VLoader()

        # Pré-processador (Limpeza de texto)
        self.preprocessor = Preprocessor()

    def vectorize(self, text: str) -> np.ndarray:
        """
        Transforma um texto (frase) em um vetor numérico (média dos vetores das palavras).
        Retorna None se não conseguir vetorizar nenhuma palavra.
        """
        if not text:
            return None

        # 1. Tokeniza e limpa o texto
        tokens = self.preprocessor.tokenize(text)

        # 2. Busca os vetores de cada palavra
        word_vectors = []
        for token in tokens:
            vec = self.w2v_loader.get_vector(token)
            if vec is not None:
                word_vectors.append(vec)

        # 3. Calcula a média (centróide) da frase
        if not word_vectors:
            return None

        # Retorna a média dos vetores (axis=0 achata a lista num único vetor de 300 dim)
        return np.mean(word_vectors, axis=0)
