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
        "depends" : ["base","crm","sale_crm","account","sale","analytic","note","marketing_campaign"],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : ["gs_hpusa_crm_view.xml", 
                        "hpusa_contacts_view.xml",                 
                       ],
        "installable": True
}
