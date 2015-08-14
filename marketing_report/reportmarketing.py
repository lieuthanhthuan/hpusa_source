from openerp.osv import fields,osv
from openerp.tools.translate import _

class report_marketing(osv.osv):
    _name = 'report.marketing'
    _description = "Marketing Report"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'description': fields.text('Description', help='the description of Marketing Campaign'),
        'state': fields.selection([('draft','Draft'),('inprogress','Inprogress'),('done','Done'),('cancel','Canceled')],'State',readonly=True),
        'sequence': fields.integer('Sequence',size=30, help='the sequence of Marketing Caimpaign'),
        'date_start': fields.date('Start Date',size=30,required=True, help='the start date'),
        'date_stop': fields.date('End Date',size=30, help='the end date of program'),
        'company': fields.many2one('res.company','Company', help='Company will applied program'),
        'report_line':fields.one2many('report.marketing.stage','stage_master','Report Stage'),
    }
    _defaults = {
                  'state': 'draft',
                  }

    def action_new(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return res

    def action_start(self,cr,uid,ids,context=None):
        res = self.write(cr, uid, ids, {'state': 'inprogress'}, context=context)
        return res

    def action_end(self,cr,uid,ids,context=None):
        res = self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return res

report_marketing()

# create Report Marketing stage
class report_marketing_stage(osv.osv):
    _name='report.marketing.stage'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Marketing Report Stage"

    _columns={
        'stage_master':fields.many2one('report.marketing', 'Program stage'),
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'sale_off_percent': fields.float('Sale Off Percent'),
        'quantity_total': fields.float('Total Quantity', ),
        'quantity_website': fields.float('Quantity Website'),
        'quantity_sold': fields.float('Quantity Sold'),
        'description': fields.char('Description', help='the name'),
        'time_start': fields.datetime('Start Time'),
        'time_end': fields.datetime('End Time'),
        'line_master_id':fields.one2many('report.marketing.stage.line','line_master','Product'),
        'company_id': fields.related('stage_master', 'company', type="many2one", relation="res.company", string="Company", store=True),
              }
    def get_quantity_total(self,cr,uid,ids,contex=None):
        cr.execute('select sum(product_quantity) qty_website ' +
                   'from report_marketing_stage_line ' +
                   'where line_master = ' + str(ids[0]))
        t= cr.fetchall()

        if t[0][0]==None:
            return 0
        else:
            return t[0][0]
    def get_quantity_website(self,cr,uid,ids,contex=None):
        cr.execute('select sum(product_quantity) qty_website ' +
                   'from report_marketing_stage_line ' +
                   'where state like \'website\' ' +
                   'and line_master = ' + str(ids[0]))
        t= cr.fetchall()

        if t[0][0]==None:
            return 0
        else:
            return t[0][0]

    def get_quantity_sold(self,cr,uid,ids,contex=None):

        cr.execute('select sum(product_quantity) qty_website '
                    ' from report_marketing_stage_line '
                    ' where state like \'sold\' '
                    ' and line_master = '+ str(ids[0]))

        t= cr.fetchall()
        if t[0][0]==None:
            return 0
        else:
            return t[0][0]

    def action_update(self,cr,uid,ids,context=None ):

        marketing_stages = self.browse(cr,uid, ids,context)

        lines = self.pool.get('report.marketing.stage.line').search(cr, uid, [('line_master','=',ids)], context=context)
        for line in lines:
            report_line = self.pool.get('report.marketing.stage.line').browse(cr,uid,line,context=context)
            product_state= self.pool.get('website.product').browse(cr,uid,report_line.product_id.id,context=context).state
            sold_date = self.pool.get('website.product').browse(cr,uid,report_line.product_id.id,context=context).sold_date
            regular_price = self.pool.get('website.product').browse(cr,uid,report_line.product_id.id,context=context).regular_price
            sale_off_percent=0
            #update state of product marketing line
            for marketing_stage in marketing_stages:
                sale_off_price= round(regular_price-( marketing_stage.sale_off_percent * regular_price/100),4)
                sale_off_percent = marketing_stage.sale_off_percent
                break

            self._update_product_state(cr,uid,line,product_state)
            self._update_product_sold_date(cr,uid,line,sold_date)

            if sale_off_percent !=0:
                self._update_product_sale_off_percent(cr,uid,line,sale_off_percent)
                self._update_product_sale_off_price(cr,uid,line,sale_off_price)

        # Update program state information
        qty_total = self.get_quantity_total(cr,uid, ids)
        qty_website= self.get_quantity_website(cr,uid, ids)
        qty_sold= self.get_quantity_sold(cr,uid, ids)
        cr.execute('update report_marketing_stage '
                    'set quantity_sold = ' + str(qty_sold) +
                    ',quantity_website = ' + str(qty_website) +
                    ',quantity_total = ' + str(qty_total) +
                    ' where id = '+ str(ids[0]))

    def _update_product_state(self,cr,uid,ids,product_state,context=None ):
        res = self.pool.get('report.marketing.stage.line').write(cr, uid, ids, {'state': product_state}, context=context)
        return res

    def _update_product_sold_date(self,cr,uid,ids,sold_date,context=None):
        res = self.pool.get('report.marketing.stage.line').write(cr, uid, ids, {'sold_date': sold_date}, context=context)
        return res

    def _update_product_sale_off_price(self,cr,uid,ids,sale_off_price,context=None):
        res = self.pool.get('report.marketing.stage.line').write(cr, uid, ids, {'sale_off_price': sale_off_price}, context=context)
        return res

    def _update_product_sale_off_percent(self,cr,uid,ids,sale_off_price,context=None):
        res = self.pool.get('report.marketing.stage.line').write(cr, uid, ids, {'percent': sale_off_price}, context=context)
        return res

report_marketing_stage()

class report_marketing_stage_line(osv.osv):
    _name='report.marketing.stage.line'
    _description = "Marketing Report Line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={
        'line_master':fields.many2one('report.marketing.stage', 'Line'),
        'program_id': fields.related('line_master', 'stage_master', type="many2one", relation="report.marketing", string="Marketing Program", store=True),
        'product_id': fields.many2one('website.product','Product',size=30, domain=[('state', '=', 'website')], help='Product to sale off'),
        'style': fields.char('Style',size=30, help='Product Style'),
        'sku': fields.char('SKU' ,size=30),
        'sku_id': fields.char('SKU ID'),
        'product_type': fields.selection([('diamond','Diamond'),('jewelry','Jewelry')],'Product Type'),
        'diamon_certificate': fields.selection([('1','HPUSA'),('2','GIA')],'Certificate'),
        'product_category': fields.selection([('1','DRIMT'),
                                              ('2','DIARI'),
                                              ('3','DPDMT'),
                                              ('4','DIAPD'),
                                              ('5','DERMT'),
                                              ('6','DIAER'),
                                              ('7','DBGMT'),
                                              ('8','DIABG'),
                                              ('9','DIABL'),
                                              ('10','WEDDING BAND'),
                                              ('11','CZ') ,
                                              ('12','JADE') ,
                                              ('13','CARATER'),
                                              ('14','Non GIA'),
                                              ('15','GIA') ],'Product Categories'),
        'product_description': fields.text('Product description'),
        'regular_price': fields.float('Regular Price',required=True),
        'sale_off_price': fields.float('Sale off Price',required=True),
        'percent':fields.char('%'),
        'currency': fields.many2one('res.currency','Currency'),
        'state': fields.selection([('website','Website'),('sold','Sold')],'State',required=True),
        'sold_date': fields.date('Sold Date',size=30, help='the date sold product'),
        'product_quantity': fields.integer('Quantity', readonly =True),
        'remark': fields.char('Remark'),
        'company_id': fields.related('line_master', 'company_id', type="many2one", relation="res.company", string="Company", store=True),
              }

    _defaults = {
        'product_quantity': 1, # Report Line Default
             }

    def onchange_sale_off_price(self,cr, uid, ids, product_id, sale_off_price ,  context=None):
        context = context or {}

        product =self.pool.get('website.product').browse(cr, uid, product_id, context=context)
        percent = round((product.regular_price - sale_off_price)/product.regular_price,3)
        str_percent= str(percent*100)+'%'
        value={
            'percent': str_percent,
               }
        return {'value': value}

    def onchange_product_id(self, cr, uid, ids, product_id,stage_id ,  context=None):

        context = context or {}
        product =self.pool.get('website.product').browse(cr, uid, product_id, context=context)

        value={
            'style': product.style,
            'sku': product.sku,
            'sku_id': product.sku_id,
            'product_type': product.product_type,
            'product_category': product.product_category,
            'product_description': product.product_description,
            'regular_price': product.regular_price,
            'currency': product.currency.id,
            'state': product.state,
               }

        if (product.state =='sold'):
            raise osv.except_osv(_('Warning!'), _('You Plan to sell the Sold Product'))

        return {'value': value}

