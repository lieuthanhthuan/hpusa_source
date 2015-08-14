from openerp.osv import fields, osv
from openerp.tools.translate import _
import time

class sale_order(osv.osv):
    _inherit = "sale.order"

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        cr.commit()
        orders = self.browse(cr, uid, ids)
        for order in orders:
            if order.date_of_delivery ==False:
                date_of_delivery = time.strftime("%m/%d/%Y")
                self.write(cr, uid, order.id, {'date_of_delivery': date_of_delivery})
		print order.id
                cr.commit()
        return True

    _columns = {
        'date_of_delivery' : fields.related('picking_ids','date_done',type="date", relation="stock.picking.out", string="Delivery Date",stored=True),
    }
sale_order()

