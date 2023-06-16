# -*- coding: utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

REQUIRED_FIELDS = ['date_start_commission', 'reason_description', 'norm_id', 'resolution_description',
                   'resolution_date', 'resolution_type', 'regime_commission_id']


class ONSCLegajoAltaCS(models.Model):
    _inherit = 'onsc.legajo.alta.cs'

    def _get_legajo_employee(self):
        employee = super(ONSCLegajoAltaCS, self.with_context(is_alta_vl=True))._get_legajo_employee()
        cv = employee.cv_digital_id
        vals = employee._get_info_fromcv()
        vals.update({
            'cv_birthdate': self.cv_birthdate,
            'cv_sex': self.cv_sex,
        })
        if cv.partner_id.user_ids:
            user_id = cv.partner_id.user_ids[0]
        else:
            user_id = cv.partner_id.user_id
        if cv and employee.user_id.id != user_id.id:
            vals['user_id'] = user_id.id
        employee.write(vals)
        cv.write({'is_docket': True})
        return employee
