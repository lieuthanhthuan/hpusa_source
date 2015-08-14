{
    "name": "HPUSA PRICELIST",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "HPUSA module",
    "website": "cuatui.odoo.com",
    "description": """
    Manufacturing Module Create Relation of Sale Order, Manufacturing Order and Purchase Order
    """,
    'depends': ["sale","gs_hpusa_order","product"],
    'init_xml': [],
    'update_xml': [
                   "hpusa_product_pricelist_view.xml"
                   ],
    'installable': True,
    'active': False,
}