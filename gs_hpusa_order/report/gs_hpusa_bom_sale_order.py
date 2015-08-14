# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from openerp.report import report_sxw

class gs_bom_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(gs_bom_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_bom': self.get_bom,
        })
    def get_bom(self, object_order):
        res = {}
        pricelist_obj = self.pool.get('product.pricelist')
        bom_obj = self.pool.get('mrp.bom')
        product_uom = self.pool.get('product.uom')

        # hpusa confgure 28-05-2015
        currency_obj = self.pool.get('res.currency')
        pricelist_version = self.pool.get('product.pricelist.version')
        # hpusa confgure 28-05-2015

        result = []
        product_parent = self.pool.get('product.product').browse(self.cr, self.uid, object_order.product_id.id, context=None)
        bom_id = bom_obj._bom_find(self.cr, self.uid, product_parent.id, product_parent.uom_id and product_parent.uom_id.id, [])
        for bom in bom_obj.browse(self.cr, self.uid, [bom_id]):

            # hpusa confgure 29-05-2015
            von=0
            for bom_line in bom.bom_lines:
                pricelist = object_order.order_id.pricelist_id
                cost_p = product_uom._compute_price(self.cr, self.uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                        #cost_price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                cost_price = currency_obj.compute(self.cr, self.uid,
                                    3, pricelist.currency_id.id,
                                    cost_p, round=False,
                                    context=None)
                von +=cost_price *bom_line.product_qty
	    print 'Gia von:' + str(von)
            plist_versions= self.get_price_list_version(self.cr,self.uid,self.ids,pricelist.id,von)
            print 'Pricelist version:' + str(plist_versions)

            # hpusa confgure 29-05-2015

            for bom_line in bom.bom_lines:
                pricelist = object_order.order_id.pricelist_id

                # hpusa configures 27-05-2015
                price_supplier = pricelist_version.hpusa_price_get(self.cr,self.uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0,plist_versions, partner=None,context=None)
                # hpusa configures 27-05-2015

                #gs
                #price_supplier = pricelist_obj.price_get(self.cr,self.uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0, partner=None,context=None)
                price = product_uom._compute_price(self.cr, self.uid, bom_line.product_id.uom_id.id, price_supplier[pricelist.id], to_uom_id=bom_line.product_uom.id)
                uom_ids = product_uom.search(self.cr, self.uid, [('uom_type','=','reference'),('category_id','=',bom_line.product_uom.category_id.id)])
                if uom_ids:
                    uom = product_uom.browse(self.cr, self.uid, uom_ids[0])
                res = {
                    'name' : bom_line.product_id.name,
                    'description' : bom_line.product_id.name,
                    'weight' : bom_line.product_uom.uom_type == 'reference' and bom_line.product_qty or (bom_line.product_uom.uom_type == 'bigger' and bom_line.product_qty/bom_line.product_uom.factor or bom_line.product_qty*bom_line.product_uom.factor) ,
                    'qty' : bom_line.product_qty,
                    'price' : price,
                    'uom' : uom.name or '',
                }
                result.append(res)
        return result
    # hpusa configures 29-05-2015
    def get_price_list_version(self,cr,uid,ids,price_list,amount,context=None):
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
        # hpusa configures 29-05-2015

report_sxw.report_sxw('report.gs.bom.sale.order', 'sale.order', 'addons/gs_hpusa_order/report/gs_hpusa_bom_sale_order.rml', parser=gs_bom_order, header="external")

class gs_bom_order_cost(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(gs_bom_order_cost, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_bom': self.get_bom,
        })
    def get_bom(self, object_order):
        res = {}
        pricelist_obj = self.pool.get('product.pricelist')
        bom_obj = self.pool.get('mrp.bom')
        product_uom = self.pool.get('product.uom')

        # hpusa confgure 29-05-2015
        
        currency_obj = self.pool.get('res.currency')
        pricelist_version = self.pool.get('product.pricelist.version')
        # hpusa confgure 29-05-2015

        result = []
        product_parent = self.pool.get('product.product').browse(self.cr, self.uid, object_order.product_id.id, context=None)
        bom_id = bom_obj._bom_find(self.cr, self.uid, product_parent.id, product_parent.uom_id and product_parent.uom_id.id, [])
        for bom in bom_obj.browse(self.cr, self.uid, [bom_id]):

            # hpusa confgure 29-05-2015
            von=0
            for bom_line in bom.bom_lines:
                pricelist = object_order.order_id.pricelist_id
                cost_p = product_uom._compute_price(self.cr, self.uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                        #cost_price = product_uom._compute_price(cr, uid, bom_line.product_id.uom_id.id, price_supplier[pricelist], to_uom_id=bom_line.product_uom.id)
                cost_price = currency_obj.compute(self.cr, self.uid,
                                    3, pricelist.currency_id.id,
                                    cost_p, round=False,
                                    context=None)
                von +=cost_price *bom_line.product_qty
            plist_versions= self.get_price_list_version(self.cr,self.uid,self.ids,pricelist.id,von)
            # hpusa confgure 29-05-2015


            for bom_line in bom.bom_lines:
                pricelist = object_order.order_id.pricelist_id
                # hpusa confgure 29-05-2015
                price_supplier = pricelist_version.hpusa_price_get(self.cr,self.uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0,plist_versions, partner=None,context=None)
                # hpusa confgure 29-05-2015

                #gs
                #price_supplier = pricelist_obj.price_get(self.cr,self.uid,[pricelist.id],bom_line.product_id.id, bom_line.product_qty or 1.0, partner=None,context=None)
                price = product_uom._compute_price(self.cr, self.uid, bom_line.product_id.uom_id.id, price_supplier[pricelist.id], to_uom_id=bom_line.product_uom.id)
                uom_ids = product_uom.search(self.cr, self.uid, [('uom_type','=','reference'),('category_id','=',bom_line.product_uom.category_id.id)])
                if uom_ids:
                    uom = product_uom.browse(self.cr, self.uid, uom_ids[0])
                currency_obj = self.pool.get('res.currency')
                cost_p = product_uom._compute_price(self.cr, self.uid, bom_line.product_id.uom_id.id, bom_line.product_id.lst_price, to_uom_id=bom_line.product_uom.id)
                cost_price = currency_obj.compute(self.cr, self.uid,
                                3, pricelist.currency_id.id,
                                cost_p, round=False,
                                context=None)

                res = {
                    'name' : bom_line.product_id.name,
                    'description' : bom_line.product_id.name,
                    'weight' : bom_line.product_uom.uom_type == 'reference' and bom_line.product_qty or (bom_line.product_uom.uom_type == 'bigger' and bom_line.product_qty/bom_line.product_uom.factor or bom_line.product_qty*bom_line.product_uom.factor) ,
                    'qty' : bom_line.product_qty,
                    'price' : price,
                    'cost_price': cost_price,
                    'uom' : uom.name or '',
                }
                result.append(res)
        return result

    # hpusa configures 29-05-2015
    def get_price_list_version(self,cr,uid,ids,price_list,amount,context=None):
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
    # hpusa configures 29-05-2015
report_sxw.report_sxw('report.gs.bom.sale.order.cost', 'sale.order', 'addons/gs_hpusa_order/report/gs_hpusa_bom_sale_order.rml', parser=gs_bom_order_cost, header="external")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

