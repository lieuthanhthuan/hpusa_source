import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from datetime import datetime
from dateutil.relativedelta import relativedelta

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'sale_order_type': fields.selection([('customize', 'Customize'),('normal', 'Normal')],'Sale Order Type'),
        'sub_type': fields.selection([('diamond', 'Diamonds'),('hpcustom', 'HPUSA Custom'),('design', 'Designers'),('other', 'Other Vendors')],'Sub Type'),
        'customer_name_id' : fields.related('partner_id','customer_id',type="char", relation="res.partner", string="Customer ID", readonly=True,stored=True),
        'mo_state': fields.selection([('3d', '3D Design'),
                                      ('waxmodeling', 'Waxmodeling'),
                                      ('casting', 'Casting'),
                                      ('assembling', 'Assembling'),
                                      ('setting', 'Setting'),
                                      ('polishing', 'Polishing'),
                                      ('engraving', 'Engraving'),
                                     ],'Manufacturing State'),
    }
    def action_view_mo(self, cr, uid, ids, context=None):
        ids_mo = []
        for obj in self.browse(cr, uid, ids):
            ids_mo = self.pool.get('mrp.production').search(cr, uid, [('so_id','=',obj.id)])
        if not ids_mo:
            raise osv.except_osv(_('Error!'), _('There is no manufacturing order!'))
        mod_obj = self.pool.get('ir.model.data')

        # call action
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'hpusa_manufacturing', 'sale_open_mo')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=None)[0]
        result['context'] = {'group_by': None, 'default_so_id': ids[0], 'search_default_so_id': ids[0]}
        return result

    def action_create_mo(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        production_obj = self.pool.get('mrp.production')
        for obj in self.browse(cr, uid, ids):
            for line in obj.order_line:
                ids_mo = self.pool.get('mrp.production').search(cr, uid, [('so_id','=',obj.id),('product_id','=',line.product_id.id)])
                if ids_mo:
                    raise osv.except_osv(_('Error!'), _('There is exist Manufacturing Order for product %s!'%line.product_id.name))
                res = {}
                company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
                newdate = datetime.strptime(obj.date_order, '%Y-%m-%d') - relativedelta(days=line.product_id.produce_delay or 0.0)
                newdate = newdate - relativedelta(days=company.manufacturing_lead)
                produce_id = production_obj.create(cr, uid, {
                    'origin': obj.name,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'so_id': obj.id,
                    'so_line_id': line.id,
                    'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                    'product_uos': line.product_uos and line.product_uos.id or False,
                    'bom_id': False,
                    'location_src_id': production_obj._src_id_default(cr, uid, []),
                    'location_dest_id': production_obj._dest_id_default(cr, uid, []),
                    'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                    'company_id': obj.company_id and obj.company_id.id or False,
                })
                bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], [])
                wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        #self.action_view_mo(cr, uid, ids, context)
        return True


    def create(self, cr, uid, vals, context=None):
        res = super(sale_order, self).create(cr, uid, vals, context)
        template = self.pool.get('email.template').search(cr, uid, [('name','=','New Sale Order')])
        if template:
            self.pool.get('email.template').send_mail(cr, uid, template[0], int(res), True, context=context)
        return res

    def action_refuse(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})


sale_order()

openoffice_report.openoffice_report(
    'report.report_so_manufacturing',
    'sale.order',
    parser=sale_order
)
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _get_mo(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            wo_id = None
            state = ''
            wo_state = ''
            wo_name ='' # hpusa configure
            production_id = self.pool.get('mrp.production').search(cr, uid, [('so_id','=',record.order_id.id),('so_line_id','=',record.id)])
            if production_id:
                i = 0
                flag = False
                production_obj = self.pool.get('mrp.production').browse(cr, uid, production_id[0])
                if production_obj.workcenter_lines:
                    wc_end =  production_obj.workcenter_lines[len(production_obj.workcenter_lines)-1].id
                    flag = False
                    for wo_line in production_obj.workcenter_lines:
                        #print wo_line.id
                        if wo_line.state != 'done' or wc_end == wo_line.id:
                            if flag == False:
                                wo_id = wo_line.workcenter_id.id
                                wo_state = wo_line.state
                                wo_name= wo_line.workcenter_id.name #hpusa configure
                                flag = True
                                continue
            # hpusa start Configure
            if str(wo_state) =='draft':
                wo_state ='Draft'
            elif str(wo_state)=='waiting_director':
                wo_state ='Waiting Director'
            elif str(wo_state)=='startworking':
                wo_state ='Inprogress'
            elif str(wo_state)=='done':
                wo_state ='Done'
            elif str(wo_state)=='cancel':
                wo_state ='Cancel'
            elif str(wo_state)=='pause':
                wo_state ='Pending'
            # HPUSA Configure 23-04-2015
            self.write(cr, uid, [record.id], {'work_order': str(wo_name), 'work_order_status': str(wo_state)}, context=context) # hpusa configure
            cr.commit() # hpusa configure
            result[record.id] = {'wo_id': wo_id, 'work_state': wo_state}
        return result
    _columns = {
        'wo_id': fields.function(_get_mo, type='many2one', relation="mrp.workcenter", string='Workcenter', multi='mo'),
        'mo_state': fields.function(_get_mo, type='char', string="MO State", multi='mo'),
        'work_state': fields.function(_get_mo, type='char', string="Workorder State", multi='mo'),
        'weight_mo': fields.float('Weight MO'),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
    }
sale_order_line()
