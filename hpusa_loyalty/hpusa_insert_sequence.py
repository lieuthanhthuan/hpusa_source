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

import tools
from osv import fields, osv

class hpusa_insert_sequence(osv.osv):
    _name = "hpusa.insert.sequence"
    _auto = False
    def init(self, cr):
        sql = '''SELECT * FROM ir_sequence WHERE code = ('hpusa.gift.voucher')'''
        cr.execute(sql)
        result = cr.dictfetchall()
        if not result:
            cr.execute("""
                insert INTO ir_sequence_type(code, "name") values('hpusa.gift.voucher', 'Gift Voucher');
            """)
            sequence_obj = self.pool.get('ir.sequence')
            vals = {}
            vals['code'] = "hpusa.gift.voucher"
            vals['name'] = "Gift Voucher"
            vals['number_next'] = 1
            vals['implementation'] = "standard"
            vals['company_id'] = 1
            vals['padding'] = 5
            vals['number_increment'] = 1
            vals['prefix'] = "GV"
            vals['active'] = True
            sequence_obj.create(cr,1,vals) 
           
hpusa_insert_sequence()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