report_marketing_stage_line()

class website_product(osv.osv):
    _name = 'website.product'
    _description = "Website Product"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={
        'name': fields.char('Name',size=30, help='Name Of Product'),
        'style': fields.char('Style',size=30, help='Product Style'),
        'sku': fields.char('SKU' ,size=30),
        'sku_id': fields.char('SKU ID'),
        'product_type': fields.selection([('diamond','Diamond'),('jewelry','Jewelry')],'Product Type'),
        'diamon_certificate': fields.selection([('1','HPUSA'),('2','GIA')],'Certificate'),
        'product_category': fields.selection([('1','DRIMT'),
                                              ('2','DIARI'),
                                              ('3','DPDMT'),
                                              ('4','DIAPD'),
                                              ('5','DERMT'),
                                              ('6','DIAER'),
                                              ('7','DBGMT'),
                                              ('8','DIABG'),
                                              ('9','DIABL'),
                                              ('10','WEDDING BAND'),
                                              ('11','CZ') ,
                                              ('12','JADE') ,
                                              ('13','CARATER')], 'Product Categories'),
        'product_description': fields.text('Product description'),
        'regular_price': fields.float('Regular Price',required=True),
        'currency': fields.many2one('res.currency','Currency'),
        'state': fields.selection([('website','Website'),('sold','Sold')],'State',required=True),
        'sold_date': fields.date('Sold Date',size=30, help='the date sold product'),
        'customer': fields.many2one ('res.partner','Customer'),
        'remark': fields.char('Remark'),
              }
    _defaults = {
        'state': 'website',
             }
