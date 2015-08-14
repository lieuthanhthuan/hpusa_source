import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class stock_moves(osv.osv):
    _inherit = "stock.move"

    def onchange_percent(self,cr, uid, ids, hp_weight, hp_percent ,  context=None):
        context = context or {}
        quantity = round((hp_weight*hp_percent)/75.0,3)
        value={
            'product_qty': quantity,
               }
        return {'value': value}

    _columns = {

        'hp_weight': fields.integer('Weight'),
        'hp_percent': fields.float('Percent', size=16),
    }
stock_moves()
