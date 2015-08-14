# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://gscom.vn>). All Rights Reserved
#
##############################################################################


from openerp import tools
from openerp.osv import fields, osv

class gs_mrp_report_1(osv.osv):
    _name = "hpusa.loyalty.report.1"
    _description = "Loyalty Report"
    _auto = False
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer',readonly=True),
        'voucher_id': fields.many2one('hpusa.voucher', 'Voucher',readonly=True),
        'point_current': fields.integer('Point Current'),
        'point_voucher': fields.integer('Point Voucher'),
        'option':  fields.text('option'),
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        'program_id': fields.many2one('hpusa.loyalty.program', 'Program',readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hpusa_loyalty_report_1')
        cr.execute("""
                create or replace view hpusa_loyalty_report_1 as 
    (
   SELECT  row_number() OVER (ORDER BY partner_id, 1::integer)::integer AS id, partner_id, voucher_id, option, point_current, point_voucher, company_id, program_id
    FROM (
          SELECT DISTINCT res.id as partner_id, v.id as voucher_id, p.id as program_id, '1'::text as option,
        ((SELECT COALESCE(SUM(point), 0) as point
                FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id AND program = p.id)
               + (SELECT COALESCE(SUM(point), 0) as point
                FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id AND program = p.id)
               -(SELECT SUM(point) as point  
                FROM (SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id AND end_date < date AND program = p.id
                UNION ALL
                SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id AND end_date < date AND program = p.id
                ) as tab)
              ) as point_current, v.point as point_voucher, v.company_id
        FROM  res_partner res
              LEFT JOIN hpusa_voucher v ON(1=1)
              LEFT JOIN hpusa_loyalty_move move ON( move.partner_id = res.id)
              LEFT JOIN hpusa_loyalty_program p ON( p.id = move.program)
        WHERE 
                ((SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id)
               + (SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id)
               -(SELECT SUM(point) as point  
                    FROM (SELECT COALESCE(SUM(point), 0) as point
                            FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id AND end_date < date
                        UNION ALL
                        SELECT COALESCE(SUM(point), 0) as point
                            FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id AND end_date < date
                    ) as tab)
               ) > v.point AND res.id IN(SELECT partner_id FROM hpusa_loyalty_move WHERE state='done') AND v.state = 'done' AND v.actived = TRUE
    UNION ALL 

    SELECT  DISTINCT  res.id as partner_id, v.id as voucher_id, p.id as program_id, '2'::text as option,
        ((SELECT COALESCE(SUM(point), 0) as point
                FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id AND program = p.id)
               + (SELECT COALESCE(SUM(point), 0) as point
                FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id AND program = p.id)
               -(SELECT SUM(point) as point  
                FROM (SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id AND end_date < date AND program = p.id
                UNION ALL
                SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id AND end_date < date AND program = p.id
                ) as tab)
              ) as point_current, v.point as point_voucher, v.company_id
    FROM  res_partner res
          LEFT JOIN hpusa_voucher v ON(1=1)
          LEFT JOIN hpusa_loyalty_move move ON( move.partner_id = res.id)
          LEFT JOIN hpusa_loyalty_program p ON( p.id = move.program)
    WHERE 
              ((SELECT COALESCE(SUM(point), 0) as point
                FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id)
               + (SELECT COALESCE(SUM(point), 0) as point
                FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id)
               -(SELECT SUM(point) as point  
                FROM (SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND partner_id = res.id AND end_date < date
                UNION ALL
                SELECT COALESCE(SUM(point), 0) as point
                    FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND partner_id = res.id AND end_date < date
                ) as tab)
              ) < v.point AND res.id IN(SELECT partner_id FROM hpusa_loyalty_move WHERE state='done') AND v.state = 'done'  AND v.actived = TRUE) as tab
         WHERE program_id IS NOT NULL
     )
    
        """)
        
gs_mrp_report_1()
