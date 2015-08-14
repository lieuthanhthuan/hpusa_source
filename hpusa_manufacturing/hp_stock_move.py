import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc


class stock_picking(osv.osv):
    _inherit = "stock.picking" 
    _columns = {
        'receiver': fields.many2one('hr.employee', 'Receiver'),
        'shipper': fields.many2one('hr.employee', 'Shipper'),
        'wo_delivery_id': fields.many2one('mrp.production.workcenter.line', 'wo_delivery_id'),
        'wo_return_id': fields.many2one('mrp.production.workcenter.line', 'wo_return_id'),
        'wo_lost_id': fields.many2one('mrp.production.workcenter.line', 'wo_lost_id'),
        'hp_transfer_type': fields.selection([('delivery', 'Delivery'),
                                      ('return', 'Return'),
                                      ('lost', 'Lost'),
                                      ('ship', 'Shipping'),
                                     ],'Transfer Type'),
    }
stock_picking()    

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in" 
    _columns = {
        'receiver': fields.many2one('hr.employee', 'Receiver'),
    }
stock_picking_in() 


class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out" 
    _columns = {
        'shipper': fields.many2one('hr.employee', 'Shipper'),
    }
stock_picking_out() 

class stock_move(osv.osv):
    _inherit = "stock.move" 
    
    _columns = {
        'returned': fields.boolean('Return'),
        'weight_mo': fields.float('Weight MO',digits_compute=dp.get_precision('Stock Weight')),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
        'note': fields.text('Note'),
        'hp_transfer_type': fields.selection([('delivery', 'Delivery'),
                                      ('return', 'Return'),
                                      ('lost', 'Lost'),
                                     ],'Transfer Type'), 
    }
    def action_return(self, cr, uid, ids, quantity, location_id, weight_mo, weight_mo_unit, context=None):
        #quantity should in MOVE UOM
        if quantity <= 0:
            raise osv.except_osv(_('Warning!'), _('Please provide a positive quantity to return.'))
        res = []
        for move in self.browse(cr, uid, ids, context=context):
            source_location = move.location_id
            if move.state == 'done':
                source_location = move.location_dest_id
            if source_location.usage != 'internal':
                #restrict to scrap from a virtual location because it's meaningless and it may introduce errors in stock ('creating' new products from nowhere)
                raise osv.except_osv(_('Error!'), _('Forbidden operation: it is not allowed to return products from a virtual location.'))
            move_qty = move.product_qty
            uos_qty = quantity / move_qty * move.product_uos_qty
            default_val = {
                'location_id': source_location.id,
                'product_qty': quantity,
                'product_uos_qty': uos_qty,
                'state': move.state,
                'returned': True,
                'weight_mo': weight_mo,
                'weight_mo_unit': weight_mo_unit,
                'name': 'Return' + move.product_id.name,
                'location_dest_id': location_id,
                'tracking_id': move.tracking_id.id,
                'prodlot_id': move.prodlot_id.id,
            }
            new_move = self.copy(cr, uid, move.id, default_val)
            res += [new_move]
            product_obj = self.pool.get('product.product')
            for product in product_obj.browse(cr, uid, [move.product_id.id], context=context):
                if move.picking_id:
                    uom = product.uom_id.name if product.uom_id else ''
                    message = _("%s %s %s has been <b>return.") % (quantity, uom, product.name)
                    move.picking_id.message_post(body=message)
        self.action_done(cr, uid, res, context=context)
        return res
    
    def action_consume1(self, cr, uid, ids, quantity, location_id, weight_mo , weight_mo_unit , context=None):
        if context is None:
            context = {}
        if quantity <= 0:
            raise osv.except_osv(_('Warning!'), _('Please provide proper quantity.'))
        res = []
        for move in self.browse(cr, uid, ids, context=context):
            move_qty = move.product_qty
            if move_qty <= 0:
                raise osv.except_osv(_('Error!'), _('Cannot consume a move with negative or zero quantity.'))
            quantity_rest = move.product_qty
            quantity_rest -= quantity
            uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
            if quantity_rest <= 0:
                quantity_rest = 0
                uos_qty_rest = 0
                quantity = move.product_qty

            uos_qty = quantity / move_qty * move.product_uos_qty
            if quantity_rest > 0:
                default_val = {
                    'product_qty': quantity,
                    'product_uos_qty': uos_qty,
                    'weight_mo': weight_mo,
                    'weight_mo_unit': weight_mo_unit,
                    'state': move.state,
                    'location_id': location_id or move.location_id.id,
                }
                current_move = self.copy(cr, uid, move.id, default_val)
                res += [current_move]
                update_val = {}
                update_val['product_qty'] = quantity_rest
                update_val['product_uos_qty'] = uos_qty_rest
                self.write(cr, uid, [move.id], update_val)

            else:
                quantity_rest = quantity
                uos_qty_rest =  uos_qty
                res += [move.id]
                update_val = {
                        'product_qty' : quantity_rest,
                        'product_uos_qty' : uos_qty_rest,
                        'location_id': location_id or move.location_id.id,
                        'weight_mo': weight_mo,
                        'weight_mo_unit': weight_mo_unit,
                }
                self.write(cr, uid, [move.id], update_val)
        self.action_done(cr, uid, res, context=context)
        print 'abc', res
        return res
        
    def action_scrap(self, cr, uid, ids, quantity, location_id, weight_mo, weight_mo_unit, context=None):
        """ Move the scrap/damaged product into scrap location
        @param cr: the database cursor
        @param uid: the user id
        @param ids: ids of stock move object to be scrapped
        @param quantity : specify scrap qty
        @param location_id : specify scrap location
        @param context: context arguments
        @return: Scraped lines
        """
        #quantity should in MOVE UOM
        if quantity <= 0:
            raise osv.except_osv(_('Warning!'), _('Please provide a positive quantity to scrap.'))
        res = []
        for move in self.browse(cr, uid, ids, context=context):
            source_location = move.location_id
            if move.state == 'done':
                source_location = move.location_dest_id
            if source_location.usage != 'internal':
                #restrict to scrap from a virtual location because it's meaningless and it may introduce errors in stock ('creating' new products from nowhere)
                raise osv.except_osv(_('Error!'), _('Forbidden operation: it is not allowed to scrap products from a virtual location.'))
            move_qty = move.product_qty
            uos_qty = quantity / move_qty * move.product_uos_qty
            default_val = {
                'location_id': source_location.id,
                'product_qty': quantity,
                'product_uos_qty': uos_qty,
                'state': move.state,
                'scrapped': True,
                'weight_mo': weight_mo,
                'weight_mo_unit': weight_mo_unit,
                'location_dest_id': location_id,
                'tracking_id': move.tracking_id.id,
                'prodlot_id': move.prodlot_id.id,
            }
            new_move = self.copy(cr, uid, move.id, default_val)

            res += [new_move]
            product_obj = self.pool.get('product.product')
            for product in product_obj.browse(cr, uid, [move.product_id.id], context=context):
                if move.picking_id:
                    uom = product.uom_id.name if product.uom_id else ''
                    message = _("%s %s %s has been <b>moved to</b> scrap.") % (quantity, uom, product.name)
                    move.picking_id.message_post(body=message)
        
        self.action_done(cr, uid, res, context=context)
        return res 
    

stock_move()   
class stock_move_consume(osv.osv_memory):
    _inherit = "stock.move.consume"
    _columns = {
        'weight_mo': fields.float('Weight MO'),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
    }
    
    def do_move_consume(self, cr, uid, ids, context=None):
        """ To move consumed products
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        move_ids = context['active_ids']
        for data in self.browse(cr, uid, ids, context=context):
            id = move_obj.action_consume1(cr, uid, move_ids,
                             data.product_qty, data.location_id.id, data.weight_mo, data.weight_mo_unit and data.weight_mo_unit.id or False,
                             context=context)
#             if move_ids:
#                 sql = '''SELECT production_id FROM mrp_production_move_ids WHERE move_id = %s'''%(move_ids[0])
#                 cr.execute(sql)
#                 id = [399]
#                 result = cr.dictfetchall()
#                 if result:
#                     print result[0]['production_id'], 'sssss', id
#                     sql = '''INSERT INTO mrp_production_move_ids VALUES(%s,%s)'''%(result[0]['production_id'], id[0])
#                     cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}
stock_move_consume()

class stock_move_scrap(osv.osv_memory):
    _inherit = "stock.move.scrap"
    _columns = {
        'weight_mo': fields.float('Weight MO'),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
    }
    def move_scrap(self, cr, uid, ids, context=None):
        """ To move scrapped products
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        move_ids = context['active_ids']
        for data in self.browse(cr, uid, ids):
            id = move_obj.action_scrap(cr, uid, move_ids,
                             data.product_qty, data.location_id.id, data.weight_mo, data.weight_mo_unit and data.weight_mo_unit.id or False,
                             context=context)
            move = context.get('active_ids', [])
            if move:
                sql = '''SELECT production_id FROM mrp_production_move_ids WHERE move_id = %s'''%(move[0])
                cr.execute(sql)
                result = cr.dictfetchall()
                if result:
                    sql = '''INSERT INTO mrp_production_move_ids VALUES(%s,%s)'''%(result[0]['production_id'], id[0])
                    cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}
stock_move_scrap()






