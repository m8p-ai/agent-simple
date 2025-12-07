from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from m8_client import M8
from typing import Any
import uuid
import os
from datetime import datetime

tms = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

app = FastAPI(
    title="M8P Vector Agent", 
    description="High-performance agent using M8P Hypervisor"
)

# --- Constants ---
AGENT_SESSION_ID = "sess-"+tms
VECTOR_DB_NAME = "AGENT_MEMORY"
EMBED_DIM = 188 # Adjust based on your model (e.g. 768 for Nomic, 4096 for Llama3/Mistral usually)
MAX_ELEMENTS = 1000

print("AGENT_SESSION_ID: ", AGENT_SESSION_ID)

# --- Pydantic Models ---
class IndexRequest(BaseModel):
    content: str
    metadata: str = ""

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 128

class CommandResponse(BaseModel):
    status: str
    result: Any = None
    telemetry: Any = None

# --- Helper to Initialize Session ---
def init_agent_memory():
    """
    Ensures the Vector DB instance exists in the session memory.
    """
    init_script = f"""
    vdb_instance {VECTOR_DB_NAME} dim={EMBED_DIM} max_elements={MAX_ELEMENTS} M=68 ef_construction=200
    store <r1> "Memory Initialized"
    """
    # EnsureExists calls session-check, creating it if missing
    M8.EnsureExists(AGENT_SESSION_ID, code=init_script)

@app.on_event("startup")
async def startup_event():
    print(f"Booting Agent Session: [{AGENT_SESSION_ID}]")
    init_agent_memory()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serves the agent_frontend.html file directly at the root URL.
    """
    if os.path.exists("app/index.html"):
        with open("app/index.html", "r") as f:
            return f.read()

    return """
    <html>
        <body style="background:#000; color: #0f0; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h1>Error: APP NOT FOUND</h1>
        </body>
    </html>
    """

@app.get("/p/{pagename}", response_class=HTMLResponse)
async def read_page(pagename):
    """
    Serves the agent_frontend.html file directly at the root URL.
    """
    pagef="app/"+pagename+".html"
    if os.path.exists(pagef):
        with open(pagef, "r") as f:
            return f.read()
    return """
    <html>
        <body style="background:#000; color: #0f0; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h1>Error: APP NOT FOUND</h1>
        </body>
    </html>
    """

# --- Endpoints ---

@app.post("/index", response_model=CommandResponse)
async def index_document(req: IndexRequest):
    """
    Embeds text and stores it in the M8 Vector DB.
    """
    # M8 Script to: 1. Store text in var, 2. Embed it, 3. Add to VDB
    # Note: We escape double quotes in content to avoid breaking M8 script syntax
    safe_content = req.content.replace('"', '\\"')
    
    script = f"""
    store <doc_text> {safe_content}
    llm_embed <doc_text> <embedding> dim={EMBED_DIM}
    vdb_add {VECTOR_DB_NAME} <embedding> {safe_content}
    store <rr> "Indexed"
    """
    
    resp = M8.RunSession(AGENT_SESSION_ID, script, timeout=10)
    
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Msg')}")
        
    return CommandResponse(
        status="success", 
        result="Document indexed successfully",
        telemetry=resp.get('Tms') # Returns the execution latency string
    )

@app.post("/search", response_model=CommandResponse)
async def search_memory(req: SearchRequest):
    """
    Semantic search against the M8 Vector DB.
    """
    safe_query = req.query.replace('"', '\\"')
    
    script = f"""
    store <query_text> {safe_query}
    llm_embed <query_text> <q_vec> dim={EMBED_DIM}
    vdb_search {VECTOR_DB_NAME} <q_vec> <matches> distance=0.6
    llm_detokenize <matches> <result> 
    return <result>
    """
    
    resp = M8.RunSession(AGENT_SESSION_ID, script, timeout=5)
    
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Msg')}")

    # M8 returns the result in the 'Ret' field usually, or raw body depending on implementation
    # Assuming 'Ret' contains the return value from the script
    result_data = [resp.get('R')]
    
    return CommandResponse(
        status="success",
        result=result_data,
        telemetry=resp.get('Tms')
    )


@app.post("/stream_chat")
async def stream_chat_llm(req: ChatRequest):
    """
    Streams LLM output using the M8 'stream' opcode channel.
    """
    safe_prompt = req.prompt.replace('"', '\\"')
    
    # We use 'llm_stream' which presumably utilizes the 'stream' opcode
    # to emit tokens as they are generated.
    script = f"""
    store <sysp> You are M8. A versatile and high performnance vm for AI workloads.
    store <input> <sysp>User: {safe_prompt}; Your Response: 

    llm_instance <input> instname n_predict=24 temperature=0.1 force=true 
    llm_instancestatus instname <r3_out>
    stream Response1: <r3_out>

    llm_instance <r3_out> instname2 n_predict=25 temperature=0.5 force=true 
    llm_instancestatus instname2 <r3_out>
    stream Response2: <r3_out>

    llm_instance <r3_out> instname3 n_predict=25 temperature=0.8 force=true 
    llm_instancestatus instname3 <r3_out>
    stream Response3: <r3_out>
    """
    
    return StreamingResponse(
        M8.StreamSession(AGENT_SESSION_ID, script),
        media_type="text/plain"
    )

@app.post("/chat", response_model=CommandResponse)
async def chat_llm(req: ChatRequest):
    """
    Simple LLM generation using M8P.
    """
    safe_prompt = req.prompt.replace('"', '\\"')
    safe_prompt = safe_prompt.replace('\n', ' ')
    safe_prompt = safe_prompt.replace('\t', '')
    
    script = f"""
    store <sysp> You are M8. A versatile and high performnance vm for AI workloads.
    store <input> <sysp>User: {safe_prompt}; Your Response: 
    llm_instance <input> instname n_predict=24 temperature=0.5 force=true 
    llm_instancestatus instname <r3_out>
    """
    
    resp = M8.RunSession(AGENT_SESSION_ID, script, timeout=30)
    
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Msg')}")

    return CommandResponse(
        status="success",
        result=resp.get('R'),
        telemetry=resp.get('Tms')
    )

@app.post("/reset")
async def reset_agent():
    """
    Destroys the session and garbage collects memory.
    """
    resp = M8.DestroySession(AGENT_SESSION_ID)
    return {"status": "Reset complete", "m8_response": resp}

if __name__ == "__main__":
    import uvicorn

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn.run(app, host="0.0.0.0", port=8002)