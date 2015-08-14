from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_employee(osv.osv):

    _name="hr.employee"
    _inherit=['hr.employee','mail.thread', 'ir.needaction_mixin']
    _columns = {

        'home_address' : fields.char('Home Address'),
        'emegency_contact' : fields.char('Emegency Contact'),

    }
hr_employee()

class hr_employee_group(osv.osv):
    # HPUSA groups
    _inherit = 'hr.employee'
    def create(self, cr, uid, vals, context=None):
        res = super(hr_employee_group, self).create(cr, uid, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            try:
                v = {
                        'model_obj': 'hr.employee',
                        'res_model': 'hr.employee',
                        'res_id': int(res),
                        'partner_ids': [(6,0, partner_id) ]
                     }
                in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
                self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
            except ValueError:
                print 'error'
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(hr_employee_group, self).write(cr, uid, ids, vals, context)
        if 'groups_id_many' in vals:
            partner_id = []
            for item in vals['groups_id_many'][0][2]:
                for group in self.pool.get('hpusa.groups').browse(cr, uid, item).group_ids:
                    if group.partner_id.id not in partner_id:
                        partner_id.append(group.partner_id.id)
            v = {
                    'model_obj': 'hr.employee',
                    'res_model': 'hr.employee',
                    'res_id': ids[0],
                    'partner_ids': [(6,0, partner_id) ]
                 }
            print 'sss'
            in_id = self.pool.get('mail.wizard.invite').create(cr, uid, v, context)
            print in_id
            self.pool.get('mail.wizard.invite').add_followers(cr, uid, [in_id])
        return res

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
               #content = self._get_page_index(cr, uid, page, link=False)
            content = page.content
            res[page.id] =  content
        return res

# hpusa customize 23-04-2015
#    def onchange_parent_id(self, cr, uid, ids, parent_id, content, context=None):
#        res = {}
#        parent = self.pool.get('document.page').browse(cr, uid, parent_id, context=context)
#        res['value'] = {
#            'content': parent.content,
#            }
#        return res
    _columns = {
        'groups_id_many' : fields.many2many('hpusa.groups', 'hpusa_groups_employee', 'group_id','employee_id', 'Group'),
        'content': fields.text("Content"),
        'display_content': fields.function(_get_display_content, string='Displayed Content', type='text'),
    }
hr_employee_group()

class hr_department(osv.osv):
    _name="hr.department"
    _inherit='hr.department'
    _columns = {
        'ownermanager_ids' : fields.many2many('res.users', 'hr_department_user', 'ownermanager_id','user_id', string ='Involve Manager'),

    }
hr_department()