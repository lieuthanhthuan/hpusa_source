
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time

class hpusa_loyalty_report(osv.osv_memory):
    _name = "wizard.hpusa.loyalty.report"
    _description = "Loyalty Report"
    _columns = {
            'option':fields.selection([
                                   ('attend', 'Voucher Attend'),
                                   ('no_attend', 'Voucher Not Attend')
                                   ],
                                  'Option'),
     }
    def action_process(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context)
        if obj.option == 'attend':
            vals = {
                    'name': "Report",
                    'context':  {'search_default_Partner':1,'search_default_Voucher':1,'group_by_no_leaf':1},
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_model': 'hpusa.loyalty.report.2',
                    'view_id': False, 
                    'type': 'ir.actions.act_window',  
                    'nodestroy': True,
                }
            return vals
        else:
            vals = {
                    'name': "Report",
                    'context': {'search_default_Partner':1,'search_default_Voucher':1,'group_by_no_leaf':1},
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_model': 'hpusa.loyalty.report.1',
                    'view_id': False, 
                    'type': 'ir.actions.act_window',  
                    'nodestroy': True,
                }
            return vals
hpusa_loyalty_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
