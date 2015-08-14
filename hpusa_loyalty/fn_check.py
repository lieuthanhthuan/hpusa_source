
import tools
from osv import fields, osv

class fn_check_loyalty(osv.osv):
    _name = "fn.check.loyalty"
    _auto = False
    def init(self, cr):
        cr.execute("""
    CREATE OR REPLACE FUNCTION fn_check()
        RETURNS SETOF record AS
        $BODY$ 
        DECLARE
        find_insert BOOLEAN;
        BEGIN 
            CREATE TEMPORARY TABLE table_check ON COMMIT DROP AS  
            SELECT SUM(point) as point , partner_id
                    FROM (SELECT COALESCE(SUM(point), 0) as point, partner_id
                            FROM  hpusa_loyalty_move WHERE state='done' AND type='cumulative' AND end_date < date
                            GROUP BY partner_id
                        UNION ALL
                        SELECT COALESCE(SUM(point), 0) as point, partner_id
                            FROM  hpusa_loyalty_move WHERE state='done' AND type='used' AND end_date < date
                             GROUP BY partner_id
                        UNION ALL
                        SELECT COALESCE(SUM(point), 0) as point, partner_id
                            FROM  hpusa_loyalty_move WHERE state='expired' AND type='used' AND end_date < date
                             GROUP BY partner_id
                    ) as tab
                    GROUP BY partner_id;
                    
         find_insert := (CASE WHEN EXISTS(SELECT * FROM table_check) THEN True ELSE False END);
         IF find_insert THEN
        INSERT INTO hpusa_loyalty_move(name, date, partner_id, point, type, state)
        SELECT 'Expired' as name, date as date , partner_id, - point, 'expired' as type, 'done' as state
        FROM table_check
        WHERE point > 0;
         END IF;
        RETURN QUERY SELECT True;
          END;   
        $BODY$
    LANGUAGE plpgsql;
        """)
fn_check_loyalty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
