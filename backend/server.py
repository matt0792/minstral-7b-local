from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_cpp import Llama
import uvicorn
import json
import asyncio
from typing import List, Dict

class ChatRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]] = []
    temperature: float = 0.3
    max_tokens: int = 192
    system_prompt: str = """<<SYS>>
You are an expert Q&A assistant. Provide concise, factual answers.
Always ask relevant follow-up questions to continue the conversation.
<</SYS>>"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    llm = Llama(
        model_path="./model/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        n_gpu_layers=30,
        n_threads=6,
        n_batch=1024,
        n_ctx=2048,
        offload_kqv=True,
        mul_mat_q=True,
        verbose=False
    )
except Exception as e:
    print(f"MODEL LOADING ERROR: {str(e)}")
    raise RuntimeError("Failed to load model") from e

def format_history(history: List[Dict[str, str]]) -> str:
    conversation = []
    for msg in history:
        if msg["role"] == "user":
            conversation.append(f"[INST] {msg['content']} [/INST]")
        elif msg["role"] == "assistant":
            conversation.append(f"{msg['content']}</s>")
    return "\n".join(conversation)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        system_prompt = request.system_prompt
        history_str = format_history(request.history)
        
        formatted_prompt = f"""{system_prompt}
{history_str}
[INST] {request.prompt} [/INST]"""

        try:
            stream = llm(
                formatted_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_k=40,
                stop=["</s>", "[INST]"],
                repeat_penalty=1.15,
                mirostat_mode=2,
                mirostat_tau=5.0,
                mirostat_eta=0.1,
                stream=True
            )
        except Exception as e:
            raise HTTPException(500, f"Model generation error: {str(e)}")

        async def generate():
            full_response = ""
            try:
                for chunk in stream:
                    token = chunk["choices"][0]["text"]
                    full_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0.001)

                clean_response = full_response.split("[/INST]")[-1] \
                    .replace("<s>", "") \
                    .replace("</s>", "") \
                    .strip()
                
                updated_history = request.history + [
                    {"role": "user", "content": request.prompt},
                    {"role": "assistant", "content": clean_response}
                ]
                # Send final response and history update
                yield f"data: {json.dumps({'final': clean_response})}\n\n"
                yield f"data: {json.dumps({'history': updated_history[-4:]})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                raise

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        print(f"API ERROR: {str(e)}")
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")