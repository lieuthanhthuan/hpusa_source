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

_TASK_SCHEDULE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class task(osv.osv):
    _inherit = "project.task"    
    _columns = {
	     'assignedby_id': fields.many2one('res.users', 'Assigned By',track_visibility='onchange'),
	     'reportto_ids': fields.many2many('res.users', 'task_user_reportto', 'task_id', 'uid', 'Report To'),
	     'involvestaff_ids': fields.many2many('res.users', 'task_user_involvestaff', 'task_id', 'uid','Involve Staff'), 
            'phase_name': fields.related('phase_id','name', type='char', readonly=True, size=128, relation='project.phase', store=True, string='Task Phase'),   
            'schedule_id': fields.many2one('project.task.schedule', 'Task Schedule', track_visibility='onchange',domain="['&', ('fold', '=', False), ('project_ids', '=', project_id)]"),       
            'directory_id': fields.many2one('document.directory', 'Directory', select=1, change_default=True), 
            'tags_id': fields.many2one('project.category', 'Tags'), 

		 }



task()
class project(osv.osv):
    _inherit = 'project.project'
    
    _columns = {	     

	     'involvestaff_ids': fields.many2many('res.users', 'project_user_involvestaff', 'project_id', 'uid','Involve Manager'),
            'schedule_ids': fields.many2many('project.task.schedule', 'project_task_schedule_rel', 'project_id', 'schedule_id', 'Tasks Schedule', states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),

		 }

    def _get_schedule_common(self, cr, uid, context):
        ids = self.pool.get('project.task.schedule').search(cr, uid, [('case_default','=',1)], context=context)
        return ids

    _defaults = {        
        'schedule_ids': _get_schedule_common, 
        
    }

project()

