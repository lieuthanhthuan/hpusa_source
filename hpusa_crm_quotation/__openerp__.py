{
    "name": "Hpusa Quotation",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "CRM",
    "website": "cuatui.odoo.com",
    "description": """
    Show relationship CRM and Quotation
    """,
    'website': 'cuatui.odoo.com',
    'depends':["base", "sale","crm"],
    'init_xml': [],
    'update_xml': [
                    "hpusa_crm_sale_order_view.xml",
                   ],
    'installable': True,
    'active': False,
}