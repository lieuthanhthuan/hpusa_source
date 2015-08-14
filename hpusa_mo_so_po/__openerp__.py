{
    "name": "Manufacturing Relation",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "HPUSA module",
    "website": "cuatui.odoo.com",
    "description": """
    Manufacturing Module Create Relation of Sale Order, Manufacturing Order and Purchase Order
    """,
    'depends': ["mrp","sale","purchase","hr","mrp_operations","mrp_repair","gs_hpusa_order"],
    'init_xml': [],
    'update_xml': [
                   "hpusa_mo_so_po_view.xml"
                   ],
    'installable': True,
    'active': False,
}