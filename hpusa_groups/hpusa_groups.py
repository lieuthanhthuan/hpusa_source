from openerp.osv import fields, osv
from openerp.tools.translate import _

class hpusa_groups(osv.osv):
    _name = "hpusa.groups"
    _columns = {
        'name' : fields.char('Name', required=True),
        'team_leader' : fields.many2one('res.users', 'Group Leader', required=True),
        'group_ids' : fields.many2many('res.users', 'hpusa_groups_user', 'group_id','user_id', string ='Groups', required=True),
    }
hpusa_groups()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_sale', 'group_id','sale_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(sale_order, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            try:
                v = {
                        'model_obj': 'sale.order',
                        'res_model': 'sale.order',
                        'res_id': int(res),
                        'partner_ids': [(6,0, partner_id) ]
                     }
                in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
                self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
            except ValueError:
                print 'error'
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'sale.order',
                    'res_model': 'sale.order',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            print 'sss'
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            print in_id
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
sale_order()

class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_lead', 'group_id','lead_id', 'Group'),
    }
    
    def create(self, cr, uid, vals, context=None):
        res = super(crm_lead, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            try:
                v = {
                        'model_obj': 'crm.lead',
                        'res_model': 'crm.lead',
                        'res_id': int(res),
                        'partner_ids': [(6,0, partner_id) ]
                     }
                in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
                self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
            except ValueError:
                print 'error'
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(crm_lead, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'crm.lead',
                    'res_model': 'crm.lead',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            print 'sss'
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            print in_id
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
crm_lead()

class project_project(osv.osv):
    _inherit = 'project.project'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_project', 'group_id','project_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(project_project, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'project.project',
                    'res_model': 'project.project',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_project, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'project.project',
                    'res_model': 'project.project',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
project_project()

class project_task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_task', 'group_id','task_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(project_task, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'project.task',
                    'res_model': 'project.task',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_task, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'project.task',
                    'res_model': 'project.task',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
project_task()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_partner', 'group_id','partner_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(res_partner, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'res.partner',
                    'res_model': 'res.partner',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(res_partner, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'res.partner',
                    'res_model': 'res.partner',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
res_partner()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_mrp', 'group_id','mrp_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(mrp_production, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'mrp.production',
                    'res_model': 'mrp.production',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(mrp_production, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'mrp.production',
                    'res_model': 'mrp.production',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
mrp_production()

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_workcenter', 'group_id','wo_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(mrp_production_workcenter_line, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'mrp.production.workcenter.line',
                    'res_model': 'mrp.production.workcenter.line',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(mrp_production_workcenter_line, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'mrp.production.workcenter.line',
                    'res_model': 'mrp.production.workcenter.line',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
mrp_production_workcenter_line()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_workcenter', 'group_id','wo_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(purchase_order, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'purchase.order',
                    'res_model': 'purchase.order',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(purchase_order, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:                            
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'purchase.order',
                    'res_model': 'purchase.order',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
purchase_order()

#Hung phat Configure 13-05-2015
class project_issue(osv.osv):
    _inherit = 'project.issue'
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_issue', 'group_id','issue_id', 'Group'),
    }
    def create(self, cr, uid, vals, context=None):
        res = super(project_issue, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'project.issue',
                    'res_model': 'project.issue',
                    'res_id': int(res),
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_issue, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'project.issue',
                    'res_model': 'project.issue',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res
project_issue()