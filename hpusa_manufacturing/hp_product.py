import tools
from osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'is_component': fields.boolean('Component'),
        'hp_type': fields.selection([
                                     ('finish_product', 'Finish Product'),
                                     ('metal', 'Metal'),
                                      ('diamonds', 'Diamonds'),
                                      ('accessories', 'Accessories'),
                                      ('draft', 'Draft'),
                                     ],'Type'),  
        'setting_price': fields.float('Setting Price'),
        'hp_style': fields.char('HP Style'),
        'metal_type': fields.char('Metal Type'),
        'coeff_24k': fields.float('Unit of Measure -> 24K'),
        
    }
    def onchang_category(self, cr, uid, ids, category, context=None):
        if category:
            name_cate = self.pool.get('product.category').browse(cr, uid, category).name
            if name_cate == 'Components':
                return {'value': {'sale_ok': False, 'purchase_ok': False, 'is_component': True}}
        return {'value': {'sale_ok': True, 'purchase_ok': True, 'is_component': False}}
    
    def create(self, cr, uid, vals, context=None):
        if 'categ_id' in vals:
            if vals['categ_id']:
                name_cate = self.pool.get('product.category').browse(cr, uid, vals['categ_id']).name
                if name_cate == 'Components':
                    vals['sale_ok'] = False
                    vals['purchase_ok'] = False
        return super(product_product, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'categ_id' in vals:
            if vals['categ_id']:
                print vals['categ_id']
                name_cate = self.pool.get('product.category').browse(cr, uid, vals['categ_id']).name
                if name_cate == 'Components':
                    vals['sale_ok'] = False
                    vals['purchase_ok'] = False
        return super(product_product, self).write(cr, uid, ids, vals, context)
product_product()