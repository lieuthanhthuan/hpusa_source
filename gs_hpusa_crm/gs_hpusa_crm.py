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
            'date_won': fields.date('Won Date' ),
            'contact_name': fields.char('Customer Name', size=64),
            'partner_name': fields.char("Contact Name", size=64,help='The name of the future partner company that will be created while converting the lead into opportunity', select=1),
            'remark':fields.text('Remark'),
            'city': fields.many2one("crm.hpusa.city", 'city'),
		 }
    def case_mark_won(self, cr, uid, ids, context=None):
        res = super(crm_lead,self).case_mark_won( cr, uid, ids, context)
        self.write(cr, uid, ids, {'date_won':time.strftime('%Y-%m-%d'),'stage_id': 7})
        return res

    def onchange_country(self, cr, uid, ids, country_id, context=None):
        if country_id:
            obj = self.pool.get('res.country').browse(cr, uid, country_id, context)
            ids_state = self.pool.get('res.country.state').search(cr, uid, [('country_id','=',obj.id)])
            if ids_state:
                domain = [('id','in', ids_state)]
            return {'domain': {'state_id':domain}}
        return {}

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            obj = self.pool.get('res.country').browse(cr, uid, state_id, context)
            ids_state = self.pool.get('crm.hpusa.city').search(cr, uid, [('state_id','=',obj.id)])
            if ids_state:
                domain = [('id','in', ids_state)]
            return {'domain': {'city':domain}}
        return {}

    def onchange_city(self, cr, uid, ids, city_id, context=None):
        if city_id:
            obj = self.pool.get('crm.hpusa.city').browse(cr, uid, city_id, context)
            return {'value': {'zip': obj.zip}}
        return {}
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
                'warranty': fields.boolean('Lifetime Warranty Customers '),
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
                'city': fields.many2one("crm.hpusa.city", 'city'),
   		 }

    def onchange_country(self, cr, uid, ids, country_id, context=None):
        if country_id:
            obj = self.pool.get('res.country').browse(cr, uid, country_id, context)
            ids_state = self.pool.get('res.country.state').search(cr, uid, [('country_id','=',obj.id)])
            if  ids_state:
                domain = [('id','in', ids_state)]
            return {'value': {'phone': obj.code_mobile, 'mobile': obj.code_mobile}, 'domain': {'state_id':domain}}
        return {}

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            obj = self.pool.get('res.country').browse(cr, uid, state_id, context)
            ids_state = self.pool.get('crm.hpusa.city').search(cr, uid, [('state_id','=',obj.id)])
            domain = [('id','in', ids_state)]
            return {'domain': {'city':domain}}
        return {}
    def onchange_city(self, cr, uid, ids, city_id, context=None):
        if city_id:
            obj = self.pool.get('crm.hpusa.city').browse(cr, uid, city_id, context)
            return {'value': {'zip': obj.zip}}
        return {}


    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        
        address_format = address.country_id and address.country_id.address_format or \
              "%(street)s\n%(street2)s\n %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': address.state_id and address.state_id.code or '',
            'city': address.city and address.city.name or '',
            'state_name': address.state_id and address.state_id.name or '',
            'country_code': address.country_id and address.country_id.code or '',
            'country_name': address.country_id and address.country_id.name or '',
            'company_name': address.parent_id and address.parent_id.name or '',
        }
        address_field = ['title', 'street', 'street2', 'zip']
        for field in address_field :
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

res_partner()

class crm_hpusa_city(osv.osv):
    _name = "crm.hpusa.city"
    _columns = {
        'name': fields.char('City nam',  required=True),
        'code': fields.char('City code',  required=True),
        'zip': fields.char('ZIP'),
        'state_id': fields.many2one("res.country.state", 'State'),
    }
crm_hpusa_city()

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

# hpusa customize 23-04-2015

class hpusa_contact(osv.osv):
    _name="hpusa.contact"
    _description ="Partner"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
                'user_id': fields.many2one('res.users', 'Owner'),
                'representative':fields.many2one('hpusa.contact','Representative',domain=[('is_a_company', '=', False)]),
                'company_id': fields.many2one('res.company', 'Company'),
                'is_a_company': fields.boolean('Is a Company'),
                'job': fields.char('Job position'),
                'active': fields.boolean('Active'),
                'name': fields.char('Contact Name', required=True),
                'phone': fields.char('Phone'),
                'mail': fields.char('Email'),
                'website': fields.char('Website'),
                'fax': fields.char('Fax'),
                'mobile':fields.char('Mobile Phone'),
                'address':fields.char('Address'),
                'description': fields.text('Internal Notes'),
                'categories_id': fields.many2one('hpusa.contact.categories','Categories'),
                'department_id': fields.many2one('hr.department','Department'),
                'involvestaff_ids': fields.many2many('res.users', 'hpusa_contact_user_involvestaff', 'hpusa_contact_id', 'uid','Involve Owner'),
                'page_id': fields.one2many('hpusa.contact.document.page','page_line','Pages'),
            }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'active': True,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hpusa.contact', context=c),
        }
hpusa_contact()

# hpusa customize 23-04-2015
class hpusa_contact_categories(osv.osv):
    _name="hpusa.contact.categories"
    _description ="Contact Categories"
    _columns = {
                'user_id': fields.many2one('res.users', 'Owner'),
                'name': fields.char('Contact Name', required=True),
            }
hpusa_contact_categories()

# hpusa customize 23-04-2015
class contact_document_page(osv.osv):
    _name = "hpusa.contact.document.page"
    _description = "Contact Document Page"
    _order = 'name'

    def _get_page_index(self, cr, uid, page, link=True):
        index = []
        for subpage in page.child_ids:
            index += ["<li>"+ self._get_page_index(cr, uid, subpage) +"</li>"]
        r = ''
        if link:
            r = '<a href="#id=%s">%s</a>'%(page.id,page.name)
        if index:
            r += "<ul>" + "".join(index) + "</ul>"
        return r

    def _get_display_content(self, cr, uid, ids, name, args, context=None):
        res = {}
        for page in self.browse(cr, uid, ids, context=context):
            if page.type == "category":
               #content = self._get_page_index(cr, uid, page, link=False)
               content = page.content
            else:
               content = page.content
            res[page.id] =  content
        return res

# hpusa customize 23-04-2015
    def onchange_parent_id(self, cr, uid, ids, parent_id, content, context=None):
        res = {}
        parent = self.pool.get('document.page').browse(cr, uid, parent_id, context=context)
        res['value'] = {
            'content': parent.content,
            }
        return res
    _columns = {
        'type':fields.selection([('content','Content'), ('category','Category')], 'Type', help="Page type"),

        'name': fields.many2one('document.page', 'Page',required=True),
        'child_ids': fields.one2many('document.page', 'parent_id', 'Children'),

        'content': fields.text("Content"),
        'display_content': fields.function(_get_display_content, string='Displayed Content', type='text'),

        'history_ids': fields.one2many('document.page.history', 'page_id', 'History'),

        'create_date': fields.datetime("Created on", select=True, readonly=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True, readonly=True),
        'write_date': fields.datetime("Modification Date", select=True, readonly=True),
        'write_uid': fields.many2one('res.users', "Last Contributor", select=True),
        'page_line': fields.many2one('hpusa.contact', 'Contact'),
    }
    _defaults = {
        'type':'content',
    }
contact_document_page()