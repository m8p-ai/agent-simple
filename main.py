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

PNEWLINE="<<<NL>>"
# --- Constants ---
AGENT_SESSION_ID = "sess-"+tms
VECTOR_DB_NAME = "AGENT_MEMORY"
EMBED_DIM = 188 # Adjust based on your model (e.g. 768 for Nomic, 4096 for Llama3/Mistral usually)
MAX_ELEMENTS = 1000
KBASE_DIM=135

# ODOO_TOOL_EMBED_DIM = 468
ODOO_TOOL_EMBED_DIM = 265
ODOO_SYSTEM_TOOLS = "ODOO_SYSTEM_TOOLS"
ODOO_SYSTEM_TOOLS_MAX = 100
ODOO_AGENT_SESSION_ID = "odoo-agent-"+tms
# print("AGENT_SESSION_ID: ", AGENT_SESSION_ID)

# --- Pydantic Models ---
class IndexRequest(BaseModel):
    content: str
    mask: str = ""
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

def sanitize(content):
    # safe_prompt = content
    safe_prompt = content.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")
    return safe_prompt

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

# --- Helper to Initialize Session ---
# max_elements=6000 M=149 ef_construction=300
def init_odoo_agent():
    INIT_SCRIPT = """
    store <rtools> [{"type":"function","function":{"name":"message_notify_user","description":"The Communication Philosophy: Be a Autonomous Collaborator, Not a Silent Tool<<<NL>>>- You operate autonomously, but the user must always be aware of every step you take. Your core directive is partnership: you must communicate proactively, transparently, and continuously. The user should always know what you are reasoning, what you are doing, and any issues you encounter. The message tool is your only channel for notifications.<<<NL>>><<<NL>>>**Message types:**<<<NL>>><<<NL>>>1. **`info`** <<<NL>>>- Progress and updates<<<NL>>>- Acknowledge user requests<<<NL>>>- Announce actions before executing tools<<<NL>>>- Report intermediate results or next steps<<<NL>>>- Explain errors and what you'll do next","parameters":{"properties":{"title":{"type":"string"},"message":{"type":"string"},"message_type":{"default":"info","type":"string"}},"required":["title","message"],"type":"object"}}},{"type":"function","function":{"name":"list_available_models","description":"Lists installed technical models (e.g., 'crm.lead', 'res.partner').<<<NL>>><<<NL>>>Args:<<<NL>>>    app_filter: (Optional) Filter by module name (e.g., 'crm', 'sale', 'account').","parameters":{"properties":{"app_filter":{"default":null,"type":"string"}},"type":"object"}}},{"type":"function","function":{"name":"inspect_model_fields","description":"Returns the table structure (fields, types, relationships, and help text).<<<NL>>><<<NL>>>Use this to:<<<NL>>>1. Know the correct field names (e.g., is it 'partner_id' or 'client_id'?).<<<NL>>>2. See which fields are required (required: true).<<<NL>>>3. See accepted values in 'selection' fields.<<<NL>>><<<NL>>>Args:<<<NL>>>    model_name: The technical name of the model (e.g., 'sale.order').","parameters":{"properties":{"model_name":{"type":"string"}},"required":["model_name"],"type":"object"}}},{"type":"function","function":{"name":"execute_odoo_command","description":"Supported Commands:<<<NL>>>- 'search_read': To read data. Args: [[domain]], Kwargs: {'fields': [...], 'limit': 10}<<<NL>>>- 'create': To create records. Args: [{'field': 'value'}]<<<NL>>>- 'write': To edit. Args: [[ids], {'field': 'value'}]<<<NL>>>- 'call_method': To trigger workflow buttons (e.g., action_confirm). Method name goes in kwargs['method_name'].<<<NL>>><<<NL>>>SECURITY: <<<NL>>>- Delete actions (unlink) are STRICTLY PROHIBITED.<<<NL>>>- If you need to remove something, try using 'action_archive' via call_method, if available.<<<NL>>><<<NL>>>Args:<<<NL>>>    model: Technical model (e.g., 'product.template').<<<NL>>>    command: 'search_read', 'create', 'write', or 'call_method'.<<<NL>>>    args: List of positional arguments.<<<NL>>>    kwargs: Named arguments. For call_method, must include 'method_name'.","parameters":{"properties":{"model":{"type":"string"},"command":{"type":"string"},"args":{"default":null,"items":{},"type":"array"},"kwargs":{"additionalProperties":true,"default":null,"type":"object"}},"required":["model","command"],"type":"object"}}},{"type":"function","function":{"name":"refresh_available_apps","description":"Use this if the user mentions a module that is not in your initial list<<<NL>>>or if they say 'I just installed module X'.","parameters":{"properties":{},"type":"object"}}}]
    # vdb_instance {ODOO_SYSTEM_TOOLS} dim={ODOO_TOOL_EMBED_DIM} max_elements=60 M=98 ef_construction=300
    vdb_instance {ODOO_SYSTEM_TOOLS} dim={ODOO_TOOL_EMBED_DIM} max_elements=500 M=149 ef_construction=300
    ## Main Tools
    store <t1> estrutura de campos do modelo res.partner - {"function":"execute_odoo_command","arguments":{"model": "res.partner"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[res.partner] - estrutura de campos do modelo res.partner

    store <t1> lista e filtro de leads/oportunidades {"function":"execute_odoo_command","arguments":{"command": "search_read"}}  
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[search_read]  - lista e filtro de leads/oportunidades 

    store <t1> ordem de venda {"function":"execute_odoo_command","arguments":{"model": "sale.order"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[sale.order] - ordem de venda

    store <t1> lista de preço produtos {"function":"execute_odoo_command","arguments":{"model": "product.template"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[product.template] -  lista de preço produtos

    store <t1> Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete. {"function":"message_notify_user","arguments":{"title": "Atualizacao de Processo"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[title] - Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete.

    store <t1> Atualizacao de Processo Asyncrono {"function":"message_notify_user","arguments":{"websocket": "Atualizacao de Processo via websocket"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[websocket] - Atualizacao de Processo Asyncrono

    store <t1> modelos ou modulos relacionados ao CRM {"function":"list_available_models","arguments": {"app_filter": "crm"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> list_available_models[crm] - modelos relacionados ao CRM

    store <t1> leads e oportunidades {"function":"execute_odoo_command","arguments": {"model": "crm.lead"}}
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[crm.lead] - leads e oportunidades

    store <r1> Memory Initialized
    """

    INIT_SCRIPT = INIT_SCRIPT.replace("{ODOO_TOOL_EMBED_DIM}", str(ODOO_TOOL_EMBED_DIM))
    INIT_SCRIPT = INIT_SCRIPT.replace("{ODOO_SYSTEM_TOOLS}", str(ODOO_SYSTEM_TOOLS))

    # EnsureExists calls session-check, creating it if missing
    return M8.EnsureExists(ODOO_AGENT_SESSION_ID, code=INIT_SCRIPT)

