# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://gscom.vn>). All Rights Reserved
#
##############################################################################

{
        "name" : "HUNGPHAT",
        "version" : "1.0",
        "author" : "General Solutions",
        "website" : "http://www.gscom.vn",
        "category" : "GS Modules",
        "description" : """HUNG PHAT""",
        "depends" : ["base","sale"],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : ["wizard/gs_wizard_report_view.xml", 
			   "wizard/gs_wizard_report_view_cost.xml", 
                        "gs_hpusa_sale_order_view.xml",
                        "security/gs_security_hpusa_sale_order.xml",  
                        "gs_hpusa_sale_order_report.xml",   
                        "res_partner_view.xml", 
                        "res_user_view.xml",     
                       ],
        "installable": True
}
