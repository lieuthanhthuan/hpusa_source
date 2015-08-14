from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class stock_move_return(osv.osv_memory):
    _name = "stock.move.return"
    _description = "Return Products"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'weight_mo': fields.float('Weight MO'),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
    }
    _defaults = {
        'location_id': lambda *x: False
    }

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = super(stock_move_return, self).default_get(cr, uid, fields, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
        location_obj = self.pool.get('stock.location')
        scrpaed_location_ids = location_obj.search(cr, uid, [('scrap_location','=',False)])

        if 'product_id' in fields:
            res.update({'product_id': move.product_id.id})
        if 'product_uom' in fields:
            res.update({'product_uom': move.product_uom.id})
        if 'product_qty' in fields:
            res.update({'product_qty': move.product_qty})
        if 'weight_mo' in fields:
            res.update({'weight_mo': move.weight_mo})
        if 'weight_mo_unit' in fields:
            res.update({'weight_mo_unit': move.weight_mo_unit and move.weight_mo_unit.id or False})
        if 'location_id' in fields:
            if scrpaed_location_ids:
                res.update({'location_id': scrpaed_location_ids[0]})
            else:
                res.update({'location_id': False})

        return res

    def move_return(self, cr, uid, ids, context=None):
        """ To move returnped products
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
            id = move_obj.action_return(cr, uid, move_ids,
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

stock_move_return()
