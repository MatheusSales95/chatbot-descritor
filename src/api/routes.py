from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.engine.bot_manager import BotManager

router = APIRouter()

# Modelos de Entrada/Saída


class ChatRequest(BaseModel):
    text: str


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(msg: ChatRequest):

    # Endpoint principal do Chatbot.

    try:
        # Inicializa sem argumentos
        manager = BotManager()

        # Processa a mensagem (retorna um dict)
        result = manager.process_message(msg.text)

        return ChatResponse(
            response=result['response'],
            intent=result['intent'],
            confidence=result['confidence']
        )

    except Exception as e:
        print(f"ERRO API: {e}")
        raise HTTPException(status_code=500, detail=str(e))
