{
    "name": "HPUSA Groups",
    "version": "1.2",
    "author": "thanhdongcntt",
    "category": "HPUSA Groups",
    "website": "http://www.openerp.com",
    "description": """
    Loyalty
    """,
    'website': 'http://www.openerp.com',
    'depends':["base", "sale", "crm", "mrp", 'project'],
    'init_xml': [],
    'update_xml': [
                    "hpusa_groups_view.xml",
                   ],
    'installable': True,
    'active': False,
}