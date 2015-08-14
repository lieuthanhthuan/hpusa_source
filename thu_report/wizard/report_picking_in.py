# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Vision Software (<http://visoftware.com>). All Rights Reserved
#
##############################################################################
from dateutil import relativedelta 
import time
from datetime import datetime
from datetime import timedelta
from openerp.osv import fields, osv, orm
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
  
    
class report_report_picking_wizard(osv.osv_memory):
    _name = 'report.picking.in'      
    _columns = {
            'partner_id': fields.many2one('res.partner','Supplier',required=True),
            'date_from': fields.date("Dated from"),
            'date_to': fields.date("To"),
       }
    _defaults={  
              'date_from':  lambda *a: time.strftime('%Y-%m-01'),
              'date_to': lambda *a:str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]  , 
    }  
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}                        
        res = self.read(cr, uid, ids, ['date_from','date_to','partner_id'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        datas['date'] = time.strftime('%Y-%m-%d'),
        datas['line'] = self.line(cr, uid, res)
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        datas['company'] = {'name':company.name, 'street': company.street, 'city': company.city, 'country': company.country_id.name}
        datas['model'] = 'report.picking.in'   
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_picking_in',
            'datas'         : datas,
       }    
    def line(self, cr, uid, form):
        res = []
#         sql = ''' SELECT po.name as po_name, p.name as product_name, pk.name as picking_name, cu.name as cu_name, uom.name as uom, line.product_qty as product_quantity, st.product_qty as input_quantity, st.date as date, line.price_unit as price_unit FROM purchase_order po
#                     LEFT JOIN purchase_order_line line ON(line.order_id = po.id)
#                     LEFT JOIN stock_move st ON(st.purchase_line_id = line.id)
#                     LEFT JOIN product_template p ON(p.id = line.product_id)
#                     LEFT JOIN stock_picking pk ON(pk.id = st.picking_id)
#                     LEFT JOIN product_uom uom ON(uom.id = st.product_uom)
#                     LEFT JOIN res_currency cu ON(cu.id = po.currency_id)
#                     WHERE st.state = 'done' AND po.partner_id = %s AND st.date >= '%s' AND st.date <= '%s' '''%(form['partner_id'][0],form['date_from'],form['date_to'])
#         cr.execute(sql)     
#         print sql   
        result = cr.dictfetchall()  
        for i in result:     
            res.append({
                        'po_name': 's',
                        'product_name' : 'ssss',
                        'picking_name' : 'sdsd',
                        'uom' : 'sssss',
                        'cu_name' : 'sssss',
                        'product_quantity': 'sssss',
                        'input_quantity' : 'ssas',
                        'date': 'sa',
                        'price_unit': 'sdsdsd',
                        'total': '0',
                        })       
        
        return res
report_report_picking_wizard()

openoffice_report.openoffice_report(
    'report.report_picking_in',
    'report.picking.in',
    parser=report_report_picking_wizard
) 