website_product()

# Create Marketing mothly report
# ------------ Year finalcial ----------------
class marketing_year_report(osv.osv):
    _name = 'marketing.year.report'
    _description = "Marketing Year Report"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'year_id': fields.char('Year'),
        'state': fields.selection([('open','Open'),('close','Closed'),('cancel','Canceled')],'State',readonly=True),
        'description': fields.text('Description',size=60, help='the description of Marketing Campaign'),
        'company': fields.many2one('res.company','Company', help='Company will applied program'),
        'period_report':fields.one2many('marketing.year.period','year_master','Month'),
    }
    _defaults = {
        'state': 'open',
             }
    def action_open(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state': 'open'}, context=context)
        return res

    def action_cancel(self,cr,uid,ids,context=None):
        res = self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return res

    def action_close(self,cr,uid,ids,context=None):
        res = self.write(cr, uid, ids, {'state': 'close'}, context=context)
        return res

marketing_year_report()


class marketing_program_management(osv.osv):
    _name ='marketing.program'

    _description = "Marketing Program"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={
        'year_id': fields.many2one('marketing.year.report','Year',help='Fiscal Year'),
        'company': fields.many2one('res.company','Company', help='Company will applied program'),
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'state': fields.selection([('draft','Draft'),('inprogress','Inprogress'),('done','Done'),('cancel','Canceled')],'State',readonly=True),
        'description': fields.text('Description',size=60, help='the description of Marketing Program'),
        'date_start': fields.date('Start Date',size=30, help='the start date'),
        'date_stop': fields.date('End Date',size=30, help='the end date of report'),

             }
    _defaults = {
        'state': 'draft',
             }
    def action_new(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return res

    def action_start(self,cr,uid,ids,context=None):
        res = self.write(cr, uid, ids, {'state': 'inprogress'}, context=context)
        return res

    def action_end(self,cr,uid,ids,context=None):
        res = self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return res

marketing_program_management()
#------------ Period Report -----------------
class marketing_year_report_period(osv.osv):
    _name='marketing.year.period'

    _description = "Marketing Year period"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={
        'year_master':fields.many2one('marketing.year.report', 'Year'),
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'start_date': fields.date('Start Date',size=30,required=True, help='the start date'),
        'end_date': fields.date('End Date',size=30, help='the end date of report'),
        'line_master_id':fields.one2many('marketing.year.period.line','line_master','Parameters'),
              }

marketing_year_report_period()

#------------ period report detail-----------
class report_marketing_period_line(osv.osv):
    _name='marketing.year.period.line'

    _description = "Marketing Year Period Line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns={

        'line_master':fields.many2one('marketing.year.period', 'Periods'),
        'fiscal_year': fields.related('line_master', 'year_master', type="many2one", relation="marketing.year.report", string="Year", store=True),
        'name': fields.many2one('monthly.report.type','Name',size=30,required=True, help='Type of parameter'),
        'value': fields.float('Value',size=30, help='value of paramter'),
        'parameter_type': fields.many2one('monthly.parameter.type','Type Report'),
        'parameter_categories': fields.many2one('parameter.categories','Categories'),
        'unit': fields.many2one('monthly.report.unit','Units', help='Unit of paramter'),
        'remark': fields.text('Remark'),
              }

report_marketing_period_line()

class monhtly_report_type(osv.osv):
    _name = "monthly.report.type"
    _description = "Monthly Report Type"
    _columns={
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'description': fields.text('Description', help='Description of Report Type'),
        'remark': fields.char('Remark'),
              }
monhtly_report_type()


class monhtly_unit_type(osv.osv):
    _name = "monthly.report.unit"
    _columns={
        'name': fields.char('Name',size=30,required=True, help='the name'),
        'description': fields.text('Description', help='Description of Report Type'),
        'remark': fields.text('Remark'),
              }
monhtly_unit_type()

class parameter_type(osv.osv):
    _name ="monthly.parameter.type"

    _description = "Monthly Parameter type"
    _columns={
        'name':fields.char('Name',required=True,help='The Name'),
        'description': fields.text('Description', help='Description of Report Type'),
        'remark': fields.text('Remark'),
              }

parameter_type()

class line_categories(osv.osv):
    _name ="parameter.categories"
    _description = "Parameter categories"
    _columns={
        'name':fields.char('Name',required=True,help='The Name'),
        'description': fields.text('Description', help='Description of Report Type'),
        'remark': fields.text('Remark'),
              }
line_categories()