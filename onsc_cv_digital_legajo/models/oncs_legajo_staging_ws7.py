# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, tools, api, _
from odoo.exceptions import ValidationError


class ONSCLegajoStagingWS7(models.Model):
    _inherit = 'onsc.legajo.staging.ws7'

    def _set_modif_funcionario_extras(self, contract, record):
        contract.legajo_id.cv_digital_id.suspend_security().write({
            'marital_status_id': record.marital_status_id.id
        })
        return True
