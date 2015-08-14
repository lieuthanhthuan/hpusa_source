{
    "name": "Manufacturing",
    "version": "1.2",
    "author": "thanhdongcntt",
    "category": "HPUSA module",
    "website": "http://thoitrangsile.org",
    "description": """
    Manufacturing Module
    """,
    'depends': ["mrp","sale","hr","mrp_operations","mrp_repair","gs_hpusa_order"],
    'init_xml': [],
    'update_xml': [
                   "wizard/wizard_hpusa_return_product_view.xml",
                    "hp_mrp_workflow.xml",
                    "hpusa_manufacturing_report.xml",
                    "hp_mrp_planning_view.xml",
                    "hp_sale_view.xml",
                    "hp_product_view.xml",
                    "hp_mrp_view.xml",
                    "hp_mrp_repair_view.xml",
                    "wizard/wizard_hpusa_product_list_report_view.xml",
                    "wizard/wizard_hpusa_report_view.xml",
                    "data/hpusa_manufacturing_data.xml",
                    "hp_stock_move_view.xml",
                   ],
    'installable': True,
    'active': False,
}