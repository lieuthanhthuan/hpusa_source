{
    "name": "Hpusa Sale Order",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "Sales",
    "website": "cuatui.odoo.com",
    "description": """
    Show delivery date for Sale Order
    """,
    'website': 'cuatui.odoo.com',
    'depends':["base", "sale"],
    'init_xml': [],
    'update_xml': [
                    "hpusa_sale_order_view.xml",
                   ],
    'installable': True,
    'active': False,
}