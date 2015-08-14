import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta

class manufacturing_order(osv.osv):
    _inherit = "mrp.production"

    _columns = {
        'purchase_id_master': fields.one2many('purchase.order','mrp_id','Purchase Order'),
    }
manufacturing_order()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
            'mrp_id': fields.many2one('mrp.production','Manufacturing Order'),
            'sale_id': fields.many2one('sale.order','Sale Order'),
            'pickup_date': fields.date('Pick-up Date'),
            'related_po': fields.many2one('purchase.order','Related Order'), 
        }

    def create(self, cr, uid, ids, context=None):
        if 'mrp_id' in ids:
            mrp_id = self.pool.get('mrp.production').browse(cr,uid,ids['mrp_id'],context=context)
            if mrp_id.so_id:
                if not 'sale_id' in ids:
                    ids['sale_id'] = mrp_id.so_id.id
        return super(purchase_order, self).create(cr, uid, ids, context)

purchase_order()