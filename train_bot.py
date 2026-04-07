from src.engine.intent_classifier import IntentClassifier
import sys
import os


sys.path.append(os.getcwd())


def main():
    print("Iniciando Script de Treinamento Manual")
    print("-" * 40)

    # Inicializa em modo de treino (carrega tudo)
    classifier = IntentClassifier(run_mode="train")

    # Executa o treinamento e salva o arquivo .pkl
    classifier.train_and_save()

    print("-" * 40)
    print("Treinamento concluído! Agora você pode rodar a API ou o Jupyter.")


if __name__ == "__main__":
    main()
