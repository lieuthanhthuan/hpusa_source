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

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.addons.base_status.base_stage import base_stage
from openerp.addons.resource.faces import task as Task

class crm_case_section(osv.osv):
    """ Model for sales teams. """
    _inherit = "crm.case.section"
    _columns = {
            'team_lead_ids': fields.many2many('res.users', 'team_lead_ids_rel', 'ssection_id', 'uid','Team Leader'),
                }    
class crm_lead(osv.osv):
    _inherit = 'crm.lead'  
	
    def onchange_salesteam(self, cr, uid, ids, salesteam_id):  
        saleteam = self.pool.get('crm.case.section')  
        if not salesteam_id:
                return {'value': {                
                	'involvestaff_ids': False,
                	}}
        ids = []
        for id in saleteam .browse(cr, uid, salesteam_id).member_ids:
            ids.append(id.id)  
        return {'value': {
            	  'involvestaff_ids': ids or False,
            }}
    _columns = {
	     'ownermanager_ids': fields.many2many('res.users', 'crm_lead_user_ownermanager', 'crm_lead_id', 'uid','Owner Manager'),
	     'involvestaff_ids': fields.many2many('res.users', 'crm_lead_user_involvestaff', 'crm_lead_id', 'uid','Involve Owner'),          
            'lead_source_id': fields.many2one('crm.lead.source', 'Lead Source'),
            'keyword_id': fields.many2one('crm.keyword', 'Keyword'),
            'lead_date': fields.datetime('Lead Date' ), 
            'contact_name': fields.char('Customer Name', size=64),
            'partner_name': fields.char("Contact Name", size=64,help='The name of the future partner company that will be created while converting the lead into opportunity', select=1),
            'remark':fields.text('Remark'), 
		 }   

crm_lead()
class sale_order(osv.osv):
    _inherit = 'sale.order'  
	
    _columns = {
	     'ownermanager_ids': fields.many2many('res.users', 'sale_order_user_ownermanager', 'sale_order_id', 'uid','Owner Manager'),
	     'involvestaff_ids': fields.many2many('res.users', 'sale_order_user_involvestaff', 'sale_order_id', 'uid','Involve Owner'),          
           
		 }   

sale_order()
class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'  
	
    _columns = {
	     'ownermanager_ids': fields.many2many('res.users','account_analytic_account_user_ownermanager', 'account_analytic_account_id', 'uid','Owner Manager'),
	     'involvestaff_ids': fields.many2many('res.users','account_analytic_account_user_involvestaff', 'account_analytic_account_id', 'uid','Involve Owner'),          
           
		 }   

account_analytic_account()
class crm_phonecall(osv.osv):
    _inherit = 'crm.phonecall'  
	
    _columns = {
	     'ownermanager_ids': fields.many2many('res.users','crm_phonecall_user_ownermanager', 'crm_phonecall_id', 'uid','Owner Manager'),
	     'involvestaff_ids': fields.many2many('res.users','crm_phonecall_user_involvestaff', 'crm_phonecall_id', 'uid','Involve Owner'),          
           
		 }   

crm_phonecall()
class crm_vip_program(osv.osv):
    _name = "crm.vip.program"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'customer_ids':fields.one2many('res.partner', 'vip_program_id','Customer Members'),
        
          
    }

crm_vip_program()
class crm_gifts_given(osv.osv):
    _name = "crm.gifts.given"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'customer_ids':fields.one2many('res.partner', 'gifts_given_id','Customer Members'),
        
          
    }

crm_gifts_given()
class res_partner(osv.osv):
    _inherit = 'res.partner'    
    
    def onchange_salesteam(self, cr, uid, ids, salesteam_id):  
        saleteam = self.pool.get('crm.case.section')  
        if not salesteam_id:
                return {'value': {                
                	'involvestaff_ids': False,
                	}}
        ids = []
        for id in saleteam .browse(cr, uid, salesteam_id).member_ids:
            ids.append(id.id)  
        return {'value': {
            	  'involvestaff_ids': ids or False,
            }}

    _columns = {
                'vip_program_id': fields.many2one('crm.vip.program', 'Vip Program'),
                'gifts_given_id': fields.many2one('crm.gifts.given', 'Gifts Given'),
                'money_gifts': fields.char('Gifts Amount', size=2056),
                'births_date': fields.date('Births Date'),  
                'original_join_date': fields.datetime('Original Join Date' ), 
                'expiration_date': fields.datetime('Expiration Date' ),
                'refer_a_friend_date': fields.datetime('Refer-a-Friend was given on' ),
                'refer_a_friend_coupon_date': fields.datetime('Refer-a-Friend coupon was claimed on' ),
                'customer_name_id':fields.char('Customer ID', size=1028),
                'remark':fields.text('Remark'),         	  		  	
   		 }
res_partner()

class crm_lead_source(osv.osv):
    _name = "crm.lead.source"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),       
    }

crm_lead_source()
class crm_keyword(osv.osv):
    _name = "crm.keyword"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),       
    }

crm_keyword()

class note_note(osv.osv):
    _inherit = 'note.note'   
    
    _columns = {
                'user_id': fields.many2one('res.users', 'Owner'),
                'company_id': fields.many2one('res.company', 'Company'),
            }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'note.note', context=c),
        }
note_note()  

class marketing_campaign_segment(osv.osv):
    _inherit = 'marketing.campaign.segment'   
    
    _columns = {
                'user_id': fields.many2one('res.users', 'Owner'),
                'company_id': fields.many2one('res.company', 'Company'),
            }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'marketing.campaign.segment', context=c),
        }
marketing_campaign_segment() 

class marketing_campaign_workitem(osv.osv):
    _inherit = 'marketing.campaign.workitem'   
    
    _columns = {
                'user_id': fields.many2one('res.users', 'Owner'),
                'company_id': fields.many2one('res.company', 'Company'),
            }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'marketing.campaign.workitem', context=c),
        }
marketing_campaign_workitem()

class marketing_campaign(osv.osv):
    _inherit = 'marketing.campaign'   
    
    _columns = {
                'user_id': fields.many2one('res.users', 'Owner'),
                'company_id': fields.many2one('res.company', 'Company'),
            }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'marketing.campaign', context=c),
        }
marketing_campaign() 





