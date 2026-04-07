import os
import yaml
from dotenv import load_dotenv

# 1. Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Settings:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        # Caminho absoluto para o settings.yaml na raiz do projeto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(base_path, "settings.yaml")

        if not os.path.exists(settings_path):
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {settings_path}")

        with open(settings_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        # 2. Injeta as credenciais do .env nas configurações do banco
        db_conf = self._config.get('database', {})
        db_conf['user'] = os.getenv('DB_USER')
        db_conf['password'] = os.getenv('DB_PASSWORD')
        db_conf['host'] = os.getenv('DB_HOST')
        db_conf['name'] = os.getenv('DB_NAME')

        # Garante que leu as variáveis corretamente
        if not db_conf['password']:
            print("AVISO: Senha do banco não encontrada no .env")

    @property
    def database(self):
        return self._config.get('database', {})

    @property
    def nlp(self):
        return self._config.get('nlp', {})

    @property
    def app(self):
        return self._config.get('app', {})


settings = Settings()
