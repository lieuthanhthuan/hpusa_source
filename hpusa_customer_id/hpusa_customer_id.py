from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import openerp.exceptions

class res_partners(osv.osv):
    _inherit = "res.partner"

    def create(self, cr, uid, vals, context=None):
        if vals['is_company'] is False:
            if vals['customer_id'] is False:
                user =  self.pool.get('res.users').browse(cr, uid, uid, context=context)
                company = user.company_id.name
                print 'Company name:' + user.company_id.name
                print 'User name: '+ str(uid)
    
                sequence="";
                sequence= self.pool.get('ir.sequence').get(
                        cr, SUPERUSER_ID, 'res.partner')
                if(sequence != ""):
                    vals['customer_id'] =company +"-"+sequence
                else:
                    raise osv.except_osv('Sequence not ready', 'Please add sequence for Partner')
            
        return super(res_partners, self).create(cr, uid, vals, context)

    def action_update(self,cr,uid,ids,context=None ):
        companys= self.pool.get('res.company').search(cr, uid, [('id','>=',0)], context=context)

        for company_id in companys:
            company= self.pool.get('res.company').browse(cr,uid,company_id,context=None)
            print 'Company Name:' + company.name
            partners = self.search(cr, uid, [('company_id','=',company.id)], context=None)

            for partner_id in partners:
                partner = self.browse(cr, uid, partner_id, context=context)
                print 'Partner Name:' + partner.name
                customer_id=""
                if partner.id >=1 and partner.id <10:
                    customer_id =str(company.name) +"-" + "0000" + str(partner.id)
                elif partner.id >=10 and partner.id <100:
                    customer_id =str(company.name) +"-" + "000" + str(partner.id)
                elif partner.id >=100 and partner.id <1000:
                    customer_id =str(company.name) +"-" + "00"+ str(partner.id)
                elif partner.id >=1000 and partner.id <10000:
                    customer_id =str(company.name) +"-" + "0" + str(partner.id)
                elif partner.id >=10000 and partner.id <1000000:
                    customer_id =str(company.name) +"-"+str(partner.id)
                self.write(cr, uid, [partner_id], {'customer_id': str(customer_id)})
        return True

    _columns = {
        'customer_id' : fields.char(string="Customer ID",size=64),
    }

res_partners()

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    _columns = {
        'customer_name_id' : fields.related('partner_id','customer_id',type="char", relation="res.partner", string="Customer ID", readonly=True,stored=True)
    }
crm_lead()