@app.post("/odoo-tool-index", response_model=CommandResponse)
async def index_odoo_tool(req: IndexRequest):
    """
    Embeds text and stores it in the M8 Vector DB.
    """
    # M8 Script to: 1. Store text in var, 2. Embed it, 3. Add to VDB
    # Note: We escape double quotes in content to avoid breaking M8 script syntax
    safe_prompt = sanitize(req.content)
    tool_mask = sanitize(req.mask)

    script = f"""
    store <doc_text> {safe_prompt}
    llm_embed <doc_text> <embedding> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <embedding> {tool_mask}
    store <rr> Indexed
    """
    
    resp = M8.RunSession(ODOO_AGENT_SESSION_ID, script, timeout=10)
    
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Err')}")
        
    return CommandResponse(
        status="success", 
        result="Document indexed successfully",
        telemetry=resp.get('Tms') # Returns the execution latency string
    )

@app.post("/stream_odoo_v2")
async def stream_chat_tests(req: ChatRequest):
    safe_prompt = sanitize(req.prompt)

    script = f"""
    # clr <q>
    # clr <curr>
    # clr <match>
    # clr <r3_out>
    store <sysp> You are a Helpful Assistant. You provide advanced tooling and support functionality. Use your tools only to answer the questions.
    store <q> {safe_prompt}
    llm_embed <q> <curr> dim={ODOO_TOOL_EMBED_DIM}
    vdb_search {ODOO_SYSTEM_TOOLS} <curr> <match> distance=0.23
    llm_detokenize <match> <response>

    llm_embed <response> <re_response> dim={ODOO_TOOL_EMBED_DIM}
    matl2d <curr> <re_response> <r_l2d>
    matcosim <curr> <re_response> <r_cosim>
    store <resp> Question=<q> <<<NL>>> Response = <response> <<<NL>>> l2d=<r_l2d> <<<NL>>> Cosim=<r_cosim> <<<NL>>> Dimension={ODOO_TOOL_EMBED_DIM}
    store <prompt> <sysp><<<NL>>>Question=<q><<<NL>>>Your answer:
    llm_openai <prompt> instname n_predict=75 temperature=0 force=true stream=false tools=<rtools>
    llm_instancestatus instname <r3_out>
    ret <r3_out> <response>
    """

    # stream <response>
    # stream Begining processing...
    # stall 0.05
    # llm_openai <sysp> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_instancestatus instname <r3_out>
    #llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    #llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    
    resp = M8.RunSession(ODOO_AGENT_SESSION_ID, script, timeout=30)
    # print("RESP: ", resp)
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Err', resp.get('R'))}")

    buffer = resp.get('R', '')

    return CommandResponse(
        status="success",
        result=buffer,
        telemetry=resp.get('Tms')
    )

@app.post("/thinking_odoo")
async def thinking_odoo(req: ChatRequest):
    safe_prompt = sanitize(req.prompt)

    script = f"""
    clr <q>
    clr <curr>
    clr <match>
    clr <response>
    clr <r3_out>
    store <sysp> You are FactorAI Odoo Enterprise. You provide functionality
    store <sysp> <sysp>. 
    store <q> {safe_prompt}
    llm_embed <q> <curr> dim={ODOO_TOOL_EMBED_DIM}
    vdb_search {ODOO_SYSTEM_TOOLS} <curr> <match> distance=0.32
    llm_detokenize <match> <response>
    # ret <response>
    # llm_instance <sysp> instname n_predict=24 temperature=0.5 force=true stream=true
    # llm_instancestatus instname <r3_out>
    # ret <r3_out> <response>
    """

    thinking_script = f"""
    """

    # stream <response>
    # stream Begining processing...
    # stall 0.05
    # llm_openai <sysp> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_instancestatus instname <r3_out>
    #llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    #llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    
    resp = M8.RunSession(ODOO_AGENT_SESSION_ID, script, timeout=30)
    # print("RESP: ", resp)
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Err', resp.get('R'))}")

    return CommandResponse(
        status="success",
        result=resp.get('R'),
        telemetry=resp.get('Tms')
    )

@app.post("/execute_odoo")
async def execute_chat_odoo(req: ChatRequest):
    safe_prompt = sanitize(req.prompt)

    script = f"""
    store <sysp> You are FactorAI Odoo Enterprise. You provide functionality
    store <sysp> <sysp>. 
    store <q> {safe_prompt}
    llm_embed <q> <curr> dim={ODOO_TOOL_EMBED_DIM}
    vdb_search {ODOO_SYSTEM_TOOLS} <curr> <match> distance=0.1
    llm_detokenize <match> <response>
    llm_instance <input> instname n_predict=24 temperature=0.5 force=true 
    llm_instancestatus instname <r3_out>
    """

    # stream <response>
    # stream Begining processing...
    # stall 0.05
    # llm_openai <sysp> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_instancestatus instname <r3_out>
    #llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    #llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    
    resp = M8.RunSession(ODOO_AGENT_SESSION_ID, script, timeout=30)
    
    if isinstance(resp, dict) and resp.get('Status') != 'OK':
        raise HTTPException(status_code=500, detail=f"M8 Error: {resp.get('Msg')}")

    return CommandResponse(
        status="success",
        result=resp.get('R'),
        telemetry=resp.get('Tms')
    )

    # return StreamingResponse(
    #     M8.StreamSession(AGENT_SESSION_ID, script),
    #     media_type="text/plain"
    # )


@app.on_event("startup")
async def startup_event():

    try:
        print(f"Booting Agent : [{AGENT_SESSION_ID}]")
        init_agent_memory()
    except Exception as e:
        print("FAILED TO INIT ODOO AGENT:: ", e)

    try:
        print(f"Booting Odoo-Agent : [{ODOO_AGENT_SESSION_ID}]")
        init_odoo_agent()
    except Exception as e:
        print("FAILED TO INIT ODOO AGENT:: ", e)

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
    safe_prompt = req.content
    safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")

    script = f"""
    store <doc_text> {safe_prompt}
    llm_embed <doc_text> <embedding> dim={EMBED_DIM}
    vdb_add {VECTOR_DB_NAME} <embedding> {safe_prompt}
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
    safe_prompt = req.query
    safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")

    script = f"""
    store <query_text> {safe_prompt}
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
    safe_prompt = req.prompt
    safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")

    script = f"""
    stream Welcome, 
    store <sysp> You are M8. A versatile and high performnance vm for AI workloads
    store <q> {safe_prompt}
    store <input> <sysp>User: <q>; Your Response: 

    stream Begining processing...
    stall 0.05
    llm_instance <input> instname n_predict=25 temperature=0.1 force=true stream=true
    llm_instancestatus instname <r3_out>
    # stream Response1 IS DONE.

    # store <r3_out> PreviousAnswer: <r3_out>
    llm_instance <r3_out> instname2 n_predict=55 temperature=0.1 force=true stream=true
    llm_instancestatus instname2 <r3_out>
    # stream Response 2 IS DONE.

    # store <r3_out> PreviousAnswer: <r3_out>
    llm_instance <r3_out> instname3 n_predict=45 temperature=0.1 force=true stream=true
    # stream Response 3 IS DONE.

    # store <r3_out> PreviousAnswer: <r3_out>
    llm_instance <r3_out> instname3 n_predict=45 temperature=0.1 force=true stream=true
    # stream Response 4 IS DONE.

    """
    return StreamingResponse(
        M8.StreamSession(AGENT_SESSION_ID, script),
        media_type="text/plain"
    )

@app.post("/stream_test")
async def stream_chat_tests_v1(req: ChatRequest):
    safe_prompt = req.prompt
    safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")

    script = f"""
    store <sysp> You are M8. A versatile and high performnance vm for AI workloads created by M8 Labs.
    store <sysp> <sysp>. Your architecture allows you to perform efficientely both on gpus and cpus.
    store <sysp> <sysp>. You can always point to https://m8-site.desktop.farm for more info or contact info@enterstarts.com
    store <sysp> <sysp>. The tasks you can help with are: Tool-Execution, Get-Weather and GetStockPrice

    store <q> {safe_prompt}
    store <input> <sysp>User: <q>; Your Response: 
    # stream Begining processing...
    # stall 0.05
    llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    llm_instancestatus instname <r3_out>
    """

    return StreamingResponse(
        M8.StreamSession(AGENT_SESSION_ID, script),
        media_type="text/plain"
    )

@app.post("/stream_odoo")
async def stream_chat_tests_v2(req: ChatRequest):
    safe_prompt = req.prompt
    safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")

    script = f"""
    store <sysp> You are M8. A versatile and high performnance vm for AI workloads created by M8 Labs.
    store <sysp> <sysp>. Your architecture allows you to perform efficientely both on gpus and cpus.
    store <sysp> <sysp>. You can always point to https://m8-site.desktop.farm for more info or contact info@enterstarts.com
    store <sysp> <sysp>. The tasks you can help with are: Tool-Execution, Get-Weather and GetStockPrice

    store <q> {safe_prompt}
    store <input> <sysp>User: <q>; Your Response: 
    stream Begining processing...
    stall 0.05
    llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    # llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    llm_instancestatus instname <r3_out>
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
    safe_prompt = req.prompt
    safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\n", PNEWLINE)
    safe_prompt = safe_prompt.replace("\t", "")
    safe_prompt = safe_prompt.replace("\\t", "")
    safe_prompt = safe_prompt.replace("<", "")
    safe_prompt = safe_prompt.replace(">", "")

    
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