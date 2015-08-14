
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID

class hpusa_register_loyalty_point(osv.osv):
    _name = "hpusa.register.loyalty.point"

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(hpusa_register_loyalty_point,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        for field in res['fields']:
            if field == 'program':           
                sql = '''
                    SELECT id 
                    FROM hpusa_loyalty_program  
                    WHERE actived = True AND state= 'done' AND end_date >= '%s' AND start_date <= '%s'
                '''%(time.strftime('%Y-%m-%d'),time.strftime('%Y-%m-%d'))
                cr.execute(sql)
                ids = map(lambda x: x[0], cr.fetchall())
                res['fields'][field]['domain'] = str([('id','in', ids)])
        return res


    def _get_partner(self, cr, uid, context=None):
        if context is None:
            context = {}
        model = context.get('active_model', [])
        if model == 'res.partner':
            res_ids = context.get('active_ids', [])
            return res_ids[0]
        return None 

   
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name' : fields.char('Name', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer',required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'customer': fields.related('partner_id','customer_name_id',type='char', string='Customer Reference', readonly=True),
        'date': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'amount': fields.float('Amount', readonly=True, digits_compute=dp.get_precision('Account'), states={'draft': [('readonly', False)]}),
        'currency': fields.many2one('res.currency', 'Currency', readonly=True, states={'draft': [('readonly', False)]}),
        'point': fields.integer('Point', readonly=True),
        'obj': fields.selection([
                       ('shop', 'Shop'),
                       ('location', 'Location'),
                       ('cate_prod', 'Category Product')
                       ],
                       'Object', required=True, readonly=True, states={'draft': [('readonly', False)]}),  
        'type': fields.selection([
                       ('sales', 'Sales'),
                       ],
                      'Type', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'shop_id': fields.many2one('sale.shop', 'Shop',  readonly=True, states={'draft': [('readonly', False)]}),
        'location_id': fields.many2one('stock.location','Location',  readonly=True, states={'draft': [('readonly', False)]}),
        'cate_prod_id':fields.many2one('product.category', 'Category Product',  readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.text('Note'),
        'program': fields.many2one('hpusa.loyalty.program','Program Loyalty', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange',
        ),   
        'company_id': fields.many2one('res.company','Company', states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', states={'draft': [('readonly', False)]}),       
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The loyalty point name must be unique !')
    ]
    _defaults = {
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'user_id': lambda s, c, uid, ctx: uid,
        'partner_id': _get_partner,
        'type': 'sale',
        }
    def onchange_user_id(self,cr,uid, ids, user_id, context = None):
        if user_id:
            sql = '''SELECT crm.id 
                    FROM sale_member_rel rel 
                    LEFT JOIN crm_case_section crm ON(crm.id = rel.section_id)
                    WHERE rel.member_id = %s'''%user_id
            cr.execute(sql)
            result = cr.dictfetchall()
            if len(result) > 0:
                return {'value': {'section_id': int(result[0]['id'])}}    
        return {'value': {'section_id': None}}

    def onchange_date(self,cr,uid, ids, date, context = None):
        pro_ids = []
        if date:
            sql = '''
                    SELECT id 
                    FROM hpusa_loyalty_program  
                    WHERE actived = True AND state= 'done' AND end_date >= '%s' AND start_date <= '%s'
                '''%(date,date)
            cr.execute(sql)
            pro_ids = map(lambda x: x[0], cr.fetchall())
        domain = [('id','in', pro_ids)]  
        return {'domain': {'program':domain}}
    
    def action_submit(self, cr, uid, ids, context=None):    
        for obj in self.browse(cr, uid, ids, context):
            sql = '''SELECT * FROM fn_loyalty(%s,%s) as tab (program_id integer, con_id integer, amount NUMERIC, point NUMERIC, end_date date, start_date date);'''%(obj.id, obj.program and obj.program.id or 0)
            cr.execute(sql)
            print sql
            res = cr.dictfetchall()            
            obj = self.browse(cr, uid, obj.id, context)
            if res:
                self.write(cr, uid, [obj.id], {'point':res[0]['point'], 'program': res[0]['program_id']})
                self.write(cr, uid, ids, {'state':'done'}, context)
                vals = {}
                vals['name'] = obj.name
                vals['partner_id'] = obj.partner_id.id
                vals['date'] = obj.date
                vals['point'] = int(res[0]['point'])
                vals['amount'] = obj.amount
                vals['type'] = 'cumulative'
                vals['state'] = 'done'
                vals['register_loyalty_id'] = obj.id
                vals['program'] = obj.program.id or False
                vals['end_date'] = res[0]['end_date']
                vals['start_date'] = res[0]['start_date']
                vals['user_id'] = obj.user_id.id
                vals['section_id'] = obj.section_id.id
                vals['company_id'] = obj.company_id.id
                self.pool.get('hpusa.loyalty.move').create(cr, uid, vals, context)
            else:
                raise osv.except_osv(('Not Found'),('Not Loyalty Program Apply'))
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        point = self.pool.get('res.partner').browse(cr, uid, obj.partner_id.id, context).point_remain
        if point - obj.point < 0:
            raise osv.except_osv(('Processing Error'),('Not Processing. Negative point!'))
        self.write(cr, uid, ids, {'state':'cancel','program':None,'point':0}, context)
        move_id = self.pool.get('hpusa.loyalty.move').search(cr, uid, [('register_loyalty_id','=',ids[0])])
        if move_id:
            self.pool.get('hpusa.loyalty.move').action_cancel(cr, uid, move_id, context)
            
    def action_set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context)
        move_id = self.pool.get('hpusa.loyalty.move').search(cr, uid, [('register_loyalty_id','=',ids[0])])
        if move_id:
            self.pool.get('hpusa.loyalty.move').unlink(cr, uid, move_id, context)

    def unlink(self, cr, uid, ids, context=None):
        ojb = self.browse(cr, uid, ids[0])
        if ojb.state == "done":
            raise osv.except_osv(('Processing Error'),('Register Loyalty state "done" not Processing!'))      
        move_id = self.pool.get('hpusa.loyalty.move').search(cr, uid, [('register_loyalty_id','=',ids[0])])
        if move_id:
            self.pool.get('hpusa.loyalty.move').unlink(cr, uid, move_id, context)
        return super(hpusa_register_loyalty_point, self).unlink(cr, uid, ids, context)
hpusa_register_loyalty_point()

class hpusa_loyalty_conditions(osv.osv):
    _name = "hpusa.loyalty.conditions"
    _columns = {
            'name' : fields.char('Name', required=True),
            'obj': fields.selection([
                           ('shop', 'Shop'),
                           ('location', 'Location'),
                           ('cate_prod', 'Category Product')
                           ],
                           'Object',required=True),            
            'shop_id': fields.many2one('sale.shop', 'Shop'),
            'location_id': fields.many2one('stock.location','Location'),
            'start_date': fields.date('Start date'),
            'end_date': fields.date('End date'),
            'cate_prod_id':fields.many2one('product.category', 'Category Product'),                            
            'type': fields.selection([
                           ('sales', 'Sales'),
                           ],
                          'Type', required=True),
            'loyalty_id': fields.many2one('hpusa.loyalty.program', 'Loyalty'),
            'logic': fields.selection([
                                   ('and', 'And'),
                                   ('or', 'Or')
                                   ],
                                  'Logic'),
            'lines': fields.one2many('hpusa.loyalty.conditions.line','condition_id', 'Line Condition')
        }
    _defaults = {
        'type': 'sales',
        }
hpusa_loyalty_conditions()

class hpusa_loyalty_conditions_line(osv.osv):
    _name = "hpusa.loyalty.conditions.line"     
    _columns = {
                'from_value':fields.float('From Value', required=True, digits_compute=dp.get_precision('Account')),
                'to_value':fields.float('To Value', digits_compute=dp.get_precision('Account')),
                'logic':fields.selection([
                                       ('and', 'And'),
                                       ('or', 'Or')
                                       ],
                                      'Logic'), 
                'formula':fields.char('Formula Point', required=True),
                'condition_id':fields.many2one('hpusa.loyalty.conditions', 'Conditions'),
                'choose':fields.selection([
                                       ('value', 'Amount')],
                                      'Option'),
                }
    _defaults = {
        'choose': 'value',
        }
hpusa_loyalty_conditions_line()

class hpuas_loyalty_program(osv.osv):  
    _name = 'hpusa.loyalty.program'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char('Name', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'actived': fields.boolean('Active'),
        'sequence': fields.integer('Sequence', required=True),
        'start_date': fields.date('Start date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'end_date': fields.date('End date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one('res.company', 'Company',  required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'currency': fields.many2one('res.currency', 'Currency', readonly=True, states={'draft': [('readonly', False)]}), 
        'partner_id': fields.many2many('res.partner', 'loyalty_partner_rel', 'loyalty_id', 'partner_id', 'Customer', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_group_id': fields.many2many('res.partner.category', 'loyalty_partner_categoty_rel', 'loyalty_id', 'partner_category_id', 'Group customer', readonly=True, states={'draft': [('readonly', False)]}),
        'condition_lines':fields.one2many('hpusa.loyalty.conditions','loyalty_id','Conditions', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'User'),    
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange',
        ),       
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'state': 'draft',
        'user_id': lambda s, c, uid, ctx: uid,
        'actived': True,
        }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The loyalty program name must be unique !')
    ]
    def action_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        id_gift = self.pool.get('hpusa.register.loyalty.point').search(cr, uid, [('program','in',ids)])
        if id_gift:
            raise osv.except_osv(('Processing Error'),('Loyalty Program exist in Register Loyalty. Not Processing!')) 
        self.write(cr, uid, ids, {'state':'cancel'}, context)
        
    def action_set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context)

    def unlink(self, cr, uid, ids, context=None):
        ojb = self.browse(cr, uid, ids[0])
        if ojb.state == "done":
            raise osv.except_osv(('Processing Error'),('Loyalty Program state "done" not Processing!'))  
        id_gift = self.pool.get('hpusa.register.loyalty.point').search(cr, uid, [('program','in',ids)])
        if id_gift:
            raise osv.except_osv(('Processing Error'),('Loyalty Program exist in Register Loyalty. Not Processing!')) 
        return super(hpuas_loyalty_program, self).unlink(cr, uid, ids, context)
     
hpuas_loyalty_program()

class hpusa_voucher(osv.osv):
    _name = "hpusa.voucher"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _columns = {
        'level' : fields.char('Card level', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Internal Reference', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'point': fields.integer('Effective Point', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Valid Until', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'actived': fields.boolean('Active', readonly=True, states={'draft': [('readonly', False)]}),   
        'discount': fields.float('Amount Discount', required=True, readonly=True, states={'draft': [('readonly', False)]}),  
        'state': fields.selection([
                    ('draft', 'Draft'),
                    ('cancel', 'Cancelled'),
                    ('done', 'Done'),
                    ], 'Status', readonly=True, select=True, track_visibility='onchange',
                ),       
        'company_id': fields.many2one('res.company','Company', states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'User'),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Internal Reference must be unique !')
    ]
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'state': 'draft',
        'actived': True,
        }
    
    def action_submit(self, cr, uid, ids, context=None):
        ojb = self.browse(cr, uid, ids[0])
        if ojb.point <= 0:
            raise osv.except_osv(('Processing Error'),('Point voucher >= 1')) 
        self.write(cr, uid, ids, {'state':'done'}, context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        id_gift = self.pool.get('hpusa.gift.voucher').search(cr, uid, [('voucher_id','in',ids)])
        if id_gift:
            raise osv.except_osv(('Processing Error'),('Voucher exist in Gift Loyalty. Not Processing!')) 
        self.write(cr, uid, ids, {'state':'cancel'}, context)
        
    def action_set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context)

    def unlink(self, cr, uid, ids, context=None):
        ojb = self.browse(cr, uid, ids[0])
        if ojb.state == "done":
            raise osv.except_osv(('Processing Error'),('Voucher state "done" not Processing!'))      
        return super(hpusa_voucher, self).unlink(cr, uid, ids, context)
hpusa_voucher()

class hpusa_gift_voucher(osv.osv):
    _name = "hpusa.gift.voucher"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(hpusa_gift_voucher,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        for field in res['fields']:
            if field == 'voucher_id':           
                sql = '''
                    SELECT id 
                    FROM hpusa_voucher  
                    WHERE actived = True AND state= 'done' AND date >= '%s'
                '''%(time.strftime('%Y-%m-%d'))
                cr.execute(sql)
                ids = map(lambda x: x[0], cr.fetchall())
                res['fields'][field]['domain'] = str([('id','in', ids)])
            if field == 'program':           
                sql = '''
                    SELECT id 
                    FROM hpusa_loyalty_program  
                    WHERE actived = True AND state= 'done' AND end_date >= '%s' AND start_date <= '%s'
                '''%(time.strftime('%Y-%m-%d'),time.strftime('%Y-%m-%d'))
                cr.execute(sql)
                ids = map(lambda x: x[0], cr.fetchall())
                res['fields'][field]['domain'] = str([('id','in', ids)])
        return res

    def _get_point_curent(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        point = 0.0
        for obj in self.browse(cr, uid, ids):
            if obj.partner_id:
                point =  self.pool.get('res.partner').browse(cr, uid, obj.partner_id.id, context).point_remain
            res[obj.id] = point
        return res

    def _get_name(self, cr, uid, context=None):
        if context is None:
            context = {}
        name_mo = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'hpusa.gift.voucher')
        return  name_mo

    def _get_partner(self, cr, uid, context=None):
        if context is None:
            context = {}
        model = context.get('active_model', [])
        if model == 'res.partner':
            res_ids = context.get('active_ids', [])
            return res_ids[0]
        return None  
        
    _columns = {
        'name' : fields.char('Serial No.', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'voucher_id': fields.many2one('hpusa.voucher', 'Voucher Type', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'quantity': fields.integer('Quantity Voucher', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date'),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft': [('readonly', False)]}),
        'customer_no': fields.related('partner_id','customer_name_id',type='char', string='Customer No', readonly=True), 
        'point_current':fields.function(_get_point_curent,type='integer',string='Point Current'),
        'point': fields.related('voucher_id','point',type='integer', string='Point', store=True, readonly=True), 
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('confirm', 'Open'),
             ('done', 'Done'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange',
        ),            
        'program': fields.many2one('hpusa.loyalty.program','Program Loyalty', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one('res.company','Company', states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'), 
    } 
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Serial No must be unique !')
    ]
    _defaults = {
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        'user_id': lambda s, c, uid, ctx: uid,
        'name': _get_name,
        'partner_id': _get_partner,
        }
    def onchange_date(self,cr,uid, ids, date, context = None):
        pro_ids = []
        if date:
            sql = '''
                    SELECT id 
                    FROM hpusa_loyalty_program  
                    WHERE actived = True AND state= 'done' AND end_date >= '%s' AND start_date <= '%s'
                '''%(date,date)
            cr.execute(sql)
            pro_ids = map(lambda x: x[0], cr.fetchall())
        domain = [('id','in', pro_ids)]   
        return {'domain': {'program':domain}}
    
    def onchange_user_id(self,cr,uid, ids, user_id, context = None):
        if user_id:
            sql = '''SELECT id 
                        FROM crm_case_section
                        WHERE user_id = %s
                     UNION ALL
                     SELECT crm.id 
                        FROM sale_member_rel rel 
                        LEFT JOIN crm_case_section crm ON(crm.id = rel.section_id)
                        WHERE rel.member_id = %s                 
                    '''%(user_id,user_id)
            cr.execute(sql)
            result = cr.dictfetchall()
            if len(result) > 0:
                return {'value': {'section_id': int(result[0]['id'])}}    
        return {'value': {'section_id': None}}
    
    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context)
        for obj in self.browse(cr, uid, ids, context):
            vals = {}
            vals['name'] = obj.name
            vals['partner_id'] = obj.partner_id.id
            vals['date'] = obj.date
            vals['point'] = - obj.quantity * obj.voucher_id.point
            vals['amount'] = 0
            vals['quantity'] = obj.quantity
            vals['voucher_id'] = obj.voucher_id.id
            vals['program'] = obj.program.id
            vals['type'] = 'used'
            vals['state'] = 'done'
            vals['gift_loyalty_id'] = obj.id
            vals['end_date'] = obj.date
            vals['user_id'] = obj.user_id.id
            vals['section_id'] = obj.section_id.id
            vals['company_id'] = obj.company_id.id
            self.pool.get('hpusa.loyalty.move').create(cr, uid, vals, context)
        return True
        
    def action_confirm(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.voucher_id.point * obj.quantity <= 0:
                raise osv.except_osv(('Processing Error'),('Quantity voucher >= 1'))  
            if obj.point_current < obj.voucher_id.point * obj.quantity or obj.point_current <=0:
                raise osv.except_osv(('Processing Error'),('Not enough point!'))  
        self.write(cr, uid, ids, {'state':'confirm'}, context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context)  
        self.write(cr, uid, ids, {'state':'cancel'}, context)
        move_id = self.pool.get('hpusa.loyalty.move').search(cr, uid, [('gift_loyalty_id','=',ids[0])])
        if move_id:
            self.pool.get('hpusa.loyalty.move').action_cancel(cr, uid, move_id, context)    
        return True
        
    def action_set_to_draft(self, cr, uid, ids, context=None):
        move_id = self.pool.get('hpusa.loyalty.move').search(cr, uid, [('gift_loyalty_id','=',ids[0])])
        if move_id:
            self.pool.get('hpusa.loyalty.move').unlink(cr, uid, move_id, context)
        self.write(cr, uid, ids, {'state':'draft'}, context)

    def unlink(self, cr, uid, ids, context=None):
        ojb = self.browse(cr, uid, ids[0])
        if ojb.state == "done":
            raise osv.except_osv(('Processing Error'),('Gift Voucher state "done" not Processing')) 
        move_id = self.pool.get('hpusa.loyalty.move').search(cr, uid, [('gift_loyalty_id','=',ids[0])])
        if move_id:
            self.pool.get('hpusa.loyalty.move').unlink(cr, uid, move_id, context)    
        return super(hpusa_gift_voucher, self).unlink(cr, uid, ids, context)
hpusa_gift_voucher()

class hpusa_loyalty_move(osv.osv):
    _name = "hpusa.loyalty.move"
    _inherit = ['mail.thread', 'ir.needaction_mixin']    
    _columns = {
        'name' : fields.char('Name', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'register_loyalty_id': fields.many2one('hpusa.register.loyalty.point', 'Register Loyalty'),
        'voucher_id': fields.many2one('hpusa.voucher', 'Voucher', readonly=True, states={'draft': [('readonly', False)]}),
        'quantity': fields.integer('Quantity Voucher', readonly=True, states={'draft': [('readonly', False)]}),
        'gift_loyalty_id': fields.many2one('hpusa.gift.voucher', 'Gift Loyalty'),
        'date': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'point': fields.integer('Effective Point', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'amount': fields.float('Amount', readonly=True, states={'draft': [('readonly', False)]}),
        'type': fields.selection([
                               ('cumulative', 'Reward Point'),
                               ('used', 'Reward Card Issue'),
                               ('expired','Expired')
                               ],
                              'Type', readonly=True, states={'draft': [('readonly', False)]}), 
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange',
        ),
        'program': fields.many2one('hpusa.loyalty.program','Program Loyalty', readonly=True),     
        'company_id': fields.many2one('res.company','Company', states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'User'), 
        'end_date': fields.date('End date'), 
        'start_date': fields.date('Start date'),   
        'section_id': fields.many2one('crm.case.section', 'Sales Team', states={'draft': [('readonly', False)]}),   
        
    }
    _defaults = {
        'state': 'draft',
        'user_id': lambda s, c, uid, ctx: uid,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'vi.trust.account', context=c),
        }
    def onchange_user_id(self,cr,uid, ids, user_id, context = None):
        if user_id:
            sql = '''SELECT id 
                        FROM crm_case_section
                        WHERE user_id = %s
                     UNION ALL
                     SELECT crm.id 
                        FROM sale_member_rel rel 
                        LEFT JOIN crm_case_section crm ON(crm.id = rel.section_id)
                        WHERE rel.member_id = %s                 
                    '''%(user_id,user_id)
            cr.execute(sql)
            result = cr.dictfetchall()
            if len(result) > 0:
                return {'value': {'section_id': int(result[0]['id'])}}    
        return {'value': {'section_id': None}}
    
    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'}, context)
        
    def action_set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context)

    def unlink(self, cr, uid, ids, context=None):
        ojb = self.browse(cr, uid, ids[0])
        if ojb.state == "done":
            raise osv.except_osv(('Processing Error'),('Loyalty Move state "done" not Processing!'))      
        return super(hpusa_loyalty_move, self).unlink(cr, uid, ids, context)

    def check_expired(self, cr, uid, automatic=False, use_new_cursor=False, context=None):    
        print 'sssssssssssssssssssssssss'
        sql = '''SELECT * FROM fn_check() as tab (result boolean);'''
        cr.execute(sql)
        
    def get_point(self, cr, uid, ids, partner_id, context=None):
        res = 0.0
        if partner_id:
            sql = '''SELECT COALESCE(SUM(point), 0) as point
            FROM (SELECT point FROM hpusa_loyalty_move WHERE state='done' AND partner_id =  %s
            ) as tab'''%(partner_id)
            cr.execute(sql)
            result = cr.dictfetchall()
            if result:
                res = result[0]['point']
        return res
hpusa_loyalty_move()

class res_partner(osv.osv):
    _inherit = "res.partner"
    def _get_point(self, cr, uid, ids ,field_name, arg, context = None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):            
            sql = '''SELECT MAX(end_date) as end, MIN(start_date) as start
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = %s'''%(line.id)
            cr.execute(sql)
            result = cr.dictfetchall()
            start_date = result[0]['start']
            end_date = result[0]['end']
            
            sql = '''SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = %s'''%(line.id)
            cr.execute(sql)
            result = cr.dictfetchall()
            point_cumulative = result[0]['point']
            
            sql = '''SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = %s'''%(line.id)
            cr.execute(sql)
            result = cr.dictfetchall()
            point_use = result[0]['point']
            sql = '''SELECT SUM(point) as point  
                    FROM (SELECT COALESCE(SUM(point), 0) as point
                            FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = %s AND end_date < ('%s')
                        UNION ALL
                        SELECT COALESCE(SUM(point), 0) as point
                            FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = %s AND end_date < ('%s')
                    ) as tab'''%(line.id, time.strftime('%Y-%m-%d'),line.id, time.strftime('%Y-%m-%d'))
            print sql
            cr.execute(sql)
            result = cr.dictfetchall()
            point_expired = result[0]['point']
            point_remain = point_cumulative + point_use - point_expired
            res[line.id] = {
                'start_date' : start_date,
                'end_date' : end_date,
                'point_cumulative' : int(point_cumulative),
                'point_use' : - int(point_use),
                'point_expired' : int(point_expired),
                'point_remain' : int(point_remain),
            }
        return res 
    _columns = {
        'start_date': fields.function(_get_point, type='date', string='Start date', multi='get_point'),
        'end_date': fields.function(_get_point, type='date', string='End date',  multi='get_point'),
        'point_cumulative': fields.function(_get_point, type='integer', string='Point cumulative',  multi='get_point'),
        'point_use': fields.function(_get_point, type='integer', string='Point use',  multi='get_point'),
        'point_expired': fields.function(_get_point, type='integer', string='Point expired',  multi='get_point'),
        'point_remain': fields.function(_get_point, type='integer', string='Point remain',  multi='get_point'),
    }
    def acction_create_register(self, cr, uid, ids, context=None):
        vals = {
                    'name': "Create Journal Voucher",
                    'context': context,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'hpusa.register.loyalty.point',
                    'view_id': False, 
                    'type': 'ir.actions.act_window',  
                    'nodestroy': True,
                }
        return vals  
     
    def acction_create_gift(self, cr, uid, ids, context=None):
        vals = {
                    'name': "Create Journal Voucher",
                    'context': context,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'hpusa.gift.voucher',
                    'view_id': False, 
                    'type': 'ir.actions.act_window',  
                    'nodestroy': True,
                }
        return vals 
res_partner()