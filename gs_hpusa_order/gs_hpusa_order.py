# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://generalsolutions.vn>). All Rights Reserved
#
##############################################################################
from datetime import datetime, date
from lxml import etree
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.addons.base_status.base_stage import base_stage
from openerp.addons.resource.faces import task as Task


class gs_order_config_loaivang(osv.osv):
    _name = "gs.order.config.loaivang"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),       
    }

gs_order_config_loaivang()

class gs_order_config_hotgiua(osv.osv):
    _name = "gs.order.config.hotgiua"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),       
    }

gs_order_config_hotgiua()

class gs_order_config_size(osv.osv):
    _name = "gs.order.config.size"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),  
        'product_id': fields.many2one('product.product', 'Product'),     
    }

gs_order_config_size()

class gs_order_config_hottam(osv.osv):
    _name = "gs.order.config.hottam"    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),       
    }

gs_order_config_hottam()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
	
    _columns = {
        	'loaivang_id': fields.many2one('gs.order.config.loaivang', 'Loai vang', required=True, readonly=True, states={'draft': [('readonly', False)]}),
		'hotgiua_id': fields.many2one('gs.order.config.hotgiua', 'Hot giua', required=True, readonly=True, states={'draft': [('readonly', False)]}),
		'size_id': fields.many2one('gs.order.config.size', 'Size', required=True, readonly=True, states={'draft': [('readonly', False)]}),
		'hottam_id': fields.many2one('gs.order.config.hottam', 'Hot tam', required=True, readonly=True, states={'draft': [('readonly', False)]}),
    }
	
sale_order_line()

class sale_order(osv.osv):
    _inherit = 'sale.order'
	
    _columns = {

		'phive3D': fields.char('Phi ve 3D',readonly=True, states={'draft': [('readonly', False)]}, size=64),
		'philamsap': fields.char('Phi lam sap',readonly=True, states={'draft': [('readonly', False)]}, size=64),
		'phiduc': fields.char('Phi duc',readonly=True, states={'draft': [('readonly', False)]}, size=64),
		'philamnguoi': fields.char('Phi lam nguoi',readonly=True, states={'draft': [('readonly', False)]}, size=64),
		'phinhanhot': fields.char('Phi nhan hot',readonly=True, states={'draft': [('readonly', False)]}, size=64),
		'phidanhbongxima': fields.char('Phi danh bong xi-ma',readonly=True, states={'draft': [('readonly', False)]}, size=64),
		'trongluongsanpham': fields.char('Trong luong san pham',readonly=True, states={'draft': [('readonly', False)]}, size=64),            
              'client_order_ref': fields.char('Customer Reference',readonly=True, states={'draft': [('readonly', False)]}, size=64),
              'note': fields.text('Terms and conditions', readonly=True, states={'draft': [('readonly', False)]},), 
	
	}

    def action_order_in_process(self, cr, uid, ids, context=None): 
        self.write(cr, uid, ids, {'state': 'order_in_process'})
        return True   
	
sale_order()