class document_file(osv.osv):
    _inherit = 'ir.attachment'  
    
    def _task_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'project.task':                
                result[obj.id] = obj.res_id
        return result
    def _project_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'project.project':                
                result[obj.id] = obj.res_id
        return result

    def _issue_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'project.issue':                
                result[obj.id] = obj.res_id
        return result 

    def _page_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'document.page':                
                result[obj.id] = obj.res_id
        return result

    def _crm_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'crm.lead':                
                result[obj.id] = obj.res_id
        return result 

    def _partner_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'res.partner':                
                result[obj.id] = obj.res_id
        return result 

    def _applicant_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'hr.applicant':                
                result[obj.id] = obj.res_id
        return result
    def _saleorder_auto(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.res_model == 'sale.order':                
                result[obj.id] = obj.res_id
        return result
	
    def onchange_directory(self, cr, uid, ids, parent_id):  
        directory = self.pool.get('document.directory')  
        if not parent_id:
                return {'value': {                
                	'assignedby_ids': False,
                	}}
        ids = []
        for id in directory.browse(cr, uid, parent_id).ownermanager_ids:
            ids.append(id.id)  
        return {'value': {
            	  'assignedby_ids': ids or False,
            }}


    def create(self, cr, uid, vals, context=None):                   
        if context is None:
            context = {}
        if not context: 
            if vals['res_model'] == 'project.task':
                ownermanager = []
                task = self.pool.get('project.task').browse(cr, uid, vals['res_id']) 
                vals['company_id'] = task.company_id.id and task.company_id.id or False              
            if vals['res_model'] == 'project.issue':
                issue = self.pool.get('project.issue').browse(cr, uid, vals['res_id'])                                
                vals['company_id'] = issue.company_id.id and issue.company_id.id or False
            if vals['res_model'] == 'document.page':
                page = self.pool.get('document.page').browse(cr, uid, vals['res_id'])                                
                vals['company_id'] = page.company_id.id and page.company_id.id or False             
        else:
            vals['parent_id'] = context.get('parent_id', False) or vals.get('parent_id', False)
        # take partner from uid        
        if vals.get('res_id', False) and vals.get('res_model', False) and not vals.get('partner_id', False):
            vals['partner_id'] = self.__get_partner_id(cr, uid, vals['res_model'], vals['res_id'], context)
        if vals.get('datas', False):
            vals['file_type'], vals['index_content'] = self._index(cr, uid, vals['datas'].decode('base64'), vals.get('datas_fname', False), None)
        a = super(document_file, self).create(cr, uid, vals, context)
        if vals['parent_id']:
            ids = []
            for id in self.pool.get('document.directory').browse(cr, uid, vals['parent_id']).ownermanager_ids:
                ids.append(id.id)    
            self.pool.get('ir.attachment').write(cr, uid, a , {'assignedby_ids': [(6, 0, ids)]})
        return a

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if vals.get('datas', False):
            vals['file_type'], vals['index_content'] = self._index(cr, uid, vals['datas'].decode('base64'), vals.get('datas_fname', False), None)
        ids1 = []
        if 'parent_id' in vals:
            if vals['parent_id']:
                for id in self.pool.get('document.directory').browse(cr, uid, vals['parent_id']).ownermanager_ids:
                    ids1.append(id.id)
                print ids1    
                self.pool.get('ir.attachment').write(cr, uid, ids , {'assignedby_ids': [(6, 0, ids1)]})
            else:
                self.pool.get('ir.attachment').write(cr, uid, ids , {'assignedby_ids': [(6, 0, [])]})        
        return super(document_file, self).write(cr, uid, ids, vals, context)
    _columns = {
                'task_id': fields.function(_task_auto, relation='project.task', type="many2one", string='Task',store=True),
		  'project_id': fields.function(_project_auto, relation='project.project', type="many2one", string='Project',store=True),
                'issue_id': fields.function(_issue_auto, relation='project.issue', type="many2one", string='Issue',store=True),
                'page_id': fields.function(_page_auto, relation='document.page', type="many2one", string='Page',store=True),
                'res_partner_id': fields.function(_partner_auto, relation='res.partner', type="many2one", string='Partner',store=True),
                'crm_id': fields.function(_crm_auto, relation='crm.lead', type="many2one", string='CRM',store=True),
                'applicant_id': fields.function(_applicant_auto, relation='hr.applicant', type="many2one", string='Applicant',store=True),
                'saleorder_id': fields.function(_saleorder_auto, relation='sale.order', type="many2one", string='SaleOrder',store=True),
		  'involvestaff_ids': fields.many2many('res.users', 'document_user_involvestaff', 'document_id', 'uid','Involve Staff'),
		  'assignedby_ids': fields.many2many('res.users', 'document_user_assignedby', 'document_id', 'uid','Owner Manager'),
         }
    
document_file()

class document_directory(osv.osv):
    _inherit = 'document.directory'  
	
    _columns = {
	     'ownermanager_ids': fields.many2many('res.users', 'document_directory_user_ownermanager', 'document_directory_id', 'uid','Owner Manager'),
	     'involvestaff_ids': fields.many2many('res.users', 'document_directory_user_involvestaff', 'document_directory_id', 'uid','Involve Owner'),          
           
		 }   

document_directory()

class document_page(osv.osv):
    _inherit = 'document.page'     
    

    def onchange_document_page(self, cr, uid, ids, parent_id):  
        document_page = self.pool.get('document.page')  
        if not parent_id:
                return {'value': {                
                	'ownermanager_ids': False,
                	}}
        ids = []
        for id in document_page.browse(cr, uid, parent_id).ownermanager_ids:
            ids.append(id.id)  
        return {'value': {
            	  'ownermanager_ids': ids or False,
            }}

    _columns = {
		  'ownermanager_ids': fields.many2many('res.users', 'document_page_user_ownermanager', 'document_page_id', 'uid','Owner Manager'),
		  'involvestaff_ids': fields.many2many('res.users', 'document_page_user_involvestaff', 'document_page_id', 'uid','Involve Owner'),
                'directory_id': fields.many2one('document.directory', 'Directory', select=1, change_default=True),
		  'user_id': fields.many2one('res.users', 'Owner'),
		  'company_id': fields.many2one('res.company', 'Company'),

         }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'document.page', context=c),
    }
    

  
    
