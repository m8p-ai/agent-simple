def init_odoo_agent():
    INIT_SCRIPT = """
    # vdb_instance {ODOO_SYSTEM_TOOLS} dim={ODOO_TOOL_EMBED_DIM} max_elements=60 M=98 ef_construction=300
    vdb_instance {ODOO_SYSTEM_TOOLS} dim={ODOO_TOOL_EMBED_DIM} max_elements=500 M=149 ef_construction=300
    ## Main Tools
    store <t1> {"function":"execute_odoo_command","arguments":{"model": "res.partner"}} - estrutura de campos do modelo res.partner
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[res.partner] - estrutura de campos do modelo res.partner

    store <t1> {"function":"execute_odoo_command","arguments":{"command": "search_read"}} lista e filtro de leads/oportunidades 
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[search_read]  - lista e filtro de leads/oportunidades 

    store <t1> {"function":"execute_odoo_command","arguments":{"model": "sale.order"}} - ordem de venda
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[sale.order] - ordem de venda

    store <t1> {"function":"execute_odoo_command","arguments":{"model": "product.template"}} -  lista de preço produtos
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[product.template] -  lista de preço produtos

    store <t1> {"function":"message_notify_user","arguments":{"title": "Atualizacao de Processo"}} - Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete.
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[title] - Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete.

    store <t1> {"function":"message_notify_user","arguments":{"websocket": "Atualizacao de Processo via websocket"}} - Atualizacao de Processo Asyncrono
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[websocket] - Atualizacao de Processo Asyncrono

    store <t1> {"function":"list_available_models","arguments": {"app_filter": "crm"}} - modelos ou modulos relacionados ao CRM
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> list_available_models[crm] - modelos relacionados ao CRM

    store <t1> {"function":"execute_odoo_command","arguments": {"model": "crm.lead"}} - leads e oportunidades
    llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
    vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[crm.lead] - leads e oportunidades

    store <r1> Memory Initialized
    """

    INIT_SCRIPT = INIT_SCRIPT.replace("{ODOO_TOOL_EMBED_DIM}", str(ODOO_TOOL_EMBED_DIM))
    INIT_SCRIPT = INIT_SCRIPT.replace("{ODOO_SYSTEM_TOOLS}", str(ODOO_SYSTEM_TOOLS))

    # EnsureExists calls session-check, creating it if missing
    return M8.EnsureExists(ODOO_AGENT_SESSION_ID, code=INIT_SCRIPT)
