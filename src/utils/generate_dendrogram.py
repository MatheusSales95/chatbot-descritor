import json
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from src.engine.w2v_loader import W2VLoader
from src.pipeline.preprocessor import Preprocessor


def generate_dendrogram():
    print("Iniciando Análise de Cluster (Dendrograma)...")

    # 1. Carregar Motores
    loader = W2VLoader()
    preprocessor = Preprocessor()

    if not loader.is_ready():
        print("Erro: Modelos W2V não carregados.")
        return

    # 2. Carregar Frases de Treino
    data_path = "data/raw/intents_list.json"
    if not os.path.exists(data_path):
        print(f"Arquivo não encontrado: {data_path}")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sentences = []
    labels = []
    vectors = []

    print("Vetorizando frases...")

    # 3. Processar cada frase
    for intent_obj in data['intents']:
        intent_name = intent_obj['intent']
        print(f"   Processando intenção: {intent_name}")

        for example in intent_obj['examples']:
            # Tokeniza (Limpeza igual ao do Bot)
            tokens = preprocessor.tokenize(example)

            if not tokens:
                continue

            # Vetoriza (Média dos vetores das palavras)
            word_vecs = [loader.get_vector(word) for word in tokens]
            if not word_vecs:
                continue

            sentence_vec = np.mean(word_vecs, axis=0)

            # Guarda para o gráfico
            vectors.append(sentence_vec)
            # Label ex: [RANKING] quais os menores...
            labels.append(f"[{intent_name.upper()[:4]}] {example}")

    # 4. Calcular Clusterização Hierárquica (Método de Ward)
    # Ward minimiza a variância dentro dos clusters
    X = np.array(vectors)
    linked = linkage(X, 'ward')

    # 5. Plotar
    plt.figure(figsize=(15, 12))  # Tamanho da imagem
    plt.title('Dendrograma Semântico das Intenções')
    plt.xlabel('Distância Semântica (Quanto maior a altura, mais diferente)')

    dendrogram(
        linked,
        orientation='right',  # Deitado para ler melhor
        labels=labels,
        distance_sort='descending',
        show_leaf_counts=True,
        leaf_font_size=10
    )

    plt.tight_layout()

    # Salvar em vez de mostrar (para funcionar no Docker/Servidor)
    output_file = "dendrograma_intencoes.png"
    plt.savefig(output_file, dpi=300)
    print(f"\nGráfico gerado com sucesso: {output_file}")
    print("   Abra este arquivo imagem para ver o agrupamento das frases.")


if __name__ == "__main__":
    generate_dendrogram()
