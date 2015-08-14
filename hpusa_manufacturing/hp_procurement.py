# -*- coding: utf-8 -*-
##############################################################################
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc

class procurement_order(osv.osv):
    _inherit = 'procurement.order'   
    _columns = {
        'so_id': fields.many2one('sale.order','MO Planning'), 
        'main_production_id': fields.many2one('mrp.production','Main Production'),
        'parent_id': fields.many2one('mrp.production','Parent'),
    }
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.produce_delay or 0.0)
            newdate = newdate - relativedelta(days=company.manufacturing_lead)
            so = None
            parent = None
            main_mo = None
            if procurement.move_id.sale_line_id:
                so = procurement.move_id.sale_line_id.order_id.id
            else:
                parent = procurement.parent_id and procurement.parent_id.id or False
                main_mo = procurement.main_production_id and procurement.main_production_id.id or False
                so = procurement.so_id and procurement.so_id.id or False
            
            produce_id = production_obj.create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'so_id': so,
                'main_production_id': main_mo,
                'parent_id': parent,
                'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                'location_src_id': procurement.location_id.id,
                'location_dest_id': procurement.location_id.id,
                'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                'move_prod_id': res_id,
                'company_id': procurement.company_id and procurement.company_id.id or False,
            })
            
            res[procurement.id] = produce_id
            
            self.write(cr, uid, [procurement.id], {'state': 'running', 'production_id': produce_id})   
            bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            #add following
            mrp = production_obj.browse(cr, uid, [produce_id][0])
           
                        
            
            if not procurement.move_id.sale_line_id:
                wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
            else:
                production_obj.write(cr, uid, [produce_id], {'main_production_id': produce_id})
            if res_id:
                move_obj.write(cr, uid, [res_id],
                        {'location_id': procurement.location_id.id})
        self.production_order_create_note(cr, uid, ids, context=context)
        return res
   
procurement_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
