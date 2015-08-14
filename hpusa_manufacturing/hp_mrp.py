import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from openerp.tools import float_compare

class mrp_production_workcenter_line(osv.osv):
    _inherit = "mrp.production.workcenter.line"
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.product.image_medium, avoid_resize_medium=True)
        return result
    _columns = {
         'image_medium': fields.function(_get_image,
            string="Medium-sized image", type="binary", multi="_get_image"),
         'image_small': fields.function(_get_image,
            string="Small-sized image", type="binary", multi="_get_image"),

        'production_id': fields.many2one('mrp.production', 'Manufacturing Order',
            track_visibility='onchange', select=True, ondelete='cascade'),
        'so_id':fields.related('production_id','so_id',type='many2one',relation='sale.order',string='Sale Order', store=True),
        #'planning_id': fields.many2one('mo.planning', 'MO Planning'),
        'state': fields.selection([('draft','Draft'),('cancel','Cancelled'),('confirmed', 'Waiting Material'),('pause','Pending'),('startworking', 'In Progress'),('waiting_director','Waiting Director'),('done','Done')],'Status', readonly=True, track_visibility='onchange',
                                 help="* When a work order is created it is set in 'Draft' status.\n" \
                                       "* When user sets work order in start mode that time it will be set in 'In Progress' status.\n" \
                                       "* When work order is in running mode, during that time if user wants to stop or to make changes in order then can set in 'Pending' status.\n" \
                                       "* When the user cancels the work order it will be set in 'Canceled' status.\n" \
                                       "* When order is completely processed that time it is set in 'Finished' status."),
        'picking_id': fields.related('production_id','picking_id',type='many2one',relation='stock.picking',string='Picking List',readonly=True),
        'employee_id': fields.many2one('hr.employee', string="Responsible"),
        'weight': fields.float(string="Weight"),
        'delivery': fields.one2many('stock.picking', 'wo_delivery_id', string=""),
        'return_': fields.one2many('stock.picking', 'wo_return_id', string=""),
        'lost': fields.one2many('stock.picking', 'wo_lost_id', string=""),
        'amount': fields.float('Amount'),
    }
    def button_waiting_director(self, cr, uid, ids, context = None):
        """ Sets state to done, writes finish date and calculates delay.
        @return: True
        """
        delay = 0.0
        date_now = time.strftime('%Y-%m-%d %H:%M:%S')
        obj_line = self.browse(cr, uid, ids[0])

        date_start = datetime.strptime(obj_line.date_start,'%Y-%m-%d %H:%M:%S')
        date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
        delay += (date_finished-date_start).days * 24
        delay += (date_finished-date_start).seconds / float(60*60)

        self.write(cr, uid, ids, {'state':'done', 'date_finished': date_now,'delay':delay}, context=context)
        self.write(cr, uid, ids, {'state': 'waiting_director'})

    def write(self, cr, uid, ids, vals, context=None):
        if 'return_' in vals:
            obj = self.browse(cr, uid, ids[0])
            print vals['return_']
            #for sale_line in  obj.so_id.order_line:
            #    for item in vals['return_']:
            #        if 'move_lines' in item[2]:
            #            for sm in item[2]['move_lines']:
            #                if not sm[1] and sm[2] and 'product_id' in sm[2]:
            #                    if sm[2]['product_id'] == sale_line.product_id.id:
            #                        self.pool.get('sale.order.line').write(cr, uid, [sale_line.id], {'weight_mo': 'weight_mo' in sm[2] and sm[2]['weight_mo'] or 0, 'weight_mo_unit':'weight_mo_unit' in sm[2] and sm[2]['weight_mo_unit'] or False})
            #                if sm[1] and sm[2] and 'product_id' not in sm[2]:
            #                    stock_move= self.pool.get('stock.move').browse(cr, uid, sm[1])
            #                    if stock_move.product_id.id == sale_line.product_id.id:
            #                        self.pool.get('sale.order.line').write(cr, uid, [sale_line.id], {'weight_mo': 'weight_mo' in sm[2] and sm[2]['weight_mo'] or 0, 'weight_mo_unit':'weight_mo_unit' in sm[2] and sm[2]['weight_mo_unit'] or (stock_move.weight_mo_unit and stock_move.weight_mo_unit.id or False)})

        return super(mrp_production_workcenter_line, self).write(cr, uid, ids, vals)

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        obj = self.browse(cr, uid, ids[0])
        if obj.production_id:
            self.modify_production_order_state(cr,uid,ids,'done')
        return True

    def button_refuse(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_start_working(self, cr, uid, ids, context=None):
        """ Sets state to start working and writes starting date.
        @return: True
        """
        obj = self.browse(cr, uid, ids[0])

        if obj.production_id:
            self.modify_production_order_state(cr, uid, ids, 'start')

        sale_order_id = obj.so_id and  obj.so_id.id or False
        if sale_order_id:
            self.pool.get('sale.order').write(cr, uid, [sale_order_id], {'mo_state': obj.workcenter_id.mo_state})
        self.write(cr, uid, ids, {'state':'startworking', 'date_start': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        template = self.pool.get('email.template').search(cr, uid, [('name','=','Start Work Order')])
        #if template:
            #return self.send_mail_tempalte(cr, uid, ids, template[0], context)
        return True

    def send_mail(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hpusa_manufacturing', 'email_template_edi_start_work_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {}
        ctx.update({
            'default_model': 'mrp.production.workcenter.line',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def send_mail_tempalte(self, cr, uid, ids, template_id, context=None):
        vals = {
              'model': 'mrp.production.workcenter.line',
              'res_id': ids[0],
              'use_template': template_id,
              'composition_mode': 'comment',
        }

        res = self.pool.get('mail.compose.message').onchange_template_id(cr, uid, None, template_id, 'comment', 'mrp.production.workcenter.line', ids[0])


        print 'sssss',res['value']
        if res:
            vals['body'] = res['value']['body']
            vals['subject'] = res['value']['subject']
            vals['subject'] = res['value']['subject']

        mail_id = self.pool.get('mail.compose.message').create(cr, uid, vals)
        raise osv.except_osv(_('DeBug!'), _(" Email template ID: " + str(vals['use_template']) ))

        sql = '''
                update mail_compose_message set template_id = '%s' where id = %s
              '''%(template_id , int(mail_id))
        cr.execute(sql)

        return self.pool.get('mail.compose.message').send_mail(cr, uid, [mail_id])
        return True

mrp_production_workcenter_line()

class mrp_workcenter(osv.osv):
    _inherit = "mrp.workcenter"
    _columns = {
        'mo_state': fields.selection([('3d', '3D Design'),
                                      ('waxmodeling', 'Waxmodeling'),
                                      ('casting', 'Casting'),
                                      ('assembling', 'Assembling'),
                                      ('setting', 'Setting'),
                                      ('polishing', 'Polishing'),
                                      ('engraving', 'Engraving'),
                                     ],'Manufacturing State'),
    }
mrp_workcenter()

def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

class mrp_bom(osv.osv):
    _inherit = "mrp.bom"
    _columns = {
         'code': fields.char('Reference', size=255),
         'so_id': fields.many2one('sale.order','Sale Order'),
         'manufacturing': fields.boolean('Manufacturing'),
    }
    # edit create work order
    def _bom_explode(self, cr, uid, bom, factor, properties=None, addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)

            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level+(wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2

#     def _bom_find(self, cr, uid, product_id, product_uom, properties=None, manufacturing=False):
#         """ Finds BoM for particular product and product uom.
#         @param product_id: Selected product.
#         @param product_uom: Unit of measure of a product.
#         @param properties: List of related properties.
#         @return: False or BoM id.
#         """
#         if properties is None:
#             properties = []
#         cr.execute('select id from mrp_bom where product_id=%s and bom_id is null and manufacturing = %s order by sequence', (product_id,manufacturing))
#         ids = map(lambda x: x[0], cr.fetchall())
#         max_prop = 0
#         result = False
#         for bom in self.pool.get('mrp.bom').browse(cr, uid, ids):
#             prop = 0
#             for prop_id in bom.property_ids:
#                 if prop_id.id in properties:
#                     prop += 1
#             if (prop > max_prop) or ((max_prop == 0) and not result):
#                 result = bom.id
#                 max_prop = prop
#         return result

mrp_bom()

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            print tools.image_get_resized_images(obj.product_id.image_medium, avoid_resize_medium=True)
            result[obj.id] = tools.image_get_resized_images(obj.product_id.image_medium, avoid_resize_medium=True)
        return result
    _columns = {
         'image_medium': fields.function(_get_image,
            string="Medium-sized image", type="binary", multi="_get_image"),
         'image_small': fields.function(_get_image,
            string="Small-sized image", type="binary", multi="_get_image"),
         'so_id': fields.many2one('sale.order','Sale Order'),
         'so_line_id': fields.many2one('sale.order.line','Sale Order Line'),
         'main_production_id': fields.many2one('mrp.production','Main Production'),
         'parent_id': fields.many2one('mrp.production','Parent'),
         'move_lines': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Products to Consume',
            domain=[('state','not in', ('done', 'cancel'))]),
        'move_lines2': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Consumed Products',
            domain=[('state','in', ('done', 'cancel'))]),
        'move_created_ids': fields.one2many('stock.move', 'production_id', 'Products to Produce',
            domain=[('state','not in', ('done', 'cancel'))]),
    }
    def _make_production_line_procurement(self, cr, uid, production_line, shipment_move_id, context=None):
        wf_service = netsvc.LocalService("workflow")
        procurement_order = self.pool.get('procurement.order')
        production = production_line.production_id
        location_id = production.location_src_id.id
        date_planned = production.date_planned
        procurement_name = (production.origin or '').split(':')[0] + ':' + production.name
        procurement_id = procurement_order.create(cr, uid, {
                    'name': procurement_name,
                    'origin': procurement_name,
                    'main_production_id':  production.main_production_id and production.main_production_id.id or False,
                    'parent_id':  production.id,
                    'date_planned': date_planned,
                    'so_id': production.so_id and production.so_id.id or False,
                    'product_id': production_line.product_id.id,
                    'product_qty': production_line.product_qty,
                    'product_uom': production_line.product_uom.id,
                    'product_uos_qty': production_line.product_uos and production_line.product_qty or False,
                    'product_uos': production_line.product_uos and production_line.product_uos.id or False,
                    'location_id': location_id,
                    'procure_method': production_line.product_id.procure_method,
                    'move_id': shipment_move_id,
                    'company_id': production.company_id and production.company_id.id or False,
                })
        wf_service.trg_validate(uid, procurement_order._name, procurement_id, 'button_confirm', cr)
        return procurement_id

    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):

            p_ids = prod_line_obj.search(cr, SUPERUSER_ID, [('production_id', '=', production.id)], context=context)
            prod_line_obj.unlink(cr, SUPERUSER_ID, p_ids, context=context)
            w_ids = workcenter_line_obj.search(cr, SUPERUSER_ID, [('production_id', '=', production.id)], context=context)
            workcenter_line_obj.unlink(cr, SUPERUSER_ID, w_ids, context=context)

            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                print 'sss', bom_id
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0]
            results2 = res[1]

            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                line['so_id'] = production.so_id and production.so_id.id or False
                workcenter_line_obj.create(cr, uid, line)
        return len(results)

    def _make_production_internal_shipment(self, cr, uid, production, context=None):
        ir_sequence = self.pool.get('ir.sequence')
        stock_picking = self.pool.get('stock.picking')
        routing_loc = None
        pick_type = 'internal'
        partner_id = False

        # Take routing address as a Shipment Address.
        # If usage of routing location is a internal, make outgoing shipment otherwise internal shipment
        if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
            routing_loc = production.bom_id.routing_id.location_id
            if routing_loc.usage != 'internal':
                pick_type = 'out'
            partner_id = routing_loc.partner_id and routing_loc.partner_id.id or False

        # Take next Sequence number of shipment base on type
        pick_name = ir_sequence.get(cr, uid, 'stock.picking')
        picking_id = stock_picking.create(cr, uid, {
            'name': pick_name,
            'origin': (production.origin or '').split(':')[0] + ':' + production.name,
            'type': pick_type,
            'move_type': 'one',
            'state': 'auto',
            'partner_id': partner_id,
            'auto_picking': self._get_auto_picking(cr, uid, production),
            'company_id': production.company_id.id,
        })
        production.write({'picking_id': picking_id}, context=context)
        return picking_id

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        if not product_id:
            return {'value': {
                'product_uom': False,
                'bom_id': False,
                'routing_id': False
            }}
        bom_obj = self.pool.get('mrp.bom')
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        bom_id = bom_obj._bom_find(cr, uid, product.id, product.uom_id and product.uom_id.id, [])
        routing_id = False
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom_point.routing_id.id or False

        product_uom_id = product.uom_id and product.uom_id.id or False
        result = {
            'product_uom': product_uom_id,
            'bom_id': bom_id,
            'routing_id': routing_id,
        }
        return {'value': result}

    def action_produce(self, cr, uid, production_id, production_qty, weight_mo, weight_mo_unit, production_mode, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce
        @param production_mode: specify production mode (consume/consume&produce).
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)

        produced_qty = 0
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id != production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        if production_mode in ['consume','consume_produce']:
            consumed_data = {}

            # Calculate already consumed qtys
            for consumed in production.move_lines2:
                if consumed.scrapped:
                    continue
                if not consumed_data.get(consumed.product_id.id, False):
                    consumed_data[consumed.product_id.id] = 0
                consumed_data[consumed.product_id.id] += consumed.product_qty

            # Find product qty to be consumed and consume it
            for scheduled in production.product_lines:

                # total qty of consumed product we need after this consumption
                total_consume = ((production_qty + produced_qty) * scheduled.product_qty / production.product_qty)

                # qty available for consume and produce
                qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)

                if qty_avail <= 0.0:
                    # there will be nothing to consume for this raw material
                    continue

                raw_product = [move for move in production.move_lines if move.product_id.id==scheduled.product_id.id]
                if raw_product:
                    # qtys we have to consume
                    qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
                    if float_compare(qty, qty_avail, precision_rounding=scheduled.product_id.uom_id.rounding) == 1:
                        # if qtys we have to consume is more than qtys available to consume
                        prod_name = scheduled.product_id.name_get()[0][1]
                        raise osv.except_osv(_('Warning!'), _('You are going to consume total %s quantities of "%s".\nBut you can only consume up to total %s quantities.') % (qty, prod_name, qty_avail))
                    if qty <= 0.0:
                        # we already have more qtys consumed than we need
                        continue

                    raw_product[0].action_consume1(qty, raw_product[0].location_id.id, weight_mo = raw_product[0].weight_mo * qty/raw_product[0].product_qty, weight_mo_unit = raw_product[0].weight_mo_unit and raw_product[0].weight_mo_unit.id or False, context=context)

        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            #vals = {'state':'confirmed'}
            #final_product_todo = [x.id for x in production.move_created_ids]
            #stock_mov_obj.write(cr, uid, final_product_todo, vals)
            #stock_mov_obj.action_confirm(cr, uid, final_product_todo, context)
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty

            for produce_product in production.move_created_ids:
                produced_qty = produced_products.get(produce_product.product_id.id, 0)
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                rest_qty = (subproduct_factor * production.product_qty) - produced_qty

                if rest_qty < production_qty:
                    prod_name = produce_product.product_id.name_get()[0][1]
                    raise osv.except_osv(_('Warning!'), _('You are going to produce total %s quantities of "%s".\nBut you can only produce up to total %s quantities.') % (production_qty, prod_name, rest_qty))
                if rest_qty > 0 :
                    #stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)
                    if produce_product.product_id.id == production.product_id.id:
                        stock_mov_obj.action_consume1(cr, uid, [produce_product.id], (subproduct_factor * production_qty), weight_mo = weight_mo, location_id = False, weight_mo_unit = weight_mo_unit, context=context)
                        #cap nhat lai so luong va trong luong cho giai doan ke tiep
                        if production.parent_id:
                            if production.parent_id.picking_id:
                                for stock_move in production.parent_id.picking_id.move_lines:
                                    if stock_move.product_id.id == production.product_id.id:
                                        self.pool.get('stock.move').write(cr, uid, [stock_move.id], {'product_qty': (subproduct_factor * production_qty), 'weight_mo': weight_mo, 'weight_mo_unit': weight_mo_unit})
                    else:
                        stock_mov_obj.action_consume1(cr, uid, [produce_product.id], (subproduct_factor * production_qty), weight_mo = produce_product.weight_mo, location_id = False, weight_mo_unit = produce_product.weight_mo_unit and produce_product.weight_mo_unit.id or False, context=context)
        for raw_product in production.move_lines2:
            new_parent_ids = []
            parent_move_ids = [x.id for x in raw_product.move_history_ids]
            for final_product in production.move_created_ids2:
                if final_product.id not in parent_move_ids:
                    new_parent_ids.append(final_product.id)
            for new_parent_id in new_parent_ids:
                stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
        return True

    def force_production(self, cr, uid, ids, *args):
        """ Assigns products.
        @param *args: Arguments
        @return: True
        """
        pick_obj = self.pool.get('stock.picking')
        pick_obj.force_assign(cr, uid, [prod.picking_id.id for prod in self.browse(cr, uid, ids)])
        self.write(cr, uid, ids, {'state': 'ready'})
        return True

    def write(self, cr, uid, ids, vals, context = None):
        if 'move_lines' in vals:
            if vals['move_lines']:
                print vals['move_lines']
                if len(vals['move_lines'][0]) > 2:
                    for item in vals['move_lines'][0][2]:
                        sql = '''INSERT INTO mrp_production_move_ids VALUES(%s,%s)'''%(ids[0], item)
                        cr.execute(sql)
                    vals['move_lines'] = None
        return super(mrp_production, self).write(cr, uid, ids, vals, context)

    def action_ready(self, cr, uid, ids, context=None):
        """ Changes the production state to Ready and location id of stock move.
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'ready'})

        for (production_id,name) in self.name_get(cr, uid, ids):
            production = self.browse(cr, uid, production_id)
            location_production = production.move_lines and production.move_lines[0].location_dest_id.id
            if production.picking_id:
                for item in production.picking_id.move_lines:
                    flag = False
                    for consume in production.move_lines:
                        if consume.id == item.move_dest_id.id:
                            flag = True
                            if consume.product_qty != item.product_qty or consume.weight_mo != item.weight_mo:
                                move_obj.write(cr, uid, [consume.id],{'product_qty': item.product_qty, 'weight_mo': item.weight_mo, 'product_uom': item.product_uom.id, 'weight_mo_unit': item.weight_mo_unit and item.weight_mo_unit.id or False})
                    if flag == False:
                        new_mome_id = self.pool.get('stock.move').copy(cr,uid, item.id, {'state':'assigned', 'picking_id': False, 'location_id': item.location_dest_id.id, 'location_dest_id': location_production}, context = context)
                        print new_mome_id
                        move_obj.write(cr, uid, [item.id],{'move_dest_id': new_mome_id})

                        self.write(cr, uid, production.id, {'move_lines': [(4, new_mome_id)]})

            if production.move_prod_id and production.move_prod_id.location_id.id != production.location_dest_id.id:
                move_obj.write(cr, uid, [production.move_prod_id.id],
                        {'location_id': production.location_dest_id.id})
        return True

mrp_production()

class change_production_qty(osv.osv_memory):
    _inherit = 'change.production.qty'


    def change_prod_qty(self, cr, uid, ids, context=None):
        """
        Changes the Quantity of Product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        record_id = context and context.get('active_id',False)
        assert record_id, _('Active Id not found')
        prod_obj = self.pool.get('mrp.production')
        bom_obj = self.pool.get('mrp.bom')
        move_obj = self.pool.get('stock.move')
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            prod = prod_obj.browse(cr, uid, record_id, context=context)
            prod_obj.write(cr, uid, [prod.id], {'product_qty': wiz_qty.product_qty})
            prod_obj.action_compute(cr, uid, [prod.id])

            for move in prod.move_lines:
                bom_point = prod.bom_id
                bom_id = prod.bom_id.id
                if not bom_point:
                    bom_id = bom_obj._bom_find(cr, uid, prod.product_id.id, prod.product_uom.id, [])
                    if not bom_id:
                        raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))
                    prod_obj.write(cr, uid, [prod.id], {'bom_id': bom_id})
                    bom_point = bom_obj.browse(cr, uid, [bom_id])[0]

                if not bom_id:
                    raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))

                factor = prod.product_qty * prod.product_uom.factor / bom_point.product_uom.factor
                product_details, workcenter_details = \
                    bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, [])
                product_move = dict((mv.product_id.id, mv.id) for mv in prod.picking_id.move_lines)
                for r in product_details:
                    if r['product_id'] == move.product_id.id:
                        move_obj.write(cr, uid, [move.id], {'product_qty': r['product_qty']})
                    if r['product_id'] in product_move:
                        move_obj.write(cr, uid, [product_move[r['product_id']]], {'product_qty': r['product_qty']})
            if prod.move_prod_id:
                move_obj.write(cr, uid, [prod.move_prod_id.id], {'product_qty' :  wiz_qty.product_qty})
            self._update_product_to_produce(cr, uid, prod, wiz_qty.product_qty, context=context)
        return {}

