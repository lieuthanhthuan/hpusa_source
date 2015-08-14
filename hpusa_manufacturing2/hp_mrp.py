import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from openerp.tools import float_compare

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def _get_mo(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for production_id in ids:
            wo_state=''
            wo_name=''
            wo_id=0
            if production_id:
                i = 0
                flag = False
                production_obj = self.browse(cr, uid, production_id)
                if production_obj.workcenter_lines:
                    wc_end =  production_obj.workcenter_lines[len(production_obj.workcenter_lines)-1].id
                    flag = False
                    for wo_line in production_obj.workcenter_lines:
                        #print wo_line.id
                        if wo_line.state != 'done' or wc_end == wo_line.id:
                            if flag == False:
                                wo_id = wo_line.workcenter_id.id
                                wo_state = wo_line.state
                                #wo_name= wo_line.workcenter_id.name #hpusa configure
                                flag = True
                                break
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
            #self.write(cr, uid, [record.id], {'work_order': str(wo_name), 'work_order_status': str(wo_state)}, context=context) # hpusa configure
            #cr.commit() # hpusa configure
            result[production_id] = {'wo_id': wo_id, 'work_state': wo_state}
        return result
     
    def update_loss(self,cr,uid,ids,context=None ):    
        arr = []
        last_finish_id=0
        last_id_wo =0
        stt = 1
        ex_index = 0
        values=[]
                  
        for mrp in self.browse(cr, uid, ids):
            total_amount = 0.0
            total_delivery_metal=0;
            total_return_metal=0;
            total_delivery_diamond=0;
            total_return_diamond=0;
            total_qty_diamond_delivery=0;
            total_qty_diamond_return=0;
            finised_weight =0;
            
            for wo in mrp.workcenter_lines:
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
                            'hp_type':stock_move.product_id.hp_type,
                            'carat_real': stock_move.product_id.hp_type == 'diamonds' and ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))  or 0,
                            'gram_real': stock_move.product_id.hp_type == 'diamonds' and (((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)) / 5) or ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))
                                            }})
                            
                            if(stock_move.product_id.hp_type=='diamonds'):
                                 total_qty_diamond_delivery+= float(stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.product_qty or 0)
                                 total_delivery_diamond += float(stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0)
                                 total_return_diamond += float(stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)
                                 total_qty_diamond_return += float(stock_move.picking_id.hp_transfer_type =='return' and stock_move.product_qty or 0)                       
                            
                            elif(stock_move.product_id.hp_type=='metal') or (stock_move.product_id.hp_type=='finish_product') or (stock_move.product_id.hp_type=='draft'):
                                total_delivery_metal += float(stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0)
                                total_return_metal += float(stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)                    
                                if stock_move.product_id.hp_type=='finish_product':
                                    finised_weight = float(stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)
                            ex_index+=1
                        else:
                            arr_sm = arr_product[index]
                            arr_sm['%s'%stock_move.product_id.id]['qty_delivery'] = arr_sm['%s'%stock_move.product_id.id]['qty_delivery'] + (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.product_qty or 0)
                            arr_sm['%s'%stock_move.product_id.id]['weight_delivery'] = arr_sm['%s'%stock_move.product_id.id]['weight_delivery'] + (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0)
                            arr_sm['%s'%stock_move.product_id.id]['qty_return'] = arr_sm['%s'%stock_move.product_id.id]['qty_return'] + (stock_move.picking_id.hp_transfer_type =='return' and stock_move.product_qty or 0)
                            arr_sm['%s'%stock_move.product_id.id]['weight_return'] = arr_sm['%s'%stock_move.product_id.id]['weight_return'] + (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)
                            arr_sm['%s'%stock_move.product_id.id]['qty_lost']  = arr_sm['%s'%stock_move.product_id.id]['qty_lost'] + (stock_move.picking_id.hp_transfer_type =='lost' and stock_move.product_qty or 0)
                            arr_sm['%s'%stock_move.product_id.id]['weight_lost'] = arr_sm['%s'%stock_move.product_id.id]['weight_lost'] + (stock_move.picking_id.hp_transfer_type =='lost' and stock_move.weight_mo or 0)
                            arr_sm['%s'%stock_move.product_id.id]['carat_real'] = arr_sm['%s'%stock_move.product_id.id]['carat_real'] + (stock_move.product_id.hp_type == 'metal' and ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))  or 0)
                            arr_sm['%s'%stock_move.product_id.id]['gram_real'] = arr_sm['%s'%stock_move.product_id.id]['gram_real'] + (stock_move.product_id.hp_type == 'diamonds' and (((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)) / 5) or ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)))
                            if(stock_move.product_id.hp_type=='diamonds'):
                                total_delivery_diamond+= (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0)
                                total_qty_diamond_delivery+= (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.product_qty or 0)                             
                                total_return_diamond += (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)                       
                                total_qty_diamond_return += (stock_move.picking_id.hp_transfer_type =='return' and stock_move.product_qty or 0)
                           
                            elif (stock_move.product_id.hp_type=='metal') or (stock_move.product_id.hp_type=='finish_product') or (stock_move.product_id.hp_type=='draft'): 
                                total_return_metal += (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0)    
                                total_delivery_metal += (stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0)
                                           
                        for product in arr_product:
                            product_id = None
                            for pid in product:
                                product_id = pid
                                break
                                         
                            arr.append({
                                'stt': '',
                                'so_name': '',
                                'so_id':'',
                                'style': '',
                                'type': '',
                                'employee': '',
                                'wc': '',
                                'wo_time': '',
                                'product_name': product[product_id]['product_name'],
                                'hp_type': product[product_id]['hp_type'],
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
                                             
            loss_rate=0
            if total_delivery_metal !=0.0:
                loss_rate =  round(float(total_delivery_metal - (total_return_metal-((total_delivery_diamond-total_return_diamond)/5)))/total_delivery_metal *100,2) 
            loss_weight = float(total_delivery_metal - (total_return_metal-((total_delivery_diamond-total_return_diamond)/5))) 
            total_return_metal = total_return_metal- (total_delivery_diamond-total_return_diamond)/5 -finised_weight
            metal_used = total_delivery_metal - total_return_metal
            net_weight = finised_weight - (total_delivery_diamond-total_return_diamond)/5
            
            
            res = self.write(cr, uid, ids, {'metal_delivery':total_delivery_metal 
                                            ,'metal_return':total_return_metal
                                            ,'diamond_weight':round( total_delivery_diamond/5,2)
                                            ,'loss_weight':loss_weight
                                            ,'finished_weight':finised_weight
                                            ,'loss_percent':loss_rate
                                            ,'metal_used': metal_used
                                            ,'metal_in_product':net_weight
                                            ,'diamond_used':total_qty_diamond_delivery-total_qty_diamond_return }
                             , context=context)
   
        return arr
    
    
    _columns = {
            'wo_id': fields.function(_get_mo, type='many2one', relation="mrp.workcenter", string='Workcenter', multi='mo',store=True),
            'work_state': fields.function(_get_mo, type='char', string="Work Order State", multi='mo',store=True),
            'employee_id': fields.many2one('hr.employee','Worker'),
            'metal_delivery': fields.float('Total Metal Delivery'),
            'metal_return': fields.float('Total Metal Return'),
            'metal_used': fields.float('Metal Used Weight'),
            'metal_in_product': fields.float('Net Weight'),
            'finished_weight': fields.float('Finished Weight'),
            'diamond_used': fields.float('Quantity Diamonds ' ),
            'diamond_weight': fields.float('Diamond Weight'),
            'loss_weight': fields.float('Loss Weight'),
            'loss_percent': fields.float('Loss Percent'),
            'mo_date': fields.date('Manufacturing Date'),     
                    
                    } 
    #Do not touch _name it must be same as _inherit
    #_name = 'mrp.production' 
mrp_production()
