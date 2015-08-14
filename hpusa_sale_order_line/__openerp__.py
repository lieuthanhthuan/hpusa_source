{
    "name": "Sale Order Line",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "HPUSA module",
    "website": "cuatui.odoo.com",
    "description": """
    Manufacturing Module Create Relation of Sale Order, Manufacturing Order and Purchase Order
    """,
    'depends': ["sale","gs_hpusa_order"],
    'init_xml': [],
    'update_xml': [
                   "hpusa_sale_order_line_view.xml"
                   ],
    'installable': True,
    'active': False,
}