import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
        'work_order': fields.char('Work Center'), # hpusa configure
        'work_order_status': fields.char('Status'), # hpusa configure
    }
sale_order_line()

