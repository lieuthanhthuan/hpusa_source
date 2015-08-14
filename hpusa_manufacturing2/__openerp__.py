{
    "name": "Manufacturing 2",
    "version": "1.2",
    "author": "Thanh Thuan Lieu",
    "category": "HPUSA module",
    "website": "http:cuatui.odoo.com",
    "description": """
    Manufacturing Module version 2
    """,
    'depends': ["mrp","sale","hr","mrp_operations","mrp_repair","gs_hpusa_order"],
    'init_xml': [],
    'update_xml': [
                   "hp_mrp_view.xml",
		   "hp_product_view.xml",
                   "hp_stock_picking_view.xml",
                   ],
    'installable': True,
    'active': False,
}