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
        "depends" : ["project","project_issue","document","hr_holidays","hr_timesheet_sheet","hr_expense","hr","hr_contract","hr_recruitment"],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : ["security/gs_security_hpusa_project.xml",
                        "gs_hpusa_project_view.xml",                 
                       ],
        "installable": True
}
