# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import tools
from openerp.osv import osv, fields

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def _get_template1(self, cr, uid, context=None):
        if context is None:
            context = {}
        model = False
        email_template_obj = self.pool.get('email.template')
        message_id = context.get('default_parent_id', context.get('message_id', context.get('active_id')))

        if context.get('default_composition_mode') == 'reply' and message_id:
            message_data = self.pool.get('mail.message').browse(cr, uid, message_id, context=context)
            if message_data:
                model = message_data.model
        else:
            model = context.get('default_model', context.get('active_model'))
        if context.get('template'):
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id.name
            if company == 'HPUSA':
                record_ids = email_template_obj.search(cr, uid, [('model', '=', model),('name','=','Sales Order - English')], context=context)
                if record_ids:
                    return record_ids[0]
            elif company == 'HPVN':
                record_ids = email_template_obj.search(cr, uid, [('model', '=', model),('name','=','Sales Order - Vietnamese')], context=context)
                if record_ids:
                    return record_ids[0]
            else:
                record_ids = email_template_obj.search(cr, uid, [('model', '=', model)], context=context)
                if record_ids:
                    return None
        return None

    def _get_templates(self, cr, uid, context=None):
        if context is None:
            context = {}
        model = False
        email_template_obj = self.pool.get('email.template')
        message_id = context.get('default_parent_id', context.get('message_id', context.get('active_id')))

        if context.get('default_composition_mode') == 'reply' and message_id:
            message_data = self.pool.get('mail.message').browse(cr, uid, message_id, context=context)
            if message_data:
                model = message_data.model
        else:
            model = context.get('default_model', context.get('active_model'))
        record_ids = email_template_obj.search(cr, uid, [('model', '=', model)], context=context)
        return email_template_obj.name_get(cr, uid, record_ids, context) + [(False, '')]


    _columns = {
        # incredible hack of the day: size=-1 means we want an int db column instead of an str one
		'mail_from': fields.char('email'),
              'template_id': fields.selection(_get_templates, 'Template', size=-1),
    }
    _defaults = {
	'template_id': _get_template1,
    }
    def onchange_template_id(self, cr, uid, ids, template_id, composition_mode, model, res_id, context=None):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values """
        if template_id and composition_mode == 'mass_mail':
            values = self.pool.get('email.template').read(cr, uid, template_id, ['subject', 'body_html','mail_from'], context)
            values.pop('id')
        elif template_id:
            # FIXME odo: change the mail generation to avoid attachment duplication
            values = self.generate_email_for_composer(cr, uid, template_id, res_id, context=context)
            # transform attachments into attachment_ids
            values['attachment_ids'] = []
            ir_attach_obj = self.pool.get('ir.attachment')
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'datas_fname': attach_fname,
                    'res_model': model,
                    'res_id': res_id,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                values['attachment_ids'].append(ir_attach_obj.create(cr, uid, data_attach, context=context))
        else:
            values = self.default_get(cr, uid, ['body', 'subject', 'partner_ids', 'attachment_ids'], context=context)

        if values.get('body_html'):
            values['body'] = values.pop('body_html')
        if values.get('mail_from'):
	     values['mail_from'] = values.pop('mail_from')
        return {'value': values}

    def render_message(self, cr, uid, wizard, res_id, context=None):
        """ Override to handle templates. """
        # generate the composer email
        if wizard.template_id:
            values = self.generate_email_for_composer(cr, uid, wizard.template_id, res_id, context=context)
        else:
            values = {}
        # get values to return
        email_dict = super(mail_compose_message, self).render_message(cr, uid, wizard, res_id, context)
        values.update(email_dict)
        if wizard.template_id:
            val = self.pool.get('email.template').read(cr, uid, wizard.template_id, ['email_from'], context)
            values.update({'email_from': self.render_template(cr, uid, val['email_from'], wizard.model, res_id, context)})
        return values
		
mail_compose_message()		