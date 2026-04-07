import logging
import os
import multiprocessing
from gensim.models import Word2Vec
from src.config import settings
from src.pipeline.preprocessor import Preprocessor

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Word2VecTrainer:
    def __init__(self):
        self.conf = settings.nlp.get('word2vec', {})
        self.model_dir = settings.nlp.get('model_path', 'data/models/')
        self.model_name = "descrEVE_w2v.model"
        self.preprocessor = Preprocessor()
        os.makedirs(self.model_dir, exist_ok=True)

    def load_corpus_txt(self, file_path: str):
        sentences = []

        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return []

        print(f"Lendo corpus: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Usa o MESMO tokenizador que o bot usa na hora de conversar
                    tokens = self.preprocessor.tokenize(line)
                    if tokens:
                        sentences.append(tokens)

            print(
                f"Processamento concluído: {len(sentences)} frases extraídas.")
            return sentences

        except Exception as e:
            print(f"Erro ao ler corpus: {e}")
            return []

    def train(self, corpus_path: str):
        sentences = self.load_corpus_txt(corpus_path)

        if not sentences:
            print("Sem dados válidos para treinar. Verifique o arquivo .txt.")
            return

        print("Iniciando treinamento Word2Vec Especializado...")

        cores = multiprocessing.cpu_count()

        # Configuração do Modelo
        model = Word2Vec(
            sentences=sentences,
            vector_size=self.conf.get('vector_size', 300),
            window=self.conf.get('window', 5),
            min_count=self.conf.get('min_count', 2),
            workers=cores,
            epochs=self.conf.get('epochs', 30)
        )

        output_path = os.path.join(self.model_dir, self.model_name)
        model.save(output_path)
        print(f"Modelo salvo com sucesso em: {output_path}")
        print(
            f"Vocabulário aprendido: {len(model.wv.index_to_key)} palavras únicas.")


if __name__ == "__main__":
    # Define o caminho do corpus novo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    corpus_path = os.path.join(
        current_dir, '..', '..', 'data', 'raw', 'corpus_queimadas_completo.txt')
    corpus_path = os.path.normpath(corpus_path)

    trainer = Word2VecTrainer()
    trainer.train(corpus_path)
