from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):

    _name="stock.picking"
    _inherit=['stock.picking','mail.thread', 'ir.needaction_mixin']
 
stock_picking()
