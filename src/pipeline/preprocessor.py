import spacy
import re
from src.config import settings


class Preprocessor:
    def __init__(self):
        # Tenta pegar do settings, se não tiver usa o padrão
        try:
            model_name = settings.nlp.get('spacy_base', 'pt_core_news_lg')
        except (AttributeError, KeyError):
            model_name = 'pt_core_news_lg'

        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f" AVISO: Modelo '{model_name}' não encontrado.")
            print(f" Execute: python -m spacy download {model_name}")
            self.nlp = spacy.blank("pt")

        # 2. Configurações extras (.YAML)
        try:
            self.domain_stopwords = set(
                settings.nlp.get('domain_stopwords', []))
            self.synonyms = settings.nlp.get('synonyms', {})
        except (AttributeError, KeyError):
            self.domain_stopwords = set()
            self.synonyms = {}

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        # Apenas lowercase e strip. Mantém acentos e ç.
        text = text.lower().strip()
        return text

    def tokenize(self, text: str) -> list:
        if not text:
            return []

        clean_txt = self.clean_text(text)
        doc = self.nlp(clean_txt)

        tokens = []
        for token in doc:
            # 1. Filtros
            if token.is_punct or token.is_space or token.like_num:
                continue

            # Verifica stopwords
            if token.is_stop or token.text in self.domain_stopwords:
                continue

            # Usar o texto original minúsculo, não o lema
            # word = token.lemma
            word = token.text.lower()

            # 3. Sinônimos
            for key, values in self.synonyms.items():
                if word in values:
                    word = key
                    break

            tokens.append(word)

        return tokens