document_page()

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'
  
    def onchange_template_id(self, cr, uid, ids, template_id, composition_mode, model, res_id, context=None):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values """
        if template_id and composition_mode == 'mass_mail':
            values = self.pool.get('email.template').read(cr, uid, template_id, ['subject', 'body_html', 'attachment_ids'], context)
            values.pop('id')        
        elif template_id:
            values = self.generate_email_for_composer(cr, uid, template_id, res_id, context=context)
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if email not send
            values['attachment_ids'] = values.pop('attachment_ids', [])
            ir_attach_obj = self.pool.get('ir.attachment')
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'datas_fname': attach_fname,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                values['attachment_ids'].append(ir_attach_obj.create(cr, uid, data_attach, context=context))
        else:
            values = self.default_get(cr, uid, ['body', 'subject', 'partner_ids', 'attachment_ids'], context=context)
        
        if model == "project.task":
            task = self.pool.get('project.task').browse(cr, uid, res_id, context=context)
            ids = []            
            for id in task.reportto_ids:
                ids.append(id.partner_id.id)
            for id in task.involvestaff_ids:
                ids.append(id.partner_id.id)                                
            values['partner_ids'] = ids
        if model == "crm.lead":
            lead = self.pool.get('crm.lead').browse(cr, uid, res_id, context=context)
            ids = []            
            #for id in lead.section_id.member_ids:
                #ids.append(id.partner_id.id)                                           
            #values['partner_ids'] = ids 
        if model == "res.partner":
            partner = self.pool.get('res.partner').browse(cr, uid, res_id, context=context)
            ids = []            
            for id in partner.section_id.member_ids:
                ids.append(id.partner_id.id)                                           
            values['partner_ids'] = ids
 
        if values.get('body_html'):
            values['body'] = values.pop('body_html')
        return {'value': values}

mail_compose_message()

class project_task_schedule(osv.osv):
    _name = 'project.task.schedule'
    _description = 'Task Schedule'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Schedule Name', required=True, size=64, translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'case_default': fields.boolean('Default for New Projects',
                        help="If you check this field, this stage will be proposed by default on each new project. It will not assign this stage to existing projects."),
        'project_ids': fields.many2many('project.project', 'project_task_schedule_rel', 'schedule_id', 'project_id', 'Projects'),
        'state': fields.selection(_TASK_SCHEDULE, 'Related Status', required=True,
                        help="The status of your document is automatically changed regarding the selected stage. " \
                            "For example, if a stage is related to the status 'Close', when your document reaches this stage, it is automatically closed."),
        'fold': fields.boolean('Folded by Default',
                        help="This stage is not visible, for example in status bar or kanban view, when there are no records in that stage to display."),
    }
    def _get_default_project_id(self, cr, uid, ctx={}):
        proj = ctx.get('default_project_id', False)
        if type(proj) is int:
            return [proj]
        return proj
    _defaults = {
        'sequence': 1,
        'state': 'open',
        'fold': False,
        'case_default': False,
        'project_ids': _get_default_project_id
    }
    _order = 'sequence'

def short_name(name):
        """Keep first word(s) of name to make it small enough
           but distinctive"""
        if not name: return name
        # keep 7 chars + end of the last word
        keep_words = name[:7].strip().split()
        return ' '.join(name.split()[:len(keep_words)])
project_task_schedule()

class res_partner_category(osv.osv):
    _inherit = 'res.partner.category'     
    

    def onchange_res_partner_category(self, cr, uid, ids, parent_id):  
        res_partner_category = self.pool.get('res.partner.category')  
        if not parent_id:
                return {'value': {                
                	'ownermanager_ids': False,
                	}}
        ids = []         

        for id in res_partner_category.browse(cr, uid, parent_id).ownermanager_ids:
            ids.append(id.id)  
        return {'value': {
            	  'ownermanager_ids': ids or False,
            }}

 
    _columns = {
		  'ownermanager_ids': fields.many2many('res.users', 'res_partner_category_user_ownermanager', 'res_partner_category_id', 'uid','Owner Manager'),
		  'involvestaff_ids': fields.many2many('res.users', 'res_partner_category_user_involvestaff', 'res_partner_category_id', 'uid','Involve Owner'),
		  'user_id': fields.many2one('res.users', 'Owner'),
		  'company_id': fields.many2one('res.company', 'Company'),

         }   


    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'res.partner.category', context=c),
    }

    
res_partner_category()

class res_partner(osv.osv):
    _inherit = 'res.partner'     
    
    def onchange_res_partner(self, cr, uid, ids, category_id):  
        res_partner_category = self.pool.get('res.partner.category')  
        if not category_id:
                return {'value': {                
                	'ownermanager_ids': False,
                	}}
        ids = []
        for id in res_partner_category.browse(cr, uid, category_id).ownermanager_ids:
            ids.append(id.id)  
        return {'value': {
            	  'ownermanager_ids': ids or False,
            }}
    
  
    _columns = {
                'owner_id': fields.many2one('res.users', 'Owner'),
                'category_id': fields.many2one('res.partner.category', 'Tags'),
                'ownermanager_ids': fields.many2many('res.users', 'res_partner_user_ownermanager', 'res_partner_id', 'uid','Owner Manager'),
                'involvestaff_ids': fields.many2many('res.users', 'res_partner_user_involvestaff', 'res_partner_id', 'uid','Involve Owner'),                 
                'property_account_receivable': fields.property('account.account', type='many2one',relation='account.account',string="Account Receivable", view_load=True,domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner"),
                'property_account_payable': fields.property('account.account', type='many2one',relation='account.account',string="Account Payable",view_load=True,domain="[('type', '=', 'payable')]",help="This account will be used instead of the default one as the payable account for the current partner"),

         }

    _defaults = {
                'owner_id': lambda obj, cr, uid, context: uid,
    }

    
res_partner()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'  
	
    _columns = {
	        'company_id': fields.many2one('res.company', 'Company'), 
               'user_id': fields.many2one('res.users', 'Owner'),    
               'involvestaff_ids': fields.many2many('res.users', 'hr_contract_user_involvestaff', 'hr_contract_id', 'uid','Involve Owner'),           
		 }   
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.contract', context=c),
               'user_id': lambda obj, cr, uid, context: uid,
 
    }


hr_contract()

class hr_attendance(osv.osv):
    _inherit = 'hr.attendance'  
	
    _columns = {
	        'company_id': fields.many2one('res.company', 'Company'),     
           
		 }   
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.attendance', context=c),
    }


hr_attendance()

class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'  
	
    _columns = {
	        'company_id': fields.many2one('res.company', 'Company'),     
           
		 }   
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.holidays', context=c),
    }


hr_holidays()

class hr_applicant(osv.osv):
    _inherit = 'hr.applicant'  
	
    _columns = {	        
               'involvestaff_ids': fields.many2many('res.users', 'hr_applicant_user_involvestaff', 'hr_applicant_id', 'uid','Involve Owner'),           
		 }    


hr_applicant()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'  
	
    _columns = {                         
               'involvestaff_ids': fields.many2many('res.users', 'hr_employee_user_involvestaff', 'hr_employee_id', 'uid','Involve Owner'),           
		 }   
    _defaults = {              
               'user_id': lambda obj, cr, uid, context: uid,
 
    }
hr_employee()



class project_issue(base_stage, osv.osv):

    _inherit = "project.issue"

    _columns = {
	     'assignedby_id': fields.many2one('res.users', 'Assigned By',track_visibility='onchange'),
	     'reportto_ids': fields.many2many('res.users', 'issue_user_reportto', 'issue_id', 'uid', 'Report To'),
	     'involvestaff_ids': fields.many2many('res.users', 'issue_user_involvestaff', 'issue_id', 'uid','Involve Staff'),
            'directory_id': fields.many2one('document.directory', 'Directory', select=1, change_default=True), 

		 }

project_issue()

