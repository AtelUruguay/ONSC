# -*- coding: utf-8 -*-
from odoo import Command
from odoo import fields, models

HISTORY_COLUMNS = [
    'basic_education_level',
    'country_id',
    'institution_id',
    'subinstitution_id',
    'state',
    'start_date',
    'end_date',
    'coursed_years',
    'other_relevant_information',
    'study_certificate_file',
    'study_certificate_filename',
    # HISTORICOS
    'documentary_validation_date',
    'documentary_validation_state',
    'documentary_user_id'
]
TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'end_date': 'Fin',
    'basic_education_level': 'Nivel',
    'institution_id': 'Institución',
    'subinstitution_id': 'Sub institución',
}

ADVANCED_HISTORY_COLUMNS = [
    'country_id',
    'institution_id',
    'subinstitution_id',
    'advanced_study_level_id',
    'academic_program_id',
    'homologated_title',
    'homologated_title_date',
    'apostilled_title',
    'apostilled_date',
    'state',
    'start_date',
    'egress_date',
    'issue_title_date',
    'apostilled_date',
    'state_thesis',
    'title_thesis',
    'description_thesis',
    'final_note_thesis',
    'max_note_thesis',
    'tutor',
    'country_code',
    'scholarship',
    'max_scholarship',
    'credits_far',
    'credits_training',
    'apostille_file',
    'apostille_filename',
    # FIXME 28.8.3 PS07 13857
    'scolarship_certificate_file',
    'scolarship_certificate_filename',
    'egress_certificate_file',
    'egress_certificate_filename',
    'revalidated_certificate_file',
    'revalidated_certificate_filename',
    'homologated_certificate_file',
    'homologated_certificate_filename',
    'apostille_file',
    'apostille_filename',
    'is_require_thesis',
    'study_certificate_file',
    'study_certificate_filename',
    'other_relevant_information',
    'knowledge_acquired_ids',
    'knowledge_thesis_ids',
    # HISTORICOS
    'documentary_validation_date',
    'documentary_validation_state',
    'documentary_user_id',
    'generic_academic_program_id',
    'name_generic_academic_program'

]
ADVANCED_TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'egress_date': 'Fin',
    'advanced_study_level_id': 'Nivel',
    'institution_id': 'Institución',
    'subinstitution_id': 'Sub institución',
    'academic_program_id': 'Programa académico',
    'state': 'Estado',
}


class ONSCCVDigitalLegajoFormationBasic(models.Model):
    _inherit = 'onsc.cv.basic.formation'
    _legajo_model = 'onsc.legajo.basic.formation'
    _order = 'start_date desc'


class ONSCLegajoBasicFormation(models.Model):
    _name = 'onsc.legajo.basic.formation'
    _inherit = ['onsc.cv.basic.formation', 'model.history']
    _description = 'Legajo - Formación básica'
    _history_model = 'onsc.legajo.basic.formation.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.basic.formation",
        string=u"Formación básica origen",
        ondelete="set null"
    )

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_basic_formation_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoBasicFormationHistory(models.Model):
    _name = 'onsc.legajo.basic.formation.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.basic.formation'

    history_study_certificate_file = fields.Binary(string="Certificado de estudio")


class ONSCCVFormationAdvanced(models.Model):
    _inherit = 'onsc.cv.advanced.formation'
    _legajo_model = 'onsc.legajo.advanced.formation'
    _order = 'start_date desc'

    def _update_legajo_record_vals(self, vals):
        if 'area_related_education_ids' in vals:
            vals['area_related_education_ids'] = [Command.clear()] + vals['area_related_education_ids']
        return vals


class ONSCLegajoAdvancedFormation(models.Model):
    _name = 'onsc.legajo.advanced.formation'
    _inherit = ['onsc.cv.advanced.formation', 'model.history']
    _description = 'Legajo - Formación avanzada'
    _history_model = 'onsc.legajo.advanced.formation.history'
    _history_columns = ADVANCED_HISTORY_COLUMNS
    _tree_history_columns = ADVANCED_TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.advanced.formation",
        string=u"Formación avanzada origen",
        ondelete="set null"
    )

    area_related_education_ids = fields.One2many('onsc.legajo.area.related.education', 'legajo_investigation_id',
                                                 string=u'Áreas relacionadas con esta educación')
    knowledge_thesis_ids = fields.Many2many('onsc.cv.knowledge', 'legajo_knowledge_thesis_id',
                                            string=u'Conocimientos aplicados a su tesis',
                                            ondelete='restrict',
                                            help='Sólo se pueden seleccionar 5 tipos de conocimientos')

    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'legajo_knowledge_acquired_advanced_formation_rel',
                                              string=u'Conocimientos adquiridos',
                                              copy=True,
                                              required=True,
                                              ondelete='restrict',
                                              store=True)
    show_generic_academic_program = fields.Boolean('¿Ver programa academico generico?', history=True)
    displayed_academic_program = fields.Char(string='Programa académico', history=True)
    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_advanced_formation_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoAreaRelatedEducation(models.Model):
    _name = 'onsc.legajo.area.related.education'
    _inherit = 'onsc.cv.area.related.education'
    _description = 'Legajo - Integrantes'

    legajo_investigation_id = fields.Many2one(
        "onsc.legajo.advanced.formation",
        string="Docencia",
        ondelete='cascade'
    )


class ONSCLegajoAdvancedFormationHistory(models.Model):
    _name = 'onsc.legajo.advanced.formation.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.advanced.formation'

    history_apostille_file = fields.Binary(string="Apostilla")
    history_revalidated_certificate_file = fields.Binary(string="Certificado de reválida de título")
    history_egress_certificate_file = fields.Binary(string="Certificado de egreso / título")
    # FIXME 28.8.3 PS07 13857
    history_scolarship_certificate_file = fields.Binary(string="Escolaridad")
    history_homologated_certificate_file = fields.Binary(string="Certificado de homologación")
    history_study_certificate_file = fields.Binary(string="Certificado de estudio")
