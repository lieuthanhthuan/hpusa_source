# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://generalsolutions.vn>). All Rights Reserved
#
##############################################################################
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
class res_users(osv.osv):
    _inherit = "res.users"
    
    def create(self, cr, uid, data, context=None):
        # create default alias same as the login
        if not data.get('login', False):
            raise osv.except_osv(_('Invalid Action!'), _('You may not create a user. To create new users, you should use the "Settings > Users" menu.'))
        user_id = super(res_users, self).create(cr, uid, data, context=context)
        obj = self.browse(cr, uid, [user_id][0])
        mail_alias = self.pool.get('mail.alias')
        alias_id = mail_alias.create_unique_alias(cr, uid, {'alias_name': data['email'].split('@')[0],'alias_domain' : data['email'].split('@')[1]}, model_name=self._name, context=context)
        data.pop('alias_name', None)  # prevent errors during copy()
        self.write(cr, uid, [user_id], {'alias_id':alias_id})
        #self.pool.get('mail.alias').unlink(cr, uid, [obj.alias_id])
        return user_id
res_users()

class mail_alias(osv.Model):
    _inherit = "mail.alias"
    _columns = {
         'alias_domain': fields.char(string="Alias domain"),
    }
mail_alias()