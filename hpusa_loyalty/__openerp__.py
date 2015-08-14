{
    "name": "Loyalty",
    "version": "1.2",
    "author": "thanhdongcntt",
    "category": "Loyalty",
    "website": "http://www.openerp.com",
    "description": """
    Loyalty
    """,
    'website': 'http://www.openerp.com',
    'depends': ["base", "sale", "stock", "product","mail","crm"],
    'init_xml': [],
    'update_xml': [
                   "hpusa_loyalty.xml",
                   "report/hpusa_loyalty_report.xml",
                   ],
    'js': [
        'static/src/js/tree_demo.js',
    ],
    'qweb' : [
        "static/src/xml/tree_demo.xml",
    ],
    'css':[
        'static/src/css/tree_demo.css',
    ],
    'installable': True,
    'active': False,
}