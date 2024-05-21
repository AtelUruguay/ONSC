# -*- coding: utf-8 -*-
from odoo import Command
from odoo import fields, models

HISTORY_COLUMNS = [
    'country_id',
    'institution_id',
    'subinstitution_id',
    'currently_working',
    'is_paid_activity',
    'position',
    'knowledge_acquired_ids',
    'start_date',
    'end_date',
    'investigation_type',
    'name',
    'description',
    'participation_type',
    'category_type',
    'situation_type',
    'research_type_id',
    'other_research_type',
    'hours_worked_monthly',
]

TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'end_date': 'Fin',
    'investigation_type': 'Tipo',
    'name': 'Nombre',
    'institution_id': 'Institución',
    'subinstitution_id': 'Sub institución',
}


class ONSCCVDigitalWorkInvestigation(models.Model):
    _inherit = 'onsc.cv.work.investigation'
    _legajo_model = 'onsc.legajo.work.investigation'

    def _update_legajo_record_vals(self, vals):
        if 'member_ids' in vals:
            vals['member_ids'] = [Command.clear()] + vals['member_ids']
        if 'education_area_ids' in vals:
            vals['education_area_ids'] = [Command.clear()] + vals['education_area_ids']
        if 'receipt_ids' in vals:
            vals['receipt_ids'] = [Command.clear()] + vals['receipt_ids']
        return vals


class ONSCLegajoWorkInvestigation(models.Model):
    _name = 'onsc.legajo.work.investigation'
    _inherit = ['onsc.cv.work.investigation', 'model.history']
    _description = u'Legajo - Investigación'
    _history_model = 'onsc.legajo.work.investigation.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.work.investigation",
        string=u"Investigación origen",
        ondelete="set null"
    )

    # Grilla Integrantes
    member_ids = fields.One2many('onsc.legajo.work.investigation.member', inverse_name='legajo_investigation_id',
                                 string='Integrantes')

    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.legajo.education.area.investigation',
                                         inverse_name='legajo_investigation_id',
                                         string="Áreas relacionadas con esta educación", copy=True)

    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge',
                                              relation='legajo_knowledge_acquired_investigation_rel',
                                              string="Conocimientos adquiridos",
                                              required=True,
                                              copy=True,
                                              ondelete='restrict',
                                              store=True)
    # Grila Comprobantes
    receipt_ids = fields.One2many('onsc.legajo.work.investigation.receipt.file', inverse_name='legajo_investigation_id',
                                  string='Comprobantes', copy=True)

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_work_investigation_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoWorkInvestigationMember(models.Model):
    _name = 'onsc.legajo.work.investigation.member'
    _inherit = 'onsc.cv.work.investigation.member'
    _description = 'Legajo - Integrantes'

    legajo_investigation_id = fields.Many2one(
        "onsc.legajo.work.investigation",
        string="Docencia",
        ondelete='cascade'
    )


class ONSCLegajoEducationAreaInvestigation(models.Model):
    _name = 'onsc.legajo.education.area.investigation'
    _inherit = 'onsc.cv.education.area.investigation'
    _description = 'Legajo - Áreas relacionadas con esta educación'

    legajo_investigation_id = fields.Many2one(
        "onsc.legajo.work.investigation",
        string="Investigación",
        ondelete='cascade'
    )


class ONSCLegajoWorkInvestigationReceiptFile(models.Model):
    _name = 'onsc.legajo.work.investigation.receipt.file'
    _inherit = 'onsc.cv.work.investigation.receipt.file'
    _description = 'Legajo - Comprobantes'

    legajo_investigation_id = fields.Many2one(
        "onsc.legajo.work.investigation",
        string="Investigación",
        ondelete='cascade'
    )


# HISTORICOS
class ONSCLegajoWorkInvestigationHistory(models.Model):
    _name = 'onsc.legajo.work.investigation.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.work.investigation'
