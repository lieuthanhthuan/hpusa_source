import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class res_partners(osv.osv):
    _inherit = "res.partner"
    _columns = {

        'is_agent_cooperate': fields.boolean('Is Affiliate Or A.R'),
        'option_choose': fields.selection([('affiliate', 'Affiliate '),('ar', 'Authorized Representative')],'Affiliate Or A.R'),
        'refer_from':fields.many2one('res.partner','Refer from'),
        'ticket_master':fields.one2many('ticket.referafriend','contact_id','Voucher Given'),
    }
    _defaults = {
        'option_choose': 'affiliate',

    }

    def create(self, cr, uid, vals, context=None):
        if not 'customer_name_id' is False:
            user =  self.pool.get('res.partner').browse(cr, uid, uid, context=context)
            company = user.company_id.name
            vals['customer_name_id'] =company +"-"+self.pool.get('ir.sequence').get(
                    cr, SUPERUSER_ID, 'res.partner')

        return super(res_partners, self).create(cr, uid, vals, context)

res_partners()

class ticket_refer_a_friend(osv.osv):
    _name= "ticket.referafriend"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={

            'contact_id': fields.many2one('res.partner','Affiliate Or A.R'),
            'refer_ids_master': fields.one2many('referafriend.issue','ticket_refer','Issue By'),
            'name': fields.char('Voucher Name', size=16, required=True),
            'quantity': fields.integer('Quantity given',required=True),
            'used_quantity':fields.integer('Used Quantity', size=16 ),
            'giving_date': fields.date('Given on date', size=16, required=True),
            'date_to': fields.date('Expiration Date', size=16),
               }
    _defaults = {
        'giving_date': fields.date.context_today,
        'name': 'Refer-A-Friend',
        'quantity':10,
    }

    def action_update(self,cr,uid,ids,context=None):
        refer_partners = self.pool.get('referafriend.issue').search(cr, uid, [('ticket_refer','=',ids)], context=context)
        self.write(cr,uid,ids,{'used_quantity': len(refer_partners)})
        cr.execute('select contact_id from ticket_referafriend where id = '+ str(ids[0]))
        t= cr.fetchall()
        root = t[0][0]
        if root:
            for partner in refer_partners:
                part_ner_id = self.pool.get('referafriend.issue').browse(cr,uid,partner,context=context)
                sql = 'update res_partner set refer_from ='+ str(root) +' where id = '+ str(part_ner_id.refer_ids.id)
                cr.execute(sql)
        return True
ticket_refer_a_friend()

class refer_a_friend_issue(osv.osv):
    _name= "referafriend.issue"
    _description = "Issue By"
    _columns={
       'phone': fields.char('Phone'),
       'mobile': fields.char('Mobile Phone'),
       'customer_id':fields.char('Customer ID'),
       'ticket_refer': fields.many2one('ticket.referafriend','Issue By'),
       'refer_ids': fields.many2one('res.partner','issue_by','Issue By'),
      }
    def onchange_partner_id(self,cr, uid, ids, refer_ids , context=None):
        partner = self.pool.get('res.partner').browse(cr,uid,refer_ids,context=context)
        value={
               'phone':partner.phone,
               'mobile':partner.mobile,
               'customer_id':partner.customer_name_id,
               }
        return {'value': value}

refer_a_friend_issue()