change_production_qty()

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"

    _columns = {
        'weight_mo': fields.float('Weight MO'),
        'weight_mo_unit': fields.many2one('product.uom', 'Weight UOM'),
    }

    def do_produce(self, cr, uid, ids, context=None):
        production_id = context.get('active_id', False)
        assert production_id, "Production Id should be specified in context as a Active ID."
        data = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('mrp.production').action_produce(cr, uid, production_id,
                            data.product_qty, data.weight_mo, data.weight_mo_unit and data.weight_mo_unit.id or False, data.mode, context=context)
        return {}

mrp_product_produce()

class stock_move(osv.osv):
    _inherit = "stock.move"

    def action_consume1(self, cr, uid, ids, product_qty, location_id=False, weight_mo = 0, weight_mo_unit = False, context=None):
        """ Consumed product with specific quatity from specific source location.
        @param product_qty: Consumed product quantity
        @param location_id: Source location
        @return: Consumed lines
        """
        res = []
        print '234'
        production_obj = self.pool.get('mrp.production')
        wf_service = netsvc.LocalService("workflow")
        for move in self.browse(cr, uid, ids):
            move.action_confirm(context)
            new_moves = super(stock_move, self).action_consume1(cr, uid, [move.id], product_qty, location_id, weight_mo , weight_mo_unit, context=context)
            production_ids = production_obj.search(cr, uid, [('move_lines', 'in', [move.id])])
            for prod in production_obj.browse(cr, uid, production_ids, context=context):
                if prod.state == 'confirmed':
                    production_obj.force_production(cr, uid, [prod.id])
                wf_service.trg_validate(uid, 'mrp.production', prod.id, 'button_produce', cr)
            for new_move in new_moves:
                if new_move == move.id:
                    #This move is already there in move lines of production order
                    continue
                print 's', new_move
                production_obj.write(cr, uid, production_ids, {'move_lines': [(4, new_move)]})
                res.append(new_move)
        return res
stock_move()


