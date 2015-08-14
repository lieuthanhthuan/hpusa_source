import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class mo_planning(osv.osv):
    _name = 'mo.planning'
    _columns = {
        'sale_order': fields.many2one('sale.order','Sale Order',required=True),
        'name': fields.char('Name', size=254),
        'routing_id': fields.many2one('mrp.routing', 'Routing', help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production planning."),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'company_id': fields.many2one('res.company','Company',required=True),
        'components': fields.one2many('mo.planning.line', 'planning_id','Components'),
        'user_id': fields.many2one('res.users','User'), 
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'mo.planning', context=c),
        'user_id': lambda s, c, uid, ctx: uid,
    }
    
    def onchange_routing(self, cr, uid, ids, routing_id, context=None):
        arr = []
        if routing_id:
            obj_routing = self.pool.get('mrp.routing').browse(cr, uid, routing_id)
            for item in obj_routing.workcenter_lines:
                vals = {
                          'name': item.name,
                          'workcenter_id': item.workcenter_id and item.workcenter_id.id or False,
                          'cycle_nbr': item.cycle_nbr,
                          'hour_nbr': item.hour_nbr,
                          'sequence': item.sequence,
                          'company_id': item.company_id and item.company_id.id or False,
                        }
                arr.append((0,0,vals))
        return {'value': {'components': arr}}
    
    def button_3d_view(self, cr, uid, ids, context):
        wo = self.pool.get('mrp.production.workcenter.line').search(cr, uid, [('planning_id','=',ids[0])])
        if not wo:
            raise osv.except_osv(_('Error!'), _('There is no 3D Design!'))
        mod_obj = self.pool.get('ir.model.data')
                    
        # call action
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'mrp_operations', 'mrp_production_wc_action_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of delivery orders to display     
        wo_obj =  self.pool.get('mrp.production.workcenter.line').browse(cr, uid, wo[0])
        result['domain'] = "[('id','in',["+','.join(map(str, [wo_obj.id]))+"])]"
        result['context'] = None
        return result 

    def button_3d(self, cr, uid, ids, context = None):
        if self.pool.get('mrp.production.workcenter.line').search(cr, uid, [('planning_id','=',ids[0])]):
            raise osv.except_osv(_('Error!'), _('There is exist 3D Design!'))
        wc_id = self.pool.get('mrp.workcenter').search(cr, uid, [('mo_state','=','3d')])
        print wc_id
        if wc_id:
            for workcenter_id in wc_id:
                for obj in self.browse(cr, uid, ids, context):
                    line  = None
                    for item in obj.components:
                        if item.workcenter_id.id == workcenter_id:
                            line = item
                    worker = None
                    if line:
                        if line.employee_id:
                            worker = line.employee_id
                    else:
                        employee_id =  self.pool.get('hr.employee').search(cr, uid, [('user_id','=',obj.user_id.id)])
                        if employee_id:
                            worker = self.pool.get('hr.employee').browse(cr, uid, employee_id[0])
                    wc_obj = self.pool.get('mrp.workcenter').browse(cr, uid, wc_id[0])
                    vals = {
                                'name': obj.sale_order.name + ' - ' + wc_obj.name,
                                'workcenter_id': workcenter_id,
                                'so_id': obj.sale_order.id,
                                'qty_planning': 1,
                                'product_planning': obj.product_id.id,
                                'employee_id': worker and worker.id or False,
                                'planning_id': ids[0],
                            }
                    id_wo = self.pool.get('mrp.production.workcenter.line').create(cr, uid, vals)
                    if worker and worker.user_id:
                        vals_invite = {
                                            'partner_ids': [(6,0,[worker.user_id.partner_id.id])],
                                            'message': 'You have been invited to follow' + obj.sale_order.name + ' - ' + wc_obj.name,
                                            'res_model': 'mrp.production.workcenter.line',
                                            'res_id': int(id_wo)
                                        }
                        invite_id = self.pool.get('mail.wizard.invite').create(cr, uid, vals_invite)
                        self.pool.get('mail.wizard.invite').add_followers(cr, uid, [invite_id])
                    mod_obj = self.pool.get('ir.model.data')
                            
                    # call action
                    act_obj = self.pool.get('ir.actions.act_window')
                    result = mod_obj.get_object_reference(cr, uid, 'mrp_operations', 'mrp_production_wc_action_form')
                    id = result and result[1] or False
                    result = act_obj.read(cr, uid, [id], context=context)[0]
                    #compute the number of delivery orders to display       
                    result['domain'] = "[('id','in',["+','.join(map(str, [id_wo]))+"])]"
                    result['context'] = None
                    return result  
        return False
            
mo_planning()

class mo_planning_line(osv.osv):
    _name = 'mo.planning.line'
    _columns = {
        'planning_id': fields.many2one('mo.planning','MO Planning'),
        'product_id': fields.many2one('product.product','Product', required=True),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Work Center', required=True),
        'cycle_nbr': fields.float('Number of Cycles', required=True,
            help="Number of iterations this work center has to do in the specified operation of the routing."),
        'hour_nbr': fields.float('Number of Hours', required=True, help="Time in hours for this Work Center to achieve the operation of the specified routing."),
        'name': fields.char('Name', size=64, required=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of routing Work Centers."),
        'note': fields.text('Description'),
        'company_id': fields.related('routing_id', 'company_id', type='many2one', relation='res.company', string='Company'),
        'employee_id': fields.many2one('hr.employee', 'Worker', required=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'routing_id': fields.many2one('mrp.routing', 'Parent Routing', select=True, ondelete='cascade',
             help="Routing indicates all the Work Centers used, for how long and/or cycles." \
                "If Routing is indicated then,the third tab of a production order (Work Centers) will be automatically pre-completed."),
    }
    
mo_planning_line()