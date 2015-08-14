{
    "name": "Agent Cooperate",
    "version": "1.2",
    "author": "thanhdongcntt",
    "category": "HPUSA module",
    "website": "http://thoitrangsile.org",
    "description": """
    Agent Cooperate Module
    """,
    'depends': ["base","sale_commission_calc","account","account_voucher"],
    'init_xml': [],
    'update_xml': [
                    'data/hp_agent_cooperate_data.xml',
                    'security/account_security.xml',
                    'hp_agent_coopearate_view.xml',
                    'report/hp_agent_cooperate_report.xml',
                   ],
    'installable': True,
    'active': False,
}