# -*- coding: utf-8 -*-
from odoo import fields, models

WE_HISTORY_COLUMNS = [
    'company_type',
    'country_id',
    'start_date',
    'currently_volunteering',
    'unit_name',
    'hours_monthly',
    'receipt_description',
    'receipt_file',
    'receipt_filename',
    'description_tasks',
    'inciso_id',
    'operating_unit_id'
]

WE_TREE_HISTORY_COLUMNS = [
    'start_date',
    'end_date',
    'company_type',
    'company_name_calc',
    'unit_name',
    'country_id',
    'hours_monthly',
]


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.legajo.volunteering'
    _inherit = ['onsc.cv.volunteering', 'model.history']
    _description = 'Legajo - Voluntariado'
    _history_model = 'onsc.legajo.volunteering.history'
    _history_columns = WE_HISTORY_COLUMNS
    _tree_history_columns = WE_TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one("onsc.cv.volunteering", string=u"Voluntariado origen")

    volunteering_task_ids = fields.One2many(
        "onsc.legajo.volunteering.task",
        inverse_name="legajo_volunteering_id",
        string="Tareas",

    )

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_volunteering_form_view').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoVolunteeringTask(models.Model):
    _name = 'onsc.legajo.volunteering.task'
    _inherit = 'onsc.cv.volunteering.task'
    _description = 'Legajo - Tareas de Voluntariado'

    legajo_volunteering_id = fields.Many2one(
        "onsc.legajo.volunteering",
        string="Voluntariado",
        ondelete='cascade'
    )


class ONSCLegajoVolunteeringHistory(models.Model):
    _name = 'onsc.legajo.volunteering.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.volunteering'

    history_receipt_file = fields.Binary(string="Comprobante")
