# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://generalsolutions.vn>). All Rights Reserved
#
##############################################################################
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _

class Country(osv.osv):
    _inherit = "res.country"
    _columns = {
        'code_mobile': fields.char('Code Mobile', size=64, required=True, translate=True),
               }
Country() 