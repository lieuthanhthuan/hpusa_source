import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime

class mrp_repair(osv.osv):
    _inherit = "mrp.repair"
    _columns = {
        'state': fields.selection([
            ('draft','Quotation'),
            ('cancel','Cancelled'),
            ('confirmed','Confirmed'),
            ('under_repair','Under Repair'),
            ('ready','Ready to Repair'),
            ('2binvoiced','To be Invoiced'),
            ('invoice_except','Invoice Exception'),
            ('done','Repaired'),
            ('send_manager','Send to Manager'),
            ('approve','Approve'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed repair order. \
            \n* The \'Confirmed\' status is used when a user confirms the repair order. \
            \n* The \'Ready to Repair\' status is used to start to repairing, user can start repairing only after repair order is confirmed. \
            \n* The \'To be Invoiced\' status is used to generate the invoice before or after repairing done. \
            \n* The \'Done\' status is set when repairing is completed.\
            \n* The \'Cancelled\' status is used when user cancel repair order.'),
        'receipt_size': fields.float('Receipt Size'),
        'new_size': fields.float('New Size'),
        'receipt_weight': fields.float('Receipt Weight'),
        'finish_weight': fields.float('Finish Weight'),
        'employee_id': fields.many2one('hr.employee', 'Worker'),
        'date': fields.date('Date'),
                
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    def send_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'send_manager' })
        
        
    def action_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve' })
        
    def action_repair_done(self, cr, uid, ids, context=None):
        """ Creates stock move and picking for repair order.
        @return: Picking ids.
        """
        res = {}
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        repair_line_obj = self.pool.get('mrp.repair.line')
        seq_obj = self.pool.get('ir.sequence')
        pick_obj = self.pool.get('stock.picking')
        for repair in self.browse(cr, uid, ids, context=context):
            for move in repair.operations:
                move_id = move_obj.create(cr, uid, {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'product_qty': move.product_uom_qty,
                    'origin': repair.name,
                    'product_uom': move.product_uom.id,
                    'partner_id': repair.address_id and repair.address_id.id or False,
                    'location_id': move.location_id.id,
                    'weight_mo': move.weight_mo,
                    'weight_mo_unit': move.weight_mo_unit and move.weight_mo_unit.id or False,
                    'location_dest_id': move.location_dest_id.id,
                    'tracking_id': False,
                    'prodlot_id': move.prodlot_id and move.prodlot_id.id or False,
                    'state': 'done',
                })
                repair_line_obj.write(cr, uid, [move.id], {'move_id': move_id, 'state': 'done'}, context=context)
            if repair.deliver_bool:
                pick_name = seq_obj.get(cr, uid, 'stock.picking.out')
                picking = pick_obj.create(cr, uid, {
                    'name': pick_name,
                    'origin': repair.name,
                    'state': 'draft',
                    'move_type': 'one',
                    'partner_id': repair.address_id and repair.address_id.id or False,
                    'note': repair.internal_notes,
                    'invoice_state': 'none',
                    'type': 'out',
                })
                move_id = move_obj.create(cr, uid, {
                    'name': repair.name,
                    'picking_id': picking,
                    'product_id': repair.product_id.id,
                    'product_uom': repair.product_id.uom_id.id,
                    'prodlot_id': repair.prodlot_id and repair.prodlot_id.id or False,
                    'partner_id': repair.address_id and repair.address_id.id or False,
                    'location_id': repair.location_id.id,
                    'location_dest_id': repair.location_dest_id.id,
                    'tracking_id': False,
                    'state': 'assigned',
                })
                wf_service.trg_validate(uid, 'stock.picking', picking, 'button_confirm', cr)
                self.write(cr, uid, [repair.id], {'state': 'done', 'picking_id': picking})
                res[repair.id] = picking
            else:
                self.write(cr, uid, [repair.id], {'state': 'done'})
        return res
        
class mrp_repair_line(osv.osv):
    _inherit = "mrp.repair.line" 
    
    _columns = {
        'weight_mo': fields.float('Weight MO'),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
    }
        