{
    "name": "Hpusa Refer a friend",
    "version": "1.2",
    "author": "thanhthuanlieu",
    "category": "HPUSA module",
    "website": "cuatui.odoo.com",
    "description": """
    Hpusa refer a friend used to manager about Refer afriend given to Customer
    and Friends of that customer, After that company wil give commission for that customer
    """,
    'depends': ["base","account","account_voucher"],
    'init_xml': [],
    'update_xml': [
                    'hp_referafriend_view.xml',
                   ],
    'installable': True,
    'active': False,
}