# vdb_instance {ODOO_SYSTEM_TOOLS} dim={ODOO_TOOL_EMBED_DIM} max_elements=500 M=149 ef_construction=300
# ## Main Tools
# store <t1> estrutura de campos do modelo res.partner - {"function":"execute_odoo_command","arguments":{"model": "res.partner"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[res.partner] - estrutura de campos do modelo res.partner

# store <t1> lista e filtro de leads/oportunidades {"function":"execute_odoo_command","arguments":{"command": "search_read"}}  
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[search_read]  - lista e filtro de leads/oportunidades 

# store <t1> ordem de venda {"function":"execute_odoo_command","arguments":{"model": "sale.order"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[sale.order] - ordem de venda

# store <t1> lista de preço produtos {"function":"execute_odoo_command","arguments":{"model": "product.template"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[product.template] -  lista de preço produtos

# store <t1> Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete. {"function":"message_notify_user","arguments":{"title": "Atualizacao de Processo"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[title] - Atualizacao de Processo por email, notificacao, mensagem, chat, lembrete.

# store <t1> Notificacao de utilizadores por email, notificacao, mensagem, chat, lembrete. {"function":"message_notify_user","arguments":{"title": "Notificar"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[title] -Notificacao de utilizador

# store <t1> Atualizacao de Processo Asyncrono {"function":"message_notify_user","arguments":{"websocket": "Atualizacao de Processo via websocket"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> message_notify_user[websocket] - Atualizacao de Processo Asyncrono

# store <t1> modelos ou modulos relacionados ao CRM {"function":"list_available_models","arguments": {"app_filter": "crm"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> list_available_models[crm] - modelos relacionados ao CRM

# store <t1> leads e oportunidades {"function":"execute_odoo_command","arguments": {"model": "crm.lead"}}
# llm_embed <t1> <n1> dim={ODOO_TOOL_EMBED_DIM}
# vdb_add {ODOO_SYSTEM_TOOLS} <n1> execute_odoo_command[crm.lead] - leads e oportunidades