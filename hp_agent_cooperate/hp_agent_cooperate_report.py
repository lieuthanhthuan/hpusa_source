# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Vision Software (<http://visoftware.com>). All Rights Reserved
#
##############################################################################
from dateutil import relativedelta 
import time
from datetime import datetime
from datetime import timedelta
from openerp.osv import fields, osv, orm
from openerp.addons.pxgo_openoffice_reports import openoffice_report
from openerp.report import report_sxw
  


openoffice_report.openoffice_report(
    'report.notify_commission',
    'commission.worksheet',
) 





