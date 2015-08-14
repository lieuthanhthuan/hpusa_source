
# -*- coding: utf-8 -*-
##############################################################################
##############################################################################

from osv import fields, osv
from tools.translate import _
import time
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
from docutils.languages import de
from openerp import SUPERUSER_ID

class wizard_hpusa_report(osv.osv_memory):
    _name = "wizard.hpusa.report"
    _columns = {
            'date_from': fields.date('Date From',required=True),
            'date_to': fields.date('Date To',required=True),
            
            # Hpusa configure 04-06-2015
            #'so_id': fields.many2one('sale.order','Sale Order'),
            'so_id': fields.many2many('sale.order','sale_order_hpusa_report', 'wizard_hpusa_report_id', 'so_id','Sale Orders'),
            # Hpusa configure 04-06-2015

     }
    _defaults={
              'date_from': lambda *a: time.strftime('%Y-%m-01'),
              'date_to': lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }
    def action_print(self, cr, uid, ids, context = None):
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_from','date_to','so_id','location_id'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        datas['model'] = 'wizard.hpusa.report'
        name = self.pool.get('res.users').browse(cr, uid, uid).partner_id.name
        datas['form']['name'] = name
        type = context.get('type_', '')
        if type == 'manufacturing_summary':
            datas['line'] = self.print_manufacturing_summary(cr, uid, res['date_from'], res['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'manufacturing_summary',
                'datas'         : datas,
           }

        if type == 'manufacturing_detail':
            datas['line'] = self.print_manufacturing_detail(cr, uid, res['date_from'], res['date_to'],res['so_id'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'manufacturing_detail',
                'datas'         : datas,
           }

        if type == 'material_repair_summary':
            datas['line'] = self.print_material_repair_summary(cr, uid, res['date_from'], res['date_to'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'material_repair_summay',
                'datas'         : datas,
           }

        if type == 'v_invoice':
            datas['line'] = self.manufacturing_v_invoice(cr, uid, res['date_from'], res['date_to'],res['so_id'])
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'manufacturing_v_invoice',
                'datas'         : datas,
           }


#         if type == 'material_produce_summary':
#             datas['line'] = self.print_material_produce_summary(cr, uid, res['date_from'], res['date_to'])
#             return {
#                 'type'          : 'ir.actions.report.xml',
#                 'report_name'   : 'material_produce_summary',
#                 'datas'         : datas,
#            }

#     def print_manufacturing_summary(self, cr, uid, date_form, date_to):
#         sql = '''
#             SELECT mrp.date_start, mrp.name, p.default_code, p.name_template
#             FROM mrp_production mrp
#             LEFT JOIN product_product p ON(p.id = mrp.product_id)
#             WHERE mrp.date_start >= '%s' AND mrp.date_start <='%s'
#         '''%(date_form, date_to)
#         cr.execute(sql)
#         result = cr.dictfetchall()
#         arr = []
#         for item in result:
#             arr.append({
#                         'date': item['date_start'],
#                         'mo_name': item['name'],
#                         'default_code': item['default_code'],
#                         'name_product': item['name_template'],
#                         })
#         return arr

    def manufacturing_v_invoice(self, cr, uid, date_form, date_to,so_id):
        pricelist_obj = self.pool.get('product.pricelist')
        product_uom = self.pool.get('product.uom')
        manufacturing = self.print_manufacturing_detail(cr, uid, date_form, date_to,so_id)
        
	pricelist = self.pool.get('product.pricelist')
        currency_obj = self.pool.get('res.currency')


        # hpusa 03-06-2015
        index = 0
        i=0
        sale_id = 0
        parrent_product = 0
        work_order_id = 0
        # hpusa 03-06-2015
        
        for item in manufacturing:
            if item['product_id']:
                product_obj = self.pool.get('product.product').browse(cr, uid, item['product_id'])
                sale_price = 0
                setting_price = 0
                standard_price = 0
                work_order_price = 0
                
                uom = self.pool.get('product.uom').search(cr, uid, [('name','=',item['uom'])])
                if item['so_id']:
                    # hpusa 03-06-2015
                    index=i
                    cost_price = 0
                    parrent_product_id = product_obj.id
                    # hpusa 03-06-2015
                    
                    sale_order = self.pool.get('sale.order').browse(cr, SUPERUSER_ID, item['so_id'])
                    pricelist = sale_order.pricelist_id
                    
                    # hpusa 03-06-2015
                    sale_id =sale_order.id
                    result=self.get_bom(cr,SUPERUSER_ID,item['so_id'], item['product_id'])
                    # hpusa 03-06-2015
                    
                    if uom and pricelist:
                        price_supplier = pricelist_obj.price_get(cr,SUPERUSER_ID,[pricelist.id], item['product_id'], 1.0, partner=None,context=None)
                        sale_price = product_uom._compute_price(cr, SUPERUSER_ID, product_obj.uom_id.id, price_supplier[pricelist.id], to_uom_id=uom[0])
                else:
                    sale_price = product_obj.list_price
                setting_price = product_uom._compute_price(cr, uid, product_obj.uom_id.id, product_obj.setting_price, to_uom_id=uom[0])
                standard_price = product_uom._compute_price(cr, uid, product_obj.uom_id.id, product_obj.standard_price, to_uom_id=uom[0])
                

		setting_price = currency_obj.compute(cr, uid,
                                    3, pricelist.currency_id.id,
                                    setting_price, round=False,
                                    context=None)
                
                standard_price = currency_obj.compute(cr, uid,
                                    3, pricelist.currency_id.id,
                                    standard_price, round=False,
                                    context=None)

                #item['price'] = str((product_obj.standard_price or 0.0) )
                item['price'] = str((standard_price or 0.0) )


                item['setting_price'] = str(setting_price or 0.0)
                item['total_amount'] = str((float(standard_price or 0.0)) * (float(item['qty_real'] or 0.0)))                
                item['total_setting'] = str(((setting_price or 0.0) * float(item['qty_real'] or 0.0)) )
                
                # hpusa 03-06-2015
                item['cost_price'] = ''
                item['sale_price'] = ''
                item['qty_bom']= self.get_bom_qty(cr, uid, parrent_product_id, product_obj.id, context=None)
                cost_price+= float(item['total_amount']) + float(item['total_setting'])
                # hpusa 03-06-2015
                
                #item['cost_price'] = str(standard_price or 0.0)
                #item['sale_price'] = str(sale_price or 0.0)
            # hpusa 03-06-2015 
            elif item['wc_id']:
                    work_order_price = 0
                   
                    worcenter_id= int(item['wc_id'])
                    work_center= self.pool.get('mrp.workcenter').browse(cr,SUPERUSER_ID,worcenter_id,context=None)
                    item['price']= self.get_wc_price(cr, SUPERUSER_ID, worcenter_id, context=None)
                    item['price'] = currency_obj.compute(cr, uid,
                                    3, pricelist.currency_id.id,
                                    item['price'], round=False,
                                    context=None)  
                    if(work_center.product_id):    
                        item['qty_bom']= self.get_bom_qty(cr, SUPERUSER_ID, parrent_product_id, work_center.product_id.id, context=None)
                    item['total_amount']= str( float( item['price']* float(item['qty_real'])))
                    cost_price+= float(item['total_amount'])    
                    item['setting_price'] = ''
                    item['total_setting'] = ''
                    item['cost_price'] = ''
                    item['sale_price'] = ''
            # hpusa 03-06-2015
                        
            else:
                item['price'] = ''
                item['setting_price'] = ''
                item['total_amount'] = ''
                item['cost_price'] = ''
                item['sale_price'] = ''
                item['total_setting'] = ''
            
            # hpusa 03-06-2015
            manufacturing[index]['total_amount']=str(cost_price)

            item['gram_real']= abs(float( item['gram_real'] or 0))
            item['qty_real']= abs(float(item['qty_real'] or 0))
            item['carat_real']= abs(float(item['carat_real'] or 0))

            work_order_price
            if item['so_id']:
                manufacturing[index]['cost_price']= str(round(float(result[0]['cost_price']),2))
                manufacturing[index]['sale_price']= str(round(float(result[0]['sale_price']),2))
            i+=1
            #print 'Gia von:' + str(cost_price)
            # hpusa 03-06-2015
        return manufacturing


    def print_manufacturing_detail(self, cr, uid, date_form, date_to,so_id):
        # hpusa 04-06-2015
	if so_id:
            so_ids = self.pool.get('sale.order').search(cr, SUPERUSER_ID, [('id','in',so_id)]) 
        else:
            so_ids = self.pool.get('sale.order').search(cr, SUPERUSER_ID, [('date_order','<=',date_to),('date_order','>=',date_form)])        
        # hpusa 04-06-2015

        arr = []
        last_finish_id=0
        last_id_wo =0
        stt = 1
        #print so_ids
        if so_ids:
            for so in self.pool.get('sale.order').browse(cr, SUPERUSER_ID, so_ids):
                for item in so.order_line:
                    production_ids = self.pool.get('mrp.production').search(cr, SUPERUSER_ID, [('so_line_id','=',item.id)])
                    if production_ids:
                        # get SO infomation 
                        arr.append({
                                    'stt': stt,
                                    'so_name': item.order_id.name + '-' + item.order_id.partner_id.name + '-' + item.order_id.create_date,
                                    'so_id': so.id,
                                    'style': item.product_id.default_code and item.product_id.default_code or '',
                                    'type': item.product_id.metal_type and item.product_id.metal_type or '',
                                    'employee': '',
                                    'wc': '',
                                    'wo_time': '',
                                    'product_name': item.product_id.name,
                                    'product_id': item.product_id.id,
                                    'qty_delivery': item.product_uom_qty,
                                    'weight_delivery': item.weight_mo,
                                    'qty_return': '',
                                    'weight_return': '',
                                    'qty_lost': '',
                                    'weight_lost': '',
                                    'uom': item.product_uom.name,
                                    'qty_bom': '',
                                    'qty_real': item.product_uom_qty,
                                    'carat_real': '',
                                    'gram_real': '',
                                    'rate_qty_lost': '',
                                    'rate_lost': '',
                                    'amount': 0,
                                })
                        last_finish_id = len(arr)-1
                        stt += 1

                        for mrp in self.pool.get('mrp.production').browse(cr, SUPERUSER_ID, production_ids):
                            total_amount = 0.0
                            # get work Order information 
                            for wo in mrp.workcenter_lines:
                                arr.append({
                                        'stt': '',
                                        'so_name': '',
                                        'so_id': wo.so_id.id,
                                        'style': '',
                                        'type': '',
                                        'employee': wo.employee_id and wo.employee_id.name or '',
                                        'wc_id': wo.workcenter_id.id,
                                        'wc': wo.workcenter_id and wo.workcenter_id.name or '',
                                        'wo_time': wo.delay > 0 and str(round(wo.delay,2)) or '0.00',
                                        'product_name': '',
                                        'product_id': False,
                                        'qty_delivery': wo.qty,
                                        'weight_delivery': '',
                                        'qty_return': '',
                                        'weight_return': '',
                                        'qty_lost': '',
                                        'weight_lost': '',
                                        'uom': '',
                                        'qty_bom': wo.qty,
                                        'qty_real': wo.cycle+wo.hour,
                                        #'qty_real': wo.qty,
                                        'carat_real': '',
                                        'gram_real': '',
                                        'rate_qty_lost': '',
                                        'rate_lost': '',
                                        'amount': wo.amount,
                                    })
                                last_id_wo=len(arr)-1
                                arr_product = []
                                for stock_picking in wo.delivery + wo.return_ + wo.lost:
                                    for stock_move in stock_picking.move_lines:
                                        index = None
                                        i = 0
                                        if arr_product:
                                            for product in arr_product:
                                                for pid in product:
                                                    if int(pid) == stock_move.product_id.id:
                                                        index = i
                                                    break
                                                i += 1
                                        if not arr_product or index == None:
                                            arr_product.append({
                                                '%s'%stock_move.product_id.id: {
                                                                                'qty_delivery': stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.product_qty or 0,
                                                                                'weight_delivery': stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0,
                                                                                'qty_return': stock_move.picking_id.hp_transfer_type =='return' and stock_move.product_qty or 0,
                                                                                'weight_return': stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0,
                                                                                'qty_lost': stock_move.picking_id.hp_transfer_type =='lost' and stock_move.weight_mo or 0,
                                                                                'weight_lost': stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0,
                                                                                'uom': stock_move.product_uom.name,
                                                                                'standard_price': stock_move.product_id.standard_price,
                                                                                'product_name': stock_move.product_id.name,
                                                                                'product_id': stock_move.product_id.id,
                                                                                'carat_real': stock_move.product_id.hp_type == 'diamonds' and ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))  or 0,
                                                                                'gram_real': stock_move.product_id.hp_type == 'diamonds' and (((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)) / 5) or ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))
                                                                            }})
                                        else:
                                            arr_sm = arr_product[index]
                                            arr_sm['%s'%stock_move.product_id.id]['qty_delivery'] = arr_sm['%s'%stock_move.product_id.id]['qty_delivery'] + (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.product_qty or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['weight_delivery'] = arr_sm['%s'%stock_move.product_id.id]['weight_delivery'] + (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['qty_return'] = arr_sm['%s'%stock_move.product_id.id]['qty_return'] + (stock_move.picking_id.hp_transfer_type =='return' and stock_move.product_qty or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['weight_return'] = arr_sm['%s'%stock_move.product_id.id]['weight_return'] + (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['qty_lost']  = arr_sm['%s'%stock_move.product_id.id]['qty_lost'] + (stock_move.picking_id.hp_transfer_type =='lost' and stock_move.product_qty or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['weight_lost'] = arr_sm['%s'%stock_move.product_id.id]['weight_lost'] + (stock_move.picking_id.hp_transfer_type =='lost' and stock_move.weight_mo or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['carat_real'] = arr_sm['%s'%stock_move.product_id.id]['carat_real'] + (stock_move.product_id.hp_type == 'diamonds' and ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))  or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['gram_real'] = arr_sm['%s'%stock_move.product_id.id]['gram_real'] + (stock_move.product_id.hp_type == 'diamonds' and (((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)) / 5) or ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)))
                                for product in arr_product:
                                    product_id = None
                                    for pid in product:
                                        product_id = pid
                                        break
                                    
                                    # get item material infomation    
                                    arr.append({
                                            'stt': '',
                                            'so_name': '',
                                            'so_id': '',
                                            'style': '',
                                            'type': '',
                                            'employee': '',
                                            'wc': '',
                                            'wo_time': '',
                                            'product_name': product[product_id]['product_name'],
                                            'product_id':  product[product_id]['product_id'],
                                            'qty_delivery': product[product_id]['qty_delivery'],
                                            'weight_delivery': product[product_id]['weight_delivery'],
                                            'qty_return': product[product_id]['qty_return'],
                                            'weight_return': product[product_id]['weight_return'],
                                            'qty_lost': product[product_id]['qty_lost'],
                                            'weight_lost': product[product_id]['weight_lost'],
                                            'uom': product[product_id]['uom'],
                                            'qty_bom': '',
                                            'qty_real': product[product_id]['qty_delivery'] - product[product_id]['qty_return'] - product[product_id]['qty_lost'],
                                            'carat_real': product[product_id]['carat_real'],
                                            'gram_real': product[product_id]['gram_real'],
                                            'rate_qty_lost':product[product_id]['qty_delivery'] - product[product_id]['qty_return'] - product[product_id]['qty_lost'],
                                            'rate_lost': round((product[product_id]['qty_delivery'] != 0 and (product[product_id]['qty_delivery'] - product[product_id]['qty_return'] - product[product_id]['qty_lost']) / product[product_id]['qty_delivery'] or 0) * 100, 2),
                                            'amount': 0,
                                        })

        return arr

    def print_material_repair_summary(self, cr, uid, date_from, date_to):
        arr = []
        repair_ids = self.pool.get('mrp.repair').search(cr, uid, [('date','>=', date_from),('date','<=', date_to)])
        for repair in self.pool.get('mrp.repair').browse(cr, uid, repair_ids):
            flag = False
            for repair_line in repair.operations:
                if flag == False:
                    arr.append({
                                'date': repair.date,
                                'name': repair.name,
                                'partner': repair.partner_id and repair.partner_id.name or '',
                                'product': repair.product_id.name,
                                'old_size': repair.receipt_size,
                                'new_size': repair.new_size,
                                'old_weight':repair.receipt_weight,
                                'new_weight': repair.finish_weight,
                                'worker': repair.employee_id and repair.employee_id.name or '',
                                'type': repair_line.type,
                                'product_material': repair_line.product_id.name,
                                'product_material_code': repair_line.product_id.default_code,
                                'product_qty': repair_line.product_uom_qty,
                                'product_uom': repair_line.product_uom.name,
                                'note': repair.internal_notes or '',
                               })
                    flag = True
                else:
                    arr.append({
                                'date': '',
                                'name': '',
                                'partner': '',
                                'product': '',
                                'old_size': '',
                                'new_size': '',
                                'old_weight':'',
                                'new_weight': '',
                                'worker': '',
                                'type': repair_line.type,
                                'product_material': repair_line.product_id.name,
                                'product_material_code': repair_line.product_id.default_code,
                                'product_qty': repair_line.product_uom_qty,
                                'product_uom': repair_line.product_uom.name,
                                'note': repair.internal_notes or '',
                               })
        return arr
    
    
    def get_bom(self,cr,uid,order_id ,product_id):
        res = {}
        pricelist_obj = self.pool.get('product.pricelist')
        bom_obj = self.pool.get('mrp.bom')
        product_uom = self.pool.get('product.uom')

        # hpusa confgure 28-05-2015
        currency_obj = self.pool.get('res.currency')
        pricelist_version = self.pool.get('product.pricelist.version')
        # hpusa confgure 28-05-2015

        result = []
        product_ = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        bom_id = bom_obj._bom_find(cr, uid, product_id, product_.uom_id and product_.uom_id.id, [])

	
        von=0
	pricelist_id=0
        for bom in bom_obj.browse(cr, uid, [bom_id]):

            # Tinh gia von cua san pham
            von=0
            for bom_line in bom.bom_lines:
                prl=self.pool.get('sale.order').browse(cr,uid,order_id,context=None)
                pricelist = prl.pricelist_id
                pricelist_id =pricelist.id
                cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                        #cost_price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                cost_price = currency_obj.compute(cr, uid,
                                    3, pricelist.currency_id.id,
                                    cost_p, round=False,
                                    context=None)
                von +=cost_price *bom_line.product_qty
        plist_versions= self.get_price_list_version(cr,uid,pricelist_id,von)
        # Tinh gia von cua san pham

        for bom in bom_obj.browse(cr, uid, [bom_id]):
            total_amount = 0
            for bom_line in bom.bom_lines:
                #pricelist = object_order.order_id.pricelist_id
                prl=self.pool.get('sale.order').browse(cr,uid,order_id,context=None)
                pricelist = prl.pricelist_id
                # hpusa configures 27-05-2015
                price_supplier = pricelist_version.hpusa_price_get(cr,uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0,plist_versions, partner=None,context=None)
                # hpusa configures 27-05-2015

                #gs
                #price_supplier = pricelist_obj.price_get(cr,uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0, partner=None,context=None)
                price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist.id], to_uom_id=bom_line.product_uom.id)
                total_amount+=float(price*bom_line.product_qty or 0)
                uom_ids = product_uom.search(cr, uid, [('uom_type','=','reference'),('category_id','=',bom_line.product_uom.category_id.id)])
                if uom_ids:
                    uom = product_uom.browse(cr, uid, uom_ids[0])
            res = {
                'cost_price' : von,
                'sale_price' : total_amount,
            }
            result.append(res)
                
        return result    
    
     # hpusa configures 27-05-2015
    def get_price_list_version(self,cr,uid,price_list,amount,context=None):
        val_return =0
        pricelist_version_ids = self.pool.get('product.pricelist.version').search(cr, uid, [('pricelist_id', '=', price_list)])
        for version_id in pricelist_version_ids:
            version= self.pool.get('product.pricelist.version').browse(cr,uid,version_id)
            if(version.min_amount<= amount and version.max_amount>=amount):
                val_return = version_id
                break
            else:
                val_return = -1
        return val_return
        
    
    def get_bom_qty(self, cr, uid, product_parrent,product_id, context=None):
       
        bom_obj = self.pool.get('mrp.bom')
        product_uom = self.pool.get('product.uom')
        product_ = self.pool.get('product.product').browse(cr, uid, product_parrent, context=None)
        bom_id = bom_obj._bom_find(cr, uid, product_parrent, product_.uom_id and product_.uom_id.id, [])    
        bom_qty = 0
        for bom in bom_obj.browse(cr, uid, [bom_id]):
           
            for bom_line in bom.bom_lines:
                if(bom_line.product_id.id == product_id):
                    bom_qty = bom_line.product_qty
                    break      
        return bom_qty
    
    def get_wc_price(self, cr, uid, wc_id, context=None):
        workcenter = self.pool.get('mrp.workcenter').browse(cr,uid,wc_id,context=None)
        
        price =0;
        qty=0
        if(workcenter.product_id):
            price=workcenter.product_id.standard_price
   
        return price 
    # hpusa configures 27-05-2015
     
wizard_hpusa_report()

# openoffice_report.openoffice_report(
#     'report.manufacturing_summary',
#     'wizard.hpusa.report',
#     parser=wizard_hpusa_report
# )

openoffice_report.openoffice_report(
    'report.manufacturing_detail',
    'wizard.hpusa.report',
    parser=wizard_hpusa_report
)

openoffice_report.openoffice_report(
    'report.material_repair_summay',
    'wizard.hpusa.report',
    parser=wizard_hpusa_report
)

openoffice_report.openoffice_report(
    'report.manufacturing_v_invoice',
    'wizard.hpusa.report',
    parser=wizard_hpusa_report
)
#
# openoffice_report.openoffice_report(
#     'report.material_produce_summary',
#     'wizard.hpusa.report',
#     parser=wizard_hpusa_report
# )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
