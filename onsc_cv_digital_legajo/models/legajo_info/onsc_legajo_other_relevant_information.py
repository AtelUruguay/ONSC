# -*- coding: utf-8 -*-
from odoo import fields, models, api

HISTORY_COLUMNS = [
    'theme',
    'description',
    # HISTORICOS
    'documentary_validation_date',
    'documentary_validation_state',
    'documentary_user_id'
]

TREE_HISTORY_COLUMNS = [
    'theme',
    'description',
]


class ONSCCVOtherRelevantInformation(models.Model):
    _inherit = 'onsc.cv.other.relevant.information'
    _legajo_model = 'onsc.legajo.relevant.information'


class ONSCLegajoRelevantInformation(models.Model):
    _name = 'onsc.legajo.relevant.information'
    _inherit = ['onsc.cv.other.relevant.information', 'model.history']
    _description = u'Legajo - Otra información relevante'
    _history_model = 'onsc.legajo.relevant.information.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one("onsc.cv.other.relevant.information",
                                       string=u"Otra información relevante origen",
                                       ondelete="set null")

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_relevant_information_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )

    @api.model
    def create(self, vals):
        record = super(ONSCLegajoRelevantInformation, self).create(vals)
        return record


# HISTORICOS
class ONSCLegajoRelevantInformationHistory(models.Model):
    _name = 'onsc.legajo.relevant.information.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.relevant.information'
