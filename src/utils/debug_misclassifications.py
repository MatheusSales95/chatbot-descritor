import json
import os
from collections import defaultdict
from src.engine.intent_classifier import IntentClassifier


def debug_errors():
    print("Iniciando Investigação de Erros (Debug da Matriz)...")
    print("-" * 60)

    # 1. Carregar Cérebro
    classifier = IntentClassifier()

    # 2. Carregar Gabarito
    data_path = "data/raw/intents_list.json"
    if not os.path.exists(data_path):
        print("Arquivo de treino não encontrado.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Dicionário para agrupar erros por "Quadrado da Matriz"
    # Chave: (Real, Predito) -> Valor: Lista de frases
    confusion_details = defaultdict(list)
    total_errors = 0
    total_tested = 0

    # 3. Testar cada frase
    for intent_obj in data['intents']:
        real_label = intent_obj['intent']

        for phrase in intent_obj['examples']:
            total_tested += 1

            # Classifica
            result = classifier.classify(phrase)
            pred_label = result['intent']
            confidence = result['confidence']

            # Se errou (Real diferente do Predito), guarda o detalhe
            if real_label != pred_label:
                key = (real_label, pred_label)
                # Guarda a frase e a confiança com que ele errou
                confusion_details[key].append((phrase, confidence))
                total_errors += 1

    # 4. Imprimir Relatório Detalhado
    if total_errors == 0:
        print("\nPARABÉNS! O modelo acertou 100% das frases de treino.")
        print("   A matriz de confusão é uma diagonal perfeita.")
    else:
        print(
            f"\nForam encontrados {total_errors} erros em {total_tested} frases.\n")

        for (real, pred), errors in confusion_details.items():
            print(
                f"🟥 QUADRADO ERRADO: Era '{real.upper()}' -> Robô disse '{pred.upper()}'")
            print(f"   Quantidade de erros: {len(errors)}")
            print("   Frases culpadas:")
            for phrase, conf in errors:
                print(f"    • \"{phrase}\" (Confiança do erro: {conf:.2f})")
            print("-" * 60)


if __name__ == "__main__":
    debug_errors()
