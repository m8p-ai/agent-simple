import uuid
import os
from datetime import datetime

def get_date_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

MAP = {
    # --- CRM / LEADS ---
    'execute_odoo_command[crm.lead]- leads e oportunidades' : {
        'list' : [
            {
                "id": 1,
                "name": "Interest in 3D Rendering Engine",
                "type": "opportunity",
                "partner_id": [10, "Azure Interior"], # Odoo M2O format [id, name]
                "email_from": "client@azure-interior.com",
                "expected_revenue": 15000.00,
                "probability": 20.0,
                "stage_id": [2, "Qualified"],
                "create_date": get_date_str(),
                "priority": "2"
            },
            {
                "id": 2,
                "name": "Hardware Consultation - H200 Clusters",
                "type": "lead",
                "partner_id": False,
                "email_from": "info@tech-start.io",
                "expected_revenue": 0.00,
                "probability": 0.0,
                "stage_id": [1, "New"],
                "create_date": get_date_str(),
                "priority": "1"
            }
        ]
    },

    # --- CONTACTS / PARTNERS ---
    'execute_odoo_command[res.partner]- estrutura de campos do modelo res.partner' : {
        'list': [
            {
                "id": 10,
                "name": "Azure Interior",
                "is_company": True,
                "email": "info@azure-interior.com",
                "phone": "+1 555 123 4567",
                "street": "456 Industry Way",
                "city": "San Francisco",
                "category_id": [1, "Customer"]
            },
            {
                "id": 11,
                "name": "Brandon Freeman",
                "is_company": False,
                "parent_id": [10, "Azure Interior"],
                "email": "brandon@azure-interior.com",
                "function": "CTO",
                "phone": "+1 555 987 6543"
            }
        ]
    },

    # --- GENERIC SEARCH RESULT ---
    'execute_odoo_command[search_read]- lista e filtro de leads / oportunidades' : {
        'list': [
             # Usually dynamic, but here is a mock response
             {"id": 5, "display_name": "Op: Office Design Project"},
             {"id": 6, "display_name": "Op: Server Migration"}
        ]
    },

    # --- PRODUCTS ---
    'execute_odoo_command[product.template]- lista de preco produtos' : {
        'list': [
            {
                "id": 101,
                "name": "Graphics Accelerator Card L40S",
                "default_code": "GPU-L40S",
                "list_price": 8500.00,
                "standard_price": 6000.00, # Cost
                "qty_available": 12,
                "uom_id": [1, "Units"],
                "type": "product" # Storable
            },
            {
                "id": 102,
                "name": "Consulting Service (Hour)",
                "default_code": "SERV-001",
                "list_price": 150.00,
                "standard_price": 0.00,
                "type": "service"
            }
        ]
    },

    # --- SALES ORDERS ---
    'execute_odoo_command[sale.order]- ordem de venda' : {
        'list': [
            {
                "id": 501,
                "name": "S00012",
                "partner_id": [10, "Azure Interior"],
                "date_order": get_date_str(),
                "amount_total": 17150.00,
                "state": "sale", # sale = Confirmed
                "user_id": [1, "Admin"],
                "order_line": [ # One2many mock
                    {"product_id": [101, "GPU-L40S"], "qty": 2, "price_unit": 8500.00},
                    {"product_id": [102, "SERV-001"], "qty": 1, "price_unit": 150.00}
                ]
            },
            {
                "id": 502,
                "name": "S00013",
                "partner_id": [12, "Deco Addict"],
                "date_order": get_date_str(),
                "amount_total": 450.00,
                "state": "draft", # draft = Quotation
                "user_id": [1, "Admin"]
            }
        ]
    },

    # --- NOTIFICATIONS (Mock Payloads) ---
    'message_notify_user[websocket]- atualizacao de processo asyncrono' : {
        'list': [
            {
                "type": "websocket",
                "channel": "broadcast_channel",
                "payload": {"status": "sync_complete", "records_updated": 45}
            }
        ]
    },

    'message_notify_user[title]- notificacao de utilizador' : {
        'list': [
            {
                "title": "Import Success",
                "message": "The CSV import for Res.Partner finished.",
                "sticky": False,
                "type": "success"
            }
        ]
    },
}

def execute_tool(name, params=None):
    ## GENERATE: Simple fetcher to return the fixtures based on key
    if name in MAP:
        return MAP[name]

    return []

MAP_RULES = {
    'execute_odoo_command[crm.lead]- leads e oportunidades' : {
        'description': 'Manage CRM Leads',
        'default_fields': ['name', 'partner_id', 'probability', 'stage_id']
    },

    'execute_odoo_command[res.partner]- estrutura de campos do modelo res.partner' : {
        'description': 'Manage Contacts/Partners',
        'default_fields': ['name', 'email', 'phone', 'vat']
    },

    'execute_odoo_command[search_read]- lista e filtro de leads / oportunidades' : {
        'description': 'Generic Search Read capability',
        'method': 'search_read'
    },

    'execute_odoo_command[product.template]- lista de preco produtos' : {
        'description': 'Product Pricing',
        'default_fields': ['name', 'list_price', 'standard_price']
    },
    
    'execute_odoo_command[sale.order]- ordem de venda' : {
        'description': 'Sales Orders',
        'default_fields': ['name', 'partner_id', 'amount_total', 'state']
    },

    'message_notify_user[websocket]- atualizacao de processo asyncrono' : {
        'type': 'socket',
        'channel': 'async_updates'
    },

    'message_notify_user[title]- notificacao de utilizador' : {
        'type': 'toast',
        'priority': 'high'
    },
}