
import tools
from osv import fields, osv

class fn_hpusa_loyalty(osv.osv):
    _name = "fn.hpusa.loyalty"
    _auto = False
    def init(self, cr):
        cr.execute("""
    CREATE OR REPLACE FUNCTION fn_loyalty(id integer,pro_id integer)
        RETURNS SETOF record AS
        $BODY$ 
        DECLARE
              sqlupdate VARCHAR;
              c_record RECORD;
        BEGIN 
            CREATE TEMPORARY TABLE loyalty ON COMMIT DROP AS  
            -- USER
            SELECT pr.id as program_id, co.id as con_id, pr.sequence, re.amount as amount, line.formula as formula, 0::NUMERIC as point, pr.end_date, pr.start_date FROM hpusa_register_loyalty_point re
                 LEFT JOIN loyalty_partner_rel rel ON(rel.partner_id = re.partner_id)
                 LEFT JOIN hpusa_loyalty_program pr ON(pr.id = rel.loyalty_id)
                 LEFT JOIN hpusa_loyalty_conditions co ON(co.loyalty_id = pr.id)
                 LEFT JOIN hpusa_loyalty_conditions_line line ON(line.condition_id = co.id)
                 WHERE re.id = $1  AND rel.partner_id = re.partner_id
                 AND pr.state = 'done'
		   AND pr.actived  = True
                 AND re.amount >= line.from_value AND 
                 CASE WHEN line.to_value IS NULL OR line.to_value =0 THEN 1=1 ELSE re.amount <= line.to_value END
                 AND co.type = re.type
                 AND co.obj = re.obj
                 AND CASE WHEN re.obj = 'shop' THEN co.shop_id = re.shop_id ELSE 1=1 END
                 AND CASE WHEN re.obj = 'location' THEN co.location_id = re.location_id ELSE 1=1 END
                 AND CASE WHEN $2 = 0 THEN pr.id IS NOT NULL ELSE pr.id = $2 END
                 AND CASE WHEN re.obj = 'cate_prod'  THEN co.shop_id = re.cate_prod_id ELSE 1=1 END
                 AND re.date >= pr.start_date AND re.date <= pr.end_date
                 AND re.date >= co.start_date AND re.date <= co.end_date
            -- GROUP
        UNION ALL
             SELECT pr.id as program_id, co.id as con_id, pr.sequence, re.amount as amount, line.formula as formula, 0::NUMERIC as point, pr.end_date, pr.start_date FROM hpusa_register_loyalty_point re
             LEFT JOIN res_partner_res_partner_category_rel carel ON(carel.partner_id = re.partner_id)
                 LEFT JOIN loyalty_partner_categoty_rel lrel ON(lrel.partner_category_id = carel.category_id)
                 LEFT JOIN hpusa_loyalty_program pr ON(pr.id = lrel.loyalty_id)
                 LEFT JOIN hpusa_loyalty_conditions co ON(co.loyalty_id = pr.id)
                 LEFT JOIN hpusa_loyalty_conditions_line line ON(line.condition_id = co.id)
                 WHERE re.id = $1
                 AND pr.state = 'done'
                 AND CASE WHEN $2 = 0 THEN pr.id IS NOT NULL ELSE pr.id = $2 END
                 AND pr.actived  = True
                 AND re.amount >= line.from_value AND 
                 CASE WHEN line.to_value IS NULL OR line.to_value =0 THEN 1=1 ELSE re.amount <= line.to_value END
                 AND co.type = re.type
                 AND co.obj = re.obj
                 AND CASE WHEN re.obj = 'shop' THEN co.shop_id = re.shop_id ELSE 1=1 END
                 AND CASE WHEN re.obj = 'location' THEN co.location_id = re.location_id ELSE 1=1 END
                 AND CASE WHEN re.obj = 'cate_prod'  THEN co.shop_id = re.cate_prod_id ELSE 1=1 END
                 AND re.date >= pr.start_date AND re.date <= pr.end_date
                 AND re.date >= co.start_date AND re.date <= co.end_date
                 
             -- NO CUSTOMER, NO GROUP
             UNION ALL
             SELECT pr.id as program_id, co.id as con_id, pr.sequence, re.amount as amount, line.formula as formula, 0::NUMERIC as point, pr.end_date, pr.start_date
                 FROM hpusa_register_loyalty_point re
                 LEFT JOIN hpusa_loyalty_program pr ON(1=1)
                 LEFT JOIN loyalty_partner_rel rel ON(rel.loyalty_id = pr.id)
                 LEFT JOIN loyalty_partner_categoty_rel lrel ON(lrel.loyalty_id = pr.id)
                 LEFT JOIN hpusa_loyalty_conditions co ON(co.loyalty_id = pr.id)
                 LEFT JOIN hpusa_loyalty_conditions_line line ON(line.condition_id = co.id)
                 WHERE re.id = $1  AND rel.loyalty_id IS NULL AND lrel.loyalty_id IS NULL
                 AND pr.state = 'done'
                 AND CASE WHEN $2 = 0 THEN pr.id IS NOT NULL ELSE pr.id = $2 END
		   AND pr.actived  = True
                 AND re.amount >= line.from_value AND 
                 CASE WHEN line.to_value IS NULL OR line.to_value =0 THEN 1=1 ELSE re.amount <= line.to_value END
                 AND co.type = re.type
                 AND co.obj = re.obj
                 AND CASE WHEN re.obj = 'shop' THEN co.shop_id = re.shop_id ELSE 1=1 END
                 AND CASE WHEN re.obj = 'location' THEN co.location_id = re.location_id ELSE 1=1 END
                 AND CASE WHEN re.obj = 'cate_prod'  THEN co.shop_id = re.cate_prod_id ELSE 1=1 END
                 AND re.date >= pr.start_date AND re.date <= pr.end_date
                 AND re.date >= co.start_date AND re.date <= co.end_date;
        FOR c_record IN (SELECT * FROM loyalty)
        LOOP
            sqlupdate:= 'UPDATE loyalty
                SET point = '||c_record.formula||'
                 WHERE program_id = '||c_record.program_id ||' AND con_id = '||c_record.con_id;    
            IF sqlupdate IS NOT NULL THEN
            EXECUTE(sqlupdate);
            END IF;
        END LOOP;
        RETURN QUERY SELECT distinct program_id, con_id, amount::NUMERIC, point, end_date, start_date FROM loyalty WHERE sequence = (SELECT MIN(sequence) FROM loyalty);
          END;   
        $BODY$
    LANGUAGE plpgsql;
        """)
fn_hpusa_loyalty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
