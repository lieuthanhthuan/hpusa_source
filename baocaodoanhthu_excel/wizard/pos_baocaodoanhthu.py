# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2004-2012 OpenERP S.A. <http://openerp.com>
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

import base64
import cStringIO
import xlwt
from openerp import tools
from openerp.osv import fields,osv
from openerp.tools.translate import _
from openerp.tools.misc import get_iso_codes



class Pos_baocaodoanhthu(osv.osv_memory):
    _name = "pos_baocaodoanhthu"

    _columns = {
            'start_date': fields.date(u'Ngay Bat Dau'),
            'end_date': fields.date(u'Ngay ket Thuc'),

            'name': fields.char('File Name', readonly=True),

            'data': fields.binary('File', readonly=True),
            'state': fields.selection([('choose', 'choose'),   # choose language
                                       ('get', 'get')])        # get the file
    }
    _defaults = {
        'state': 'choose',
        'name': 'baocao.xls',
    }

    def act_getfile(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]

        style_header = xlwt.easyxf('font: bold on,italic on;pattern: pattern solid, fore-colour grey25;')
        style_pattern=xlwt.easyxf('font: bold on;pattern: pattern solid, fore-colour yellow;')
        style_date = xlwt.easyxf(num_format_str='DD.MM.YYYY')
        style_cur = xlwt.easyxf(num_format_str="[$SFr.]" + " 0.00")

        wb = xlwt.Workbook(encoding = 'utf-8')
        ws = wb.add_sheet(u'Luong')
        ws.write(0,0,u'Danh sach cac thanh vien', style_pattern)

        row=2
        ws.write(row,0,u'Mã Nhân viên', style_header)
        ws.write(row,1,u' Mã vân tay', style_header)
        ws.write(row,2,u' Số hợp đồng', style_header)
        ws.write(row,3,u' Tên', style_header)
        ws.write(row,4,u'Giới tính', style_header)
        ws.write(row,5,u' Bộ Phận', style_header)
        ws.write(row,6,u'Chức vụ', style_header)
        ws.write(row,7,u'Chức danh', style_header)
        ws.write(row,8,u' Tổng thu nhập    ', style_header)
        ws.write(row,9,u'Lương chính', style_header)
        ws.write(row,10,u'Lương cơ bản tham gia BHXH', style_header)
        ws.write(row,11,u'Phụ cấp vị trí', style_header)
        ws.write(row,12,u'Lương KPB', style_header)
        ws.write(row,13,u'Số ngày công làm việc thực tế trong tháng', style_header)
        ws.write(row,14,u'Ngày Thường', style_header)
        ws.write(row,15,u'Ngày chủ nhật', style_header)
        ws.write(row,16,u'Lễ, tết', style_header)
        ws.write(row,17,u'Lương chính', style_header)
        ws.write(row,18,u'Lương KPB', style_header)
        ws.write(row,19,u'Lương trách nhiệm', style_header)
        ws.write(row,20,u'Hoàn trản 1/3 đã giữ', style_header)
        ws.write(row,21,u'Thưởng doanh số', style_header)
        ws.write(row,22,u'Khác', style_header)
        ws.write(row,23,u'Giữ 1/3 lương chính', style_header)
        ws.write(row,24,'BHXH', style_header)
        ws.write(row,25,'BHYT', style_header)
        ws.write(row,26,'BHTN', style_header)
        ws.write(row,27,u'Bồi thường khóa học', style_header)
        ws.write(row,28,u'Trừ lương do không đủ KPB', style_header)
        ws.write(row,29,u'Trả tiền đồng phục', style_header)
        ws.write(row,30,u'Thu hồi tiền đào tạo', style_header)
        ws.write(row,31,u'Giảm trừ gia cảnh', style_header)
        ws.write(row,32,u'Tổng thu nhập', style_header)
        ws.write(row,33,u'Thực nhận trong tháng', style_header)

        cr.execute('select count(*) from hr_contract')
        e=cr.fetchall()
        ws.write(1,0,u'So luong: %s '%(str(e[0][0])), style_pattern)
        cr.execute('select b.employee_id,a."x_employee_id" MVT'
                    +', b.id contractid'
                    +',a.name_related Ten_NhanVien'
                    +',a.gender gioitinh'
                    +',c.name BoPhan'
                    +',d.name'
                    +',a."x_job_name"'
                    +',b.wage+b."x_KPB" tongluong'
                    +',b.wage luongchinh'
                    +',b."x_Base_Social"'
                    +',b.wage -b."x_Base_Social" phucapvitri'
                    +',b."x_KPB" LuongKPB'
                    +' from hr_employee a'
                    +' , hr_contract b'
                    +' , hr_department c'
                    +' , hr_job d '
                    +' where a.id = +b.employee_id'
                    +' and c.id = a.department_id'
                    +' and a.job_id = d.id')

        t=cr.fetchall()
        bd=3
        sld=len(t)+bd


        for i in range(bd,sld):
            ws.write(i,0,(t[i-bd][0]))
            ws.write(i,1,(t[i-bd][1]).encode('utf8'))
            ws.write(i,2,(t[i-bd][2]))
            ws.write(i,3,(t[i-bd][3]).encode('utf8'))
            ws.write(i,4,(t[i-bd][4]).encode('utf8'))
            ws.write(i,5,(t[i-bd][5]).encode('utf8'))
            ws.write(i,6,(t[i-bd][6]).encode('utf8'))
            ws.write(i,7,(t[i-bd][7]).encode('utf8'))
            ws.write(i,8,(t[i-bd][8]))
            ws.write(i,9,(t[i-bd][9]))
            ws.write(i,10,(t[i-bd][10]))
            ws.write(i,11,(t[i-bd][11]))
            ws.write(i,12,(t[i-bd][12]))

            cr.execute('select  slip_id, name , amount '
            +' from hr_payslip_line '
            +' where slip_id =(select id from hr_payslip '
            +' where employee_id = ' +str(t[i-bd][0]) +u''
            +' and date_from >= to_date(\'2014-11-01\',\'yyyy-mm-dd\'))'
            +' and create_date > to_date(\'2014-11-01\',\'yyyy-mm-dd\')'
            +' order by name')
            x=cr.fetchall()

            min=3
            max=len(x)+min
            if(len(x)>0):

                    ws.write(i,13,(x[20][2]))
                    ws.write(i,14,(x[16][2]))
                    ws.write(i,15,(x[13][2]))
                    ws.write(i,16,(x[14][2]))
                    ws.write(i,17,(x[3][2]))
                    ws.write(i,18,(x[10][2]))
                    ws.write(i,19,(x[17][2]))
                    ws.write(i,20,(x[18][2]))
                    ws.write(i,21,(x[4][2]))
                    ws.write(i,22,(x[15][2]))
                    ws.write(i,23,(x[11][2]))
                    ws.write(i,24,(x[1][2]))
                    ws.write(i,25,(x[2][2]))
                    ws.write(i,26,(x[0][2]))
                    ws.write(i,27,(x[9][2]))
                    ws.write(i,28,(x[6][2]))
                    ws.write(i,29,(x[19][2]))
                    ws.write(i,30,(x[7][2]))
                    ws.write(i,31,(x[5][2]))
                    ws.write(i,32,(x[8][2]))
                    ws.write(i,33,(x[12][2]))



        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        f.close()
        self.write(cr, uid, ids, {'state': 'get',
                                  'data': out,
                                  'name':'Salary_report.xls'}, context=context)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pos_baocaodoanhthu',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    def manufacturing_v_invoice(self, cr, uid, date_form, date_to):
        pricelist_obj = self.pool.get('product.pricelist')
        product_uom = self.pool.get('product.uom')
        manufacturing = self.print_manufacturing_detail(cr, uid, date_form, date_to)
        for item in manufacturing:
            if item['product_id']:
                product_obj = self.pool.get('product.product').browse(cr, uid, item['product_id'])
                sale_price = 0
                setting_price = 0
                standard_price = 0
                uom = self.pool.get('product.uom').search(cr, uid, [('name','=',item['uom'])])
                if item['so_id']:
                    sale_order = self.pool.get('sale.order').browse(cr, uid, item['so_id'])
                    pricelist = sale_order.pricelist_id
                    if uom and pricelist:
                        price_supplier = pricelist_obj.price_get(cr,uid,[pricelist.id], item['product_id'], 1.0, partner=None,context=None)
                        sale_price = product_uom._compute_price(cr, uid, product_obj.uom_id.id, price_supplier[pricelist.id], to_uom_id=uom[0])
                else:
                    sale_price = product_obj.list_price
                setting_price = product_uom._compute_price(cr, uid, product_obj.uom_id.id, product_obj.setting_price, to_uom_id=uom[0])
                standard_price = product_uom._compute_price(cr, uid, product_obj.uom_id.id, product_obj.standard_price, to_uom_id=uom[0])
                item['price'] = str((product_obj.standard_price or 0.0) )
                item['setting_price'] = str(setting_price or 0.0)
                item['total_amount'] = str( float(item['price']) * (float(item['qty_real'] or 0.0)))
                item['cost_price'] = str(standard_price or 0.0)
                item['sale_price'] = str((float(sale_price or 0.0))*(float(item['qty_real'] or 0.0)))
                item['total_setting'] = str(((setting_price or 0.0) * float(item['qty_real'] or 0.0)) )
            else:
                item['price'] = ''
                item['setting_price'] = ''
                item['total_amount'] = ''
                item['cost_price'] = ''
                item['sale_price'] = ''
                item['total_setting'] = ''
        return manufacturing

    def print_manufacturing_detail(self, cr, uid, date_form, date_to):
        so_ids = self.pool.get('sale.order').search(cr, uid, [('date_order','<=',date_to),('date_order','>=',date_form)])
        arr = []
        last_finish_id=0
        last_id_wo =0
        stt = 1
        print so_ids
        if so_ids:
            for so in self.pool.get('sale.order').browse(cr, uid, so_ids):
                for item in so.order_line:
                    production_ids = self.pool.get('mrp.production').search(cr, uid, [('so_line_id','=',item.id)])
                    if production_ids:
                        arr.append({
                                    'stt': stt,
                                    'so_name': item.order_id.name + '-' + item.order_id.partner_id.name + '-' + item.order_id.create_date,
                                    'so_id': so.id,
                                    'style': item.product_id.hp_style and item.product_id.hp_style or '',
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

                        for mrp in self.pool.get('mrp.production').browse(cr, uid, production_ids):
                            total_amount = 0.0

                            for wo in mrp.workcenter_lines:
                                arr.append({
                                        'stt': '',
                                        'so_name': '',
                                        'so_id': wo.so_id.id,
                                        'style': '',
                                        'type': '',
                                        'employee': wo.employee_id and wo.employee_id.name or '',
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
                                        'qty_real': wo.qty,
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
                                                                                'standard_price': stock_move.product_uom.standard_price,
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
                                            arr_sm['%s'%stock_move.product_id.id]['carat_real'] = arr_sm['%s'%stock_move.product_id.id]['carat_real'] + (stock_move.product_id.hp_type == 'metal' and ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0))  or 0)
                                            arr_sm['%s'%stock_move.product_id.id]['gram_real'] = arr_sm['%s'%stock_move.product_id.id]['gram_real'] + (stock_move.product_id.hp_type == 'metal' and (((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)) / 5) or ((stock_move.picking_id.hp_transfer_type =='delivery' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type =='return' and stock_move.weight_mo or 0) - (stock_move.picking_id.hp_transfer_type == 'lost' and stock_move.weight_mo or 0)))
                                for product in arr_product:
                                    product_id = None
                                    for pid in product:
                                        product_id = pid
                                        break

                                    arr.append({
                                            'stt': '',
                                            'so_name': '',
                                            'so_id': wo.so_id.id,
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
