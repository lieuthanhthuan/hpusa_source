{
    "name": "Hpusa Purchase Order",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "Purchase",
    "website": "cuatui.odoo.com",
    "description": """
    Done Purchase Order
    """,
    'website': 'cuatui.odoo.com',
    'depends':["base", "purchase"],
    'init_xml': [],
    'update_xml': [
                    "hpusa_purchase_order_view.xml",
                   ],
    'installable': True,
    'active': False,
}