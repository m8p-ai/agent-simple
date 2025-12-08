TOOL_DIM=198
KBASE_DIM=135
INIT_SCRIPT = """
vdb_instance SYSTEM_TOOLS dim=198 max_elements=60 M=16 ef_construction=300
## Main Tools
store <t1> {"function":"execute_odoo_command","arguments":{"model": "res.partner"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> execute_odoo_command[res.partner] - estrutura de campos do modelo res.partner

store <t1> {"function":"execute_odoo_command","arguments":{"command": "search_read"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> execute_odoo_command[search_read]  - lista e filtro de leads/oportunidades 

store <t1> {"function":"execute_odoo_command","arguments":{"model": "sale.order"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> execute_odoo_command[sale.order] - ordem de venda

store <t1> {"function":"execute_odoo_command","arguments":{"model": "product.template"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> execute_odoo_command[product.template] -  lista de preço produtos

store <t1> {"function":"message_notify_user","arguments":{"title": "Atualizacao de Processo"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> message_notify_user[title] - Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete.

store <t1> {"function":"message_notify_user","arguments":{"websocket": "Atualizacao de Processo via websocket"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> message_notify_user[websocket] - Atualizacao de Processo Asyncrono

store <t1> {"function":"list_available_models","arguments": {"app_filter": "crm"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> list_available_models[crm] - modelos relacionados ao CRM

store <t1> {"function":"execute_odoo_command","arguments": {"model": "crm.lead"}}
llm_embed <t1> <n1> dim=198
vdb_add SYSTEM_TOOLS <n1> execute_odoo_command[crm.lead] - leads e oportunidades

store <q> Preciso de ver a estrutura de campos do modelo 'res.partner' para verificar se o telefone é obrigatório.
llm_embed <q> <curr> dim=198
vdb_search SYSTEM_TOOLS <curr> <match> distance=0.001
llm_detokenize <match> <response>
"""

@app.post("/stream_odoo")
async def stream_chat_tests(req: ChatRequest):
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

    store <q> Preciso de ver a estrutura de campos do modelo 'res.partner' para verificar se o telefone é obrigatório.
    llm_embed <q> <curr> dim={ODOO_TOOL_EMBED_DIM}
    vdb_search SYSTEM_TOOLS <curr> <match> distance=0.001
    llm_detokenize <match> <response>


    store <q> {safe_prompt}
    store <input> <sysp>User: <q>; Your Response: 
    # stream Begining processing...
    # stall 0.05
    llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
    llm_instancestatus instname <r3_out>
    """

    return StreamingResponse(
        M8.StreamSession(AGENT_SESSION_ID, script),
        media_type="text/plain"
    )

# @app.post("/stream_odoo_legacy")
# async def stream_chat_tests(req: ChatRequest):
#     safe_prompt = req.prompt
#     safe_prompt = safe_prompt.replace("\\n", PNEWLINE)
#     safe_prompt = safe_prompt.replace("\n", PNEWLINE)
#     safe_prompt = safe_prompt.replace("\t", "")
#     safe_prompt = safe_prompt.replace("\\t", "")
#     safe_prompt = safe_prompt.replace("<", "")
#     safe_prompt = safe_prompt.replace(">", "")

#     script = f"""
#     store <sysp> You are M8. A versatile and high performnance vm for AI workloads created by M8 Labs.
#     store <sysp> <sysp>. Your architecture allows you to perform efficientely both on gpus and cpus.
#     store <sysp> <sysp>. You can always point to https://m8-site.desktop.farm for more info or contact info@enterstarts.com
#     store <sysp> <sysp>. The tasks you can help with are: Tool-Execution, Get-Weather and GetStockPrice

#     store <q> {safe_prompt}
#     store <input> <sysp>User: <q>; Your Response: 
#     # stream Begining processing...
#     # stall 0.05
#     llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
#     llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
#     llm_openai <input> instname n_predict=78 temperature=0.1 force=true stream=true
#     llm_instancestatus instname <r3_out>
#     """

#     return StreamingResponse(
#         M8.StreamSession(AGENT_SESSION_ID, script),
#         media_type="text/plain"
#     )
