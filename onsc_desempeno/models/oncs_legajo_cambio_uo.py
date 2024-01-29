# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoCambioUO(models.Model):
    _inherit = 'onsc.legajo.cambio.uo'

    def _action_confirm(self):
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        new_job = super(ONSCLegajoCambioUO, self)._action_confirm()
        # OBTENIENDO COLABORADORES
        evaluation_list_lines = EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.start_date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.start_date),
            ('generated', '=', True),
            ('job_id', '=', self.id),
        ])
        evaluation_list_lines.suspend_security().mapped('evaluation_ids').write(
            {'current_job_id': new_job.id}
        )
        return new_job
