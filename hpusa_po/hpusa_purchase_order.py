from openerp.osv import fields, osv
from openerp.tools.translate import _
import time


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        cr.commit()

        return True

purchase_order()

