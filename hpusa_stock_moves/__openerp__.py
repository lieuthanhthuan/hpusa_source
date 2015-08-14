{
    "name": "Hpusa Stock Moves",
    "version": "1.2",
    "author": "thanhthuanlieu",
    "category": "HPUSA module",
    "website": "cuatui.odoo.com",
    "description": """
    auto translate draft to gold 18K 75% 
    """,
    'depends': ["stock"],
    'init_xml': [],
    'update_xml': [
                    'hpusa_stock_moves_view.xml',
                   ],
    'installable': True,
    'active': False,
}