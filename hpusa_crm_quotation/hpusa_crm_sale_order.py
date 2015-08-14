from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import openerp.exceptions

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    def action_view_so(self, cr, uid, ids, context=None):
        ids_so = []
        for obj in self.browse(cr, uid, ids):
            ids_so = self.pool.get('sale.order').search(cr, uid, [('partner_id','=',obj.partner_id.id)])
        if not ids_so:
            raise osv.except_osv(_('Error!'), _('There is no Sale order!'))
        mod_obj = self.pool.get('ir.model.data')

        # call action view so
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'hpusa_crm_quotation', 'hpusa_crm_open_so')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=None)[0]
        result['context'] = {'group_by': None, 'default_partner_id': obj.partner_id.id, 'search_default_partner_id': obj.partner_id.id}
        return result
crm_lead()