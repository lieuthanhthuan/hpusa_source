# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://generalsolutions.vn>). All Rights Reserved
#
##############################################################################
from datetime import datetime, date
from lxml import etree
import time
import openerp.addons.decimal_precision as dp

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
from openerp.addons.base_status.base_stage import base_stage
from openerp.addons.resource.faces import task as Task

class sale_order(osv.osv):
    _inherit = 'sale.order'   

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

	# total check
    def _amount_all_check(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                if line.check_ == True:
                    val1 += line.price_subtotal
                    val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id] = cur_obj.round(cr, uid, cur, val)+ cur_obj.round(cr, uid, cur, val1)
        return res
    
    def _total_discount(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            qty = 0
            for item in line.order_line:
                if item.check_ == True:
                    qty += item.dicount_number
            res[line.id] = qty
        return res 
        
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()


    def button_dummy(self, cr, uid, ids, context=None):
        pricelist_obj = self.pool.get('product.pricelist')
        order_line = self.pool.get('sale.order.line')
        bom_obj = self.pool.get('mrp.bom')
        product_uom = self.pool.get('product.uom')
        
        # hpusa added 28-05-2015
        pricelist_version = self.pool.get('product.pricelist.version')
        currency_obj = self.pool.get('res.currency')
        # hpusa added 28-05-2015
        
        for order in self.browse(cr, uid, ids, context=context):
            for order_line in order.order_line:
                gia = 0
                
                # hpusa added 28-05-2015
                von=0
                # hpusa added 28-05-2015
                
                product_parent = self.pool.get('product.product').browse(cr, uid, order_line.product_id.id, context=context)  
                sql = '''select id from mrp_bom where product_id=%s order by sequence ''' % (product_parent.id)
                cr.execute(sql)
                kq = cr.fetchall()
                if not kq:
                    raise osv.except_osv(_('Cannot Bom !'), _('Please to create bom structure.'))
                bom_id = bom_obj._bom_find(cr, uid, product_parent.id, product_parent.uom_id and product_parent.uom_id.id, [])                
                
                # hpusa added 28-05-2015
                for bom in bom_obj.browse(cr, uid, [bom_id]):
                    for bom_line in bom.bom_lines:
                        pricelist = order.pricelist_id
                        cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                        cost_price = currency_obj.compute(cr, uid,
                                    3, pricelist.currency_id.id,
                                    cost_p, round=False,
                                    context=context)
                        von +=cost_price *bom_line.product_qty
		print 'Gia von:'+ str(von)	
                plist_versions= self.get_price_list_version(cr,uid,ids,pricelist.id,von)
		print 'pricelist version:' + str(plist_versions)
                # hpusa added 28-05-2015
                               
                for bom in bom_obj.browse(cr, uid, [bom_id]):
                    for bom_line in bom.bom_lines:                        
                        pricelist = order.pricelist_id
                        
                        # hpusa added 28-05-2015
                        price_supplier = pricelist_version.hpusa_price_get(cr,uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0,plist_versions, partner=None,context=None)
                        # hpusa added 28-05-2015
                        
                        #gs                   
                        #price_supplier = pricelist_obj.price_get(cr,uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0, partner=None,context=None)  
                        price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist.id], to_uom_id=bom_line.product_uom.id)                                                
                        gia +=price*bom_line.product_qty
                self.pool.get('sale.order.line').write(cr, uid, [order_line.id], {'price_unit': gia})
        return True

# hpusa configures 29-05-2015
    def get_price_list_version(self,cr,uid,ids,price_list,amount,context=None):
        val_return =0
        pricelist_version_ids = self.pool.get('product.pricelist.version').search(cr, uid, [('pricelist_id', '=', price_list)])
        for version_id in pricelist_version_ids:
            version= self.pool.get('product.pricelist.version').browse(cr,uid,version_id)
            if(version.min_amount<= amount and version.max_amount>=amount):
                val_return = version_id
                break
            else:
                val_return = -1
        return val_return
# hpusa configures 29-05-2015

    def get_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            str = {}
            if order.state == 'draft':
                str = '1. Draft Quotation'
            elif order.state == 'waiting_manager':
                str = '2. Waiting Manager'
            elif order.state == 'waiting_director':
                str = '3. Waiting Director'
            elif order.state == 'approved':
                str = '4. Approved'
            elif order.state == 'sent':
                str = '5. Quotation Sent'
            elif order.state == 'progress':
                str = '6. Sales Order'
            elif order.state == 'manual':
                str = '7. Sale to Invoice'
            elif order.state == 'done':
                str = '8. Done'
            elif order.state == 'cancel':
                str = '8. Cancelled'
            elif order.state == 'shipping_except':
                str = 'Shipping Exception'
            elif order.state == 'invoice_except':
                str = 'Invoice Exception'
            elif order.state == 'order_in_process':
                str = 'undefined'
            res[order.id] = str
        return res
                   
    _columns = {     
                 'amount_total_check': fields.function(_amount_all_check, digits_compute=dp.get_precision('Account'), string='Total', help="The total amount."),
                 'ownermanager_ids': fields.many2many('res.users', 'sale_order_user_ownermanager', 'sale_order_id', 'uid','Owner Manager'),
	          'involvestaff_ids': fields.many2many('res.users', 'sale_order_user_involvestaff', 'sale_order_id', 'uid','Involve Owner'),
                 'total_discount':fields.function(_total_discount,type='float',string='Total Discount'),  
                 'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)],'waiting_manager': [('readonly', False)],'waiting_director': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order."), 
                 'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)],'waiting_manager': [('readonly', False)],'waiting_director': [('readonly', False)], 'sent': [('readonly', False)]}),

        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),       
        'hp_state_1':  fields.function(get_state, type='char', string='State', store=True),                                  
	} 

    def action_button_confirm(self, cr, uid, ids, context=None):
        # fetch the partner's id and subscribe the partner to the sale order
	print 'Action Confirm start'
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        document = self.browse(cr, uid, ids[0], context=context)
        partner = document.partner_id
        self.message_unsubscribe(cr, uid, ids, [partner.id], context=context)
	print 'Action Confirm done'
        return res
    
    def action_waiting_manager(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'waiting_manager'})
        return True  
    def action_waiting_director(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'waiting_director'})
        return True
    def action_approve(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'approved'})
        return True 
    def action_refuse_director(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'waiting_manager'})
        return True
    def action_refuse_manager(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    def action_refuse_customer(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'draft'})
        return True	


    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        email_template_obj = self.pool.get('email.template')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id.name
        record_ids = []
        if company == 'HPUSA':
            record_ids = email_template_obj.search(cr, uid, [('name','=','Sales Order - English')], context=context)
        elif company == 'HPVN':
            record_ids = email_template_obj.search(cr, uid, [('name','=','Sales Order - Vietnamese')], context=context)        

        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': record_ids and record_ids[0] or False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']) - line.dicount_number
        return res   
 
 
    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        pricelist_obj = self.pool.get('product.pricelist')
        bom_obj = self.pool.get('mrp.bom')
        product_uom = self.pool.get('product.uom')    
        for object_order in self.browse(cr, uid, ids, context):
            cost_price =0 
            product_parent = self.pool.get('product.product').browse(cr, uid, object_order.product_id.id, context=None) 
            bom_id = bom_obj._bom_find(cr, uid, product_parent.id, product_parent.uom_id and product_parent.uom_id.id, [])    
            for bom in bom_obj.browse(cr, uid, [bom_id]):
                for bom_line in bom.bom_lines:                               
                    pricelist = object_order.order_id.pricelist_id                   
                    currency_obj = self.pool.get('res.currency') 
                    cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                    cost_price +=  bom_line.product_qty * currency_obj.compute(cr, uid,
                                3, pricelist.currency_id.id,
                                cost_p, round=False,
                                context=None)
            res[object_order.id] = cost_price                         
        return res         
 

    _columns = {
         'dicount_number': fields.float('Discount(number)'),  
	  'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),  
         'cost_price': fields.function(_cost_price, string='Cost Price', digits_compute= dp.get_precision('Account')),  
         'check_': fields.boolean('Check'),                                        
    } 
    _defaults = {
        'check_': True,
    }
    _dis_p = 0.0
    _dis_n = 0.0
    def onchange_discount_percent(self, cr, uid, ids, value, price_unit, product_uom_qty,  context=None):
        if value > 0:
            if self._dis_p == 0 or value -  self._dis_p >= 0.005 or value - self._dis_p <= - 0.005:
                val = price_unit * value * product_uom_qty/100.0
                self._dis_p = val
                self._dis_n = val
                return {'value': {'dicount_number': val}}
        if value == 0:
             return {'value': {'dicount_number': 0}}
        return {'value': {'discount': value}}

    def onchange_discount_number(self, cr, uid, ids, value, price_unit, product_uom_qty,  context=None):
        if value > 0:
            if self._dis_n == 0 or value -  self._dis_n >= 0.005 or value -  self._dis_n <= - 0.005:
                if price_unit == 0 or product_uom_qty == 0:
                    return {'value': {'discount': 0}} 
                val = value * 100.0 / (price_unit * product_uom_qty)
                self._dis_n = val
                self._dis_p = val
                return {'value': {'discount': val}} 
        if value == 0:
                return {'value': {'discount': 0}}
        return {'value': {'dicount_number': value}} 
    
    def create(self, cr, uid, vals, context=None):
        if 'price_unit' in vals:
            total = vals['price_unit']
            sale = self.pool.get('sale.order').browse(cr, uid, vals['order_id'], context)
            if sale.pricelist_id.currency_id.name == "VND":
                if total % 5000 > 0:
                    total = int(total/5000) *5000 + 5000
            if sale.pricelist_id.currency_id.name == "USD":
                if total % 5 > 0:
                    total = int(total/5) *5 + 5
            vals['price_unit'] = total
        return super(sale_order_line, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        for item in self.browse(cr, uid, ids):
            if 'price_unit' in vals:
                total = vals['price_unit']
                sale = self.pool.get('sale.order').browse(cr, uid, item.order_id.id, context)
                if sale.pricelist_id.currency_id.name == "VND":
                    if total % 5000 > 0:
                        total = int(total/5000) *5000 + 5000
                if sale.pricelist_id.currency_id.name == "USD":
                    if total % 5 > 0:
                        total = int(total/5) *5 + 5
                vals['price_unit'] = total
            return super(sale_order_line, self).write(cr, uid, [item.id], vals, context)
    
sale_order()


class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        active_ids = context.get('active_ids')
        re = super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)
        for wizard in self.browse(cr, uid, ids, context=context):
            for partner in wizard.partner_ids:
                try:
                    self.pool.get('sale.order').message_unsubscribe(cr, uid, active_ids[0], [partner.id], context=context)
                except Exception:
                    return False
        return re
mail_compose_message()

class invite_wizard(osv.osv_memory):
    _inherit = 'mail.wizard.invite'

    def add_followers(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            model_obj = self.pool.get(wizard.res_model)
            document = model_obj.browse(cr, uid, wizard.res_id, context=context)

            # filter partner_ids to get the new followers, to avoid sending email to already following partners
            new_follower_ids = [p.id for p in wizard.partner_ids if p.id not in document.message_follower_ids]
            model_obj.message_subscribe(cr, uid, [wizard.res_id], new_follower_ids, context=context)
            # send an email
            if wizard.message:
                # add signature
                user_id = self.pool.get("res.users").read(cr, uid, [uid], fields=["signature"], context=context)[0]
                signature = user_id and user_id["signature"] or ''
                if signature:
                    wizard.message = tools.append_content_to_html(wizard.message, signature, plaintext=True, container_tag='div')
                # FIXME 8.0: use notification_email_send, send a wall message and let mail handle email notification + message box
                for follower_id in new_follower_ids:
                    mail_mail = self.pool.get('mail.mail')
                    # the invite wizard should create a private message not related to any object -> no model, no res_id
                    mail_id = mail_mail.create(cr, uid, {
                        'model': wizard.res_model,
                        'res_id': wizard.res_id,
                        'subject': 'Invitation to follow %s' % document.name_get()[0][1],
                        'body_html': '%s' % wizard.message,
                        'auto_delete': True,
                        }, context=context)
                    mail_mail.send(cr, uid, [mail_id], recipient_ids=[follower_id], context=context)
        return {'type': 'ir.actions.act_window_close'}
