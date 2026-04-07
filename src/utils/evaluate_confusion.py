import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from src.engine.intent_classifier import IntentClassifier


def generate_confusion_matrix():
    print("Iniciando Avaliação do Modelo (Matriz de Confusão)...")

    # 1. Carregar o Classificador (Já treinado)
    classifier = IntentClassifier()

    # 2. Carregar os Dados de Gabarito (Ground Truth)
    data_path = "data/raw/intents_list.json"
    if not os.path.exists(data_path):
        print(f"Arquivo não encontrado: {data_path}")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    y_true = []  # A intenção real (Gabarito)
    y_pred = []  # A intenção que o robô chutou

    print("Testando cada frase do dataset...")

    # 3. Loop de Teste
    total_frases = 0
    for intent_obj in data['intents']:
        real_label = intent_obj['intent']

        for example in intent_obj['examples']:
            # Pede para o robô classificar
            prediction = classifier.classify(example)
            predicted_label = prediction['intent']

            y_true.append(real_label)
            y_pred.append(predicted_label)
            total_frases += 1

    # 4. Preparar Rótulos (Labels)
    # Pega todas as intenções únicas + 'fallback' caso tenha ocorrido
    labels = sorted(list(set(y_true + y_pred)))

    # 5. Gerar Matriz Numérica
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    # 6. Gerar Relatório de Texto (Precisão, Recall, F1)
    print("\n" + "="*60)
    print("RESUMO ESTATÍSTICO:")
    print("="*60)
    # zero_division=0 evita erro se alguma classe nunca for predita
    print(classification_report(y_true, y_pred, labels=labels, zero_division=0))

    # 7. Plotar Gráfico (Heatmap)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        xticklabels=labels,
        yticklabels=labels,
        cmap='Blues'
    )

    plt.title('Matriz de Confusão: Intenções Reais vs Preditas')
    plt.ylabel('Verdadeiro')
    plt.xlabel('Predito')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Salvar
    output_file = "matriz_confusao.png"
    plt.savefig(output_file, dpi=300)
    print(f"\nGráfico salvo em: {output_file}")
    print("   Abra a imagem para ver onde estão os erros.")


if __name__ == "__main__":
    generate_confusion_matrix()
