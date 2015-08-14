import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'code': fields.char('Code', size=16),
        'option_choose': fields.selection([('agent', 'Agent'),('cooperate', 'Cooperate')],'Agent/Cooperate'),  
    }
    
    def onchang_option_choose(self, cr, uid, ids, option, context = None):
        if option == 'agent':
            sequence_ids = self.pool.get('ir.sequence').search(cr, uid, [('name','=','Sequence Agent')])
            sequence_name = self.pool.get('ir.sequence')._next(cr, SUPERUSER_ID, sequence_ids)
            return {'value': {'name': 'DDUQ-','code': sequence_name}}
        elif option == 'cooperate':
            sequence_ids = self.pool.get('ir.sequence').search(cr, uid, [('name','=','Sequence Cooperate')])
            sequence_name = self.pool.get('ir.sequence')._next(cr, SUPERUSER_ID, sequence_ids)
            return {'value': {'name': 'CTV-','code': sequence_name}}
        else:
            return {'value': {'name': '','code': ''}}
        
class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def _get_name(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user.code:
            return user.code + '-' 
        else:
            return ''
    
    def _get_sale_person(self, cr, uid, context=None):  
        return uid
    
    _defaults = {
        'name': _get_name,
    }

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'account_id': fields.many2one('account.account', 'Account', ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
    }
account_invoice_line()  
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def _get_is_agent_cooperate(self, cr, uid, ids ,field_name, arg, context = None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        res = {}
        for obj in self.browse(cr, uid, ids):
            if not user.code:
                res[obj.id] = False
            else:
                res[obj.id] = True
        return res
    
    _columns = {
        'is_agent_cooperate':fields.function(_get_is_agent_cooperate,type='boolean',string='Agent Cooperate'),
    }
    
    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        amount = 0
        sql = ''' SELECT * FROM sale_order_invoice_rel rel 
                  LEFT JOIN sale_order ord ON(ord.id = rel.order_id)
                  LEFT JOIN res_users us ON(us.id = ord.user_id)
                  WHERE rel.invoice_id = %s AND (us.option_choose = 'agent' OR us.option_choose = 'cooperate')'''%(ids[0])
        cr.execute(sql)
        result = cr.dictfetchall()
        flag = False
        if result and inv.amount_total - inv.residual == 0:
            amount = inv.type in ('out_refund', 'in_refund') and -inv.residual * 0.3 or inv.residual * 0.3
            flag = True
        else:
            amount = inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': amount,
                'default_reference': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': ids[0],
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'agent_cooperate': flag,
                'amount_origin': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
            }
        }

    
class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        context = context or {}
        amount_origin = context.get('amount_origin', 0.0)
        amount = self.browse(cr, uid, ids[0]).amount
        if context.get('agent_cooperate', False) == True:
            if amount < amount_origin * 0.3:
                raise osv.except_osv(_('Error!'), _('compulsory payment of 30 %'))
            inv = context.get('invoice_id', False)
#             if inv:
#                 self.pool.get('account.invoice').write(cr, uid, [inv], {'state': 'paid'})
        wf_service = netsvc.LocalService("workflow")
        for vid in ids:
            wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
        return {'type': 'ir.actions.act_window_close'}    
    
    
class product_product(osv.osv):
    _inherit = "product.product"
    
    def onchang_option_choose(self, cr, uid, ids, option, context = None):
        if option == 'diamon':
            return {'value': {'maximum_discount': 2.0}}
        elif option == 'jewelry':
            return {'value': {'maximum_discount': 8.0}}
        else:
            return {'value': {'maximum_discount': 0.0}}