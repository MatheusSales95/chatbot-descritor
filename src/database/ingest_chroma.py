import chromadb
import json
import os


def setup_chroma():
    # 1. Configura os caminhos
    base_dir = os.path.dirname(os.path.dirname(
        os.path.dirname(__file__)))  # Sobe 3 níveis até a raiz
    db_path = os.path.join(base_dir, "data", "chroma_db")
    jsonl_path = os.path.join(base_dir, "data", "raw", "training_data.jsonl")

    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)

    # 2. Cria ou pega a coleção
    collection = client.get_or_create_collection(
        name="sql_examples",
        metadata={"hnsw:space": "cosine"}
    )

    # 3. Lê o arquivo JSONL
    perguntas = []
    sqls = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    perguntas.append(item["instruction"])
                    # Salva a instrução, o contexto e o SQL esperado nos metadados
                    sqls.append({
                        "sql": item["response"],
                        "contexto": item.get("context", "")
                    })
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {jsonl_path}")
        return

    ids = [f"query_{i}" for i in range(len(perguntas))]

    # 4. Inserindo no Banco Vetorial
    print(
        f"Lendo {len(perguntas)} exemplos do JSONL e salvando no ChromaDB...")
    collection.upsert(
        documents=perguntas,
        metadatas=sqls,
        ids=ids
    )

    print(
        f"Sucesso! {collection.count()} exemplos SQL foram indexados no ChromaDB.")


if __name__ == "__main__":
    setup_chroma()
