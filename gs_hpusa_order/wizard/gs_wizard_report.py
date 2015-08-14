# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://gscom.vn>). All Rights Reserved
#
##############################################################################
from dateutil import relativedelta
import time
from datetime import datetime
from datetime import timedelta
from openerp.osv import fields, osv
import locale
locale.setlocale(locale.LC_ALL,"")
import sys;
reload(sys);
sys.setdefaultencoding("utf8")

class gs_wizard_report(osv.osv_memory):
    _name = 'gs.wizard.report'

    def _get_context(self, cr, uid, context=None):
        sale_order = self.pool.get('sale.order').browse(cr, uid, context.get('active_ids'), context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        object = sale_order[0]
        str_line = ''
        str_bom = []
        unit = []
        total = []
        sub = []
        flag = False
        for line in object.order_line:
            if line.product_uom_qty >= 2:
                flag = True
                continue
        #quantity >= 2
        def get_bom_2(product_id,pricelist_id,quantity, quantity_product):
            res = {}
            pricelist_obj = self.pool.get('product.pricelist')
            bom_obj = self.pool.get('mrp.bom')
            product_uom = self.pool.get('product.uom')

            # hpusa added 28-05-2015
            von=0
            pricelist_version = self.pool.get('product.pricelist.version')
            # hpusa added 28-05-2015

            result = []
            currency_obj = self.pool.get('res.currency')
            product_parent = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
            bom_id = bom_obj._bom_find(cr, uid, product_parent.id, product_parent.uom_id and product_parent.uom_id.id, [])

            # hpusa added 28-05-2015
            for bom in bom_obj.browse(cr, uid, [bom_id]):
                for bom_line in bom.bom_lines:
                    pricelist = pricelist_id.id
                    cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                    cost_price = currency_obj.compute(cr, uid,
                            3, pricelist.currency_id.id,
                            cost_p, round=False,
                            context=context)
                    von +=cost_price *bom_line.product_qty
            plist_versions= self.get_price_list_version(cr,uid,pricelist,von)
            # hpusa added 28-05-2015

            for bom in bom_obj.browse(cr, uid, [bom_id]):
                for bom_line in bom.bom_lines:
                    pricelist = pricelist_id.id

                    print  pricelist
                    # hpusa added 28-05-2015
                    price_supplier = pricelist_version.hpusa_price_get(cr,uid,[pricelist_id.id],bom_line.product_id.id, bom_line.product_qty or 1.0,plist_versions, partner=None,context=None)
                    # hpusa added 28-05-2015

                    #gs
                    #price_supplier = pricelist_obj.price_get(cr,uid,[pricelist],bom_line.product_id.id, bom_line.product_qty or 1.0, partner=None,context=None)

                    cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                    #cost_price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                    cost_price = currency_obj.compute(cr, uid,
                                3, pricelist_id.currency_id.id,
                                cost_p, round=False,
                                context=context)
                    price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                    uom_ids = product_uom.search(cr, uid, [('uom_type','=','reference'),('category_id','=',bom_line.product_uom.category_id.id)])
                    if uom_ids:
                        uom = product_uom.browse(cr, uid, uom_ids[0])
                    #ind = ind + 1
                    quantity_bom = quantity * bom_line.product_qty
                    if len(unit) == 0:
                        unit.append(cost_price)
                    else:
                        unit[0] = unit[0] + cost_price
                    if len(total) == 0:
                        total.append((quantity_bom/quantity_product)*cost_price)
                    else:
                        total[0] = total[0] + (quantity_bom/quantity_product)*cost_price
                    if len(sub) == 0:
                        sub.append((quantity_bom)*cost_price)
                    else:
                        sub[0] = sub[0] + (quantity_bom)*cost_price
                    total_1 = 0
                    sub_1 = 0
                    if cost_price > 0:
                        total_1 = (((quantity_bom/quantity_product)*price - (quantity_bom/quantity_product)*cost_price)/((quantity_bom/quantity_product)*cost_price))*100
                        sub_1 = ((quantity_bom*price - quantity_bom*cost_price)/(quantity_bom*cost_price))*100

                    str_bom.append('<tr align="left" width="100%">'\
                  '<td width="150px" style=" background-color: rgb(245, 245, 245) ; vertical-align:top; margin-top:5px;"><li>'+str(bom_line.product_id.name)+'</li></td>'\
                  '<td width="150px" style="background-color: rgb(245, 245, 245) ; vertical-align:top">'+str(bom_line.product_id.name)+'</td>'\
                  '<td width="90px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(bom_line.product_uom.uom_type == 'reference' and bom_line.product_qty or (bom_line.product_uom.uom_type == 'bigger' and bom_line.product_qty/bom_line.product_uom.factor or bom_line.product_qty*bom_line.product_uom.factor))+' '+ str(uom.name or '')+'</div></td>'\
                  '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',quantity_bom/quantity_product,True))+'</div></td>'\
                  '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',quantity_bom,True))+'</div></td>'\
                  '<td width="90px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>0.00%</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',price,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',(quantity_bom/quantity_product)*price,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',(quantity_bom)*price,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                  '</tr>')
        #quantity < 2
        def get_bom_1(product_id,pricelist_id,quantity, quantity_product):
            res = {}
            pricelist_obj = self.pool.get('product.pricelist')
            bom_obj = self.pool.get('mrp.bom')
            product_uom = self.pool.get('product.uom')
            result = []
            currency_obj = self.pool.get('res.currency')
            product_parent = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
            bom_id = bom_obj._bom_find(cr, uid, product_parent.id, product_parent.uom_id and product_parent.uom_id.id, [])
            # hpusa added 28-05-2015
            von=0
            pricelist_version = self.pool.get('product.pricelist.version')
            # hpusa added 28-05-2015

 	    # hpusa added 28-05-2015
            for bom in bom_obj.browse(cr, uid, [bom_id]):
                for bom_line in bom.bom_lines:
                    pricelist = pricelist_id.id
                    cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                    cost_price = currency_obj.compute(cr, uid,
                            3, pricelist_id.currency_id.id,
                            cost_p, round=False,
                            context=context)
                    von +=cost_price *bom_line.product_qty
            plist_versions= self.get_price_list_version(cr,uid,pricelist,von)
            # hpusa added 28-05-2015
		

	    for bom in bom_obj.browse(cr, uid, [bom_id]):
                for bom_line in bom.bom_lines:
                    pricelist = pricelist_id.id
                    print  pricelist

		    # hpusa added 28-05-2015
                    price_supplier = pricelist_version.hpusa_price_get(cr,uid,[pricelist_id.id],bom_line.product_id.id, bom_line.product_qty or 1.0,plist_versions, partner=None,context=None)
                    # hpusa added 28-05-2015
		    
                    #gs
                    #price_supplier = pricelist_obj.price_get(cr,uid,[pricelist],bom_line.product_id.id, bom_line.product_qty or 1.0, partner=None,context=None)

                    cost_p = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                    #cost_price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                    cost_price = currency_obj.compute(cr, uid,
                                3, pricelist_id.currency_id.id,
                                cost_p, round=False,
                                context=context)
                    price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                    uom_ids = product_uom.search(cr, uid, [('uom_type','=','reference'),('category_id','=',bom_line.product_uom.category_id.id)])
                    if uom_ids:
                        uom = product_uom.browse(cr, uid, uom_ids[0])
                    #ind = ind + 1
                    quantity_bom = quantity * bom_line.product_qty
                    if len(unit) == 0:
                        unit.append(cost_price)
                    else:
                        unit[0] = unit[0] + cost_price
                    if len(total) == 0:
                        total.append((quantity_bom/quantity_product)*cost_price)
                    else:
                        total[0] = total[0] + (quantity_bom/quantity_product)*cost_price
                    if len(sub) == 0:
                        sub.append((quantity_bom)*cost_price)
                    else:
                        sub[0] = sub[0] + (quantity_bom)*cost_price
                    total_1 = 0
                    sub_1 = 0
                    if cost_price > 0:
                        total_1 = (((quantity_bom/quantity_product)*price - (quantity_bom/quantity_product)*cost_price)/((quantity_bom/quantity_product)*cost_price))*100
                        sub_1 = ((quantity_bom*price - quantity_bom*cost_price)/(quantity_bom*cost_price))*100

                    str_bom.append('<tr align="left" width="100%">'\
                  '<td width="150px" style=" background-color: rgb(245, 245, 245) ; vertical-align:top; margin-top:5px;"><li>'+str(bom_line.product_id.name)+'</li></td>'\
                  '<td width="150px" style="background-color: rgb(245, 245, 245) ; vertical-align:top">'+str(bom_line.product_id.name)+'</td>'\
                  '<td width="90px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(bom_line.product_uom.uom_type == 'reference' and bom_line.product_qty or (bom_line.product_uom.uom_type == 'bigger' and bom_line.product_qty/bom_line.product_uom.factor or bom_line.product_qty*bom_line.product_uom.factor))+' '+ str(uom.name or '')+'</div></td>'\
                  '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',quantity_bom/quantity_product,True))+'</div></td>'\
                  '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',quantity_bom,True))+'</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',price,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+object.pricelist_id.currency_id.name+'</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>0.00%</div></td>'\
                  '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',(quantity_bom)*price,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                  '</tr>')

                    #get_bom(bom_line.product_id.id,pricelist_id,quantity,quantity_product)
        if flag == True:
            for line in object.order_line:
                if line.check_ == True:
                    str_bom = []
                    get_bom_2(line.product_id.id,line.order_id.pricelist_id, line.product_uom_qty, line.product_uom_qty)
                    total_1 = 0
                    sub_1 = 0
                    if len(total) > 0 and  total[0] > 0:
                        total_1 = ((line.price_unit - total[0])/total[0])*100
                        sub_1= ((line.price_unit * line.product_uom_qty - sub[0])/sub[0])*100
                    str_line += '<tr align="left" style="vertical-align:top;" width="100%" height="36px">'\
                      '<td style=" vertical-align:top;" rowspan="'+str(len(str_bom)+1)+'"><div><img width="150px" height="150px" src="data::image/png;base64,'+str(line.product_id.image_medium)+'"</div><br></td>'\
                      '<td width="150px" style=" background-color: rgb(245, 245, 245) ; vertical-align:top; margin-top:5px;">'+str(line.product_id.name)+'</td>'\
                      '<td width="150px" style="background-color: rgb(245, 245, 245) ; vertical-align:top">'+str(line.product_id.name)+'</td>'\
                      '<td width="90px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>0.00</div></td>'\
                      '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>1.00</div></td>'\
                      '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.product_uos and line.product_uos_qty or line.product_uom_qty,True))+'</div></td>'\
                      '<td width="90px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.discount,True))+ '%'+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.price_unit,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.price_unit,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.price_unit * line.product_uom_qty,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                      '</tr>'
                    unit[0] = 0
                    total[0] = 0
                    sub[0] = 0
                    for item in str_bom:
                        str_line += item
                    str_line += '<tr align="left" style="vertical-align:top;" width="100%" height="10px">'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '</tr>'

            return '<table id="view_bom" width="1000px">'\
                        '<tr align="left" width="1300px" height="36px" style="background-color: rgb(238, 76, 140) ;">'\
                        '<th width="150px" rowspan="2"><div align = center><font color= white>&nbsp;&nbsp;Image</font></th>'\
                        '<th width="150px" rowspan="2"><div align = center><font color= white>Product ID</font></th>'\
                        '<th width="150px" rowspan="2"><div align = center><font color= white>Description</font></th>'\
                        '<th width="90px" rowspan="2"><div align = center><font color= white>Wt.</font></div></th>'\
                        '<th width="120px" colspan="2"><div align = center><font color= white>Quantity</font></div></th>'\
                      '<th width="90px" rowspan="2"><div align = center><font color= white>Discount</font></div></th>'\
                      '<th width="325px" colspan="3"><div align = center><font color= white>Total</font></div></th>'\
               '</tr>'\
               '<tr align="left" width="100%" height="36px" style="background-color: rgb(238, 76, 140) ;">'\
                  '<th width="60px"><div align = center><font color= white>Unit</font></div></th>'\
                  '<th width="60px"><div align = center><font color= white>Total</font></div></th>'\
                  '<th width="108px"><div align = center><font color= white>Unit</font></div></th>'\
                  '<th width="108px"><div align = center><font color= white>Total</font></div></th>'\
                  '<th width="108px"><div align = center><font color= white>Sub Total</font></div></th>'\
               '</tr>'\
               +str_line+''\
               '</table></div>'
        else:
            for line in object.order_line:
                if line.check_ == True:
                    str_bom = []
                    get_bom_1(line.product_id.id,line.order_id.pricelist_id, line.product_uom_qty, line.product_uom_qty)
                    total_1 = 0
                    sub_1 = 0
                    if len(total) > 0 and  total[0] > 0:
                        total_1 = ((line.price_unit - total[0])/total[0])*100
                        sub_1= ((line.price_unit * line.product_uom_qty - sub[0])/sub[0])*100
                    str_line += '<tr align="left" style="vertical-align:top;" width="100%" height="36px">'\
                      '<td style=" vertical-align:top;" rowspan="'+str(len(str_bom)+1)+'"><div><img width="150px" height="150px" src="data::image/png;base64,'+str(line.product_id.image_medium)+'"</div><br></td>'\
                      '<td width="150px" style=" background-color: rgb(245, 245, 245) ; vertical-align:top; margin-top:5px;">'+str(line.product_id.name)+'</td>'\
                      '<td width="150px" style="background-color: rgb(245, 245, 245) ; vertical-align:top">'+str(line.product_id.name)+'</td>'\
                      '<td width="90px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>0.00</div></td>'\
                      '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>1.00</div></td>'\
                      '<td width="60px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.product_uos and line.product_uos_qty or line.product_uom_qty,True))+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.price_unit,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+object.pricelist_id.currency_id.name+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.discount,True))+ '%'+'</div></td>'\
                      '<td width="108px" style="background-color: rgb(245, 245, 245) ; vertical-align:top"><div align = right>'+str(locale.format('%0.2f',line.price_unit * line.product_uom_qty,True))+object.pricelist_id.currency_id.symbol+'</div></td>'\
                      '</tr>'
                    unit[0] = 0
                    total[0] = 0
                    sub[0] = 0
                    for item in str_bom:
                        str_line += item
                    str_line += '<tr align="left" style="vertical-align:top;" width="100%" height="10px">'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '<td></td>'\
                      '</tr>'

            return '<table id="view_bom" width="1000px">'\
                        '<tr align="left" width="1300px" height="36px" style="background-color: rgb(238, 76, 140) ;">'\
                        '<th width="150px" rowspan="2"><div align = center><font color= white>&nbsp;&nbsp;Image</font></th>'\
                        '<th width="150px" rowspan="2"><div align = center><font color= white>Product ID</font></th>'\
                        '<th width="150px" rowspan="2"><div align = center><font color= white>Description</font></th>'\
                        '<th width="90px" rowspan="2"><div align = center><font color= white>Wt.</font></div></th>'\
                        '<th width="60px" rowspan="2"><div align = center><font color= white>Unit</font></div></th>'\
                        '<th width="60px" rowspan="2"><div align = center><font color= white>Total</font></div></th>'\
                        '<th width="415px" colspan="4"><div align = center><font color= white>Amount</font></div></th>'\
               '</tr>'\
               '<tr align="left" width="100%" height="36px" style="background-color: rgb(238, 76, 140) ;">'\
                  '<th width="108px"><div align = center><font color= white>Unit</font></div></th>'\
                  '<th width="108px"><div align = center><font color= white>Currency</font></div></th>'\
                  '<th width="108px"><div align = center><font color= white>Discount</font></div></th>'\
                  '<th width="108px"><div align = center><font color= white>Total</font></div></th>'\
               '</tr>'\
               +str_line+''\
               '</table></div>'

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
    # hpusa configures 27-05-2015

    _columns = {
                'context': fields.html('Contents', help='Automatically sanitized HTML contents'),
          }
    _defaults = {
         'context': _get_context,

    }
gs_wizard_report()




