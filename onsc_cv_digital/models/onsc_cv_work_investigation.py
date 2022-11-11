# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

POSITION_TYPES = [('effective', 'Efectivo'), ('interim', 'Interino'), ('honorary', 'Honorario')]
INVESTIGATION_TYPES = [('invest_line', 'Línea de investigación'),
                       ('invest_project', 'Proyecto de investigación y desarrollo')]
PARTICIPATION_TYPES = [('coordinator', 'Coordinador o responsable'), ('team_member', 'Integrante del equipo')]
CATEGORY_TYPES = [('applied', 'Aplicada'), ('fundamental', 'Fundamental'), ('mixed', 'Mixta')]
SITUATION_TYPES = [('canceled', 'Cancelado'), ('finished', 'Concluido'), ('in_progress', 'En marcha')]


class ONSCCVWorkInvestigation(models.Model):
    _name = 'onsc.cv.work.investigation'
    _description = 'Investigación'
    _inherit = ['onsc.cv.abstract.work', 'onsc.cv.abstract.conditional.state', 'onsc.cv.abstract.institution']
    _catalogs_2validate = ['institution_id', 'subinstitution_id']
    _order = 'start_date desc'

    investigation_type = fields.Selection(INVESTIGATION_TYPES, 'Tipo de investigación', required=True)
    name = fields.Char('Nombre de la investigación', required=True)
    description = fields.Text('Descripción de la investigación', required=True)
    participation_type = fields.Selection(PARTICIPATION_TYPES, 'Tipo de participación', required=True)
    category_type = fields.Selection(CATEGORY_TYPES, 'Categoría')
    situation_type = fields.Selection(SITUATION_TYPES, 'Situación')
    research_type_id = fields.Many2one('onsc.cv.research.types.classes', string='Tipo/clase')
    is_option_other_enable = fields.Boolean(related='research_type_id.is_option_other_enable')
    other_research_type = fields.Char('Otro tipo/clase')

    # Grilla Integrantes
    member_ids = fields.One2many('onsc.cv.work.investigation.member', inverse_name='investigation_id',
                                 string='Integrantes', copy=True)

    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.cv.education.area.investigation', inverse_name='investigation_id',
                                         string="Áreas relacionadas con esta educación", copy=True)
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', relation='knowledge_acquired_investigation_rel',
                                              string="Conocimientos adquiridos",
                                              required=True,
                                              copy=True,
                                              store=True)

    additional_information = fields.Text(string="Información adicional")
    other_relevant_information = fields.Text(string="Otra información relevante")
    # Grila Comprobantes
    receipt_ids = fields.One2many('onsc.cv.work.investigation.receipt.file', inverse_name='investigation_id',
                                  string='Comprobantes', copy=True)

    @api.onchange('knowledge_acquired_ids')
    def onchange_knowledge_acquired_ids(self):
        if len(self.knowledge_acquired_ids) > 5:
            self.knowledge_acquired_ids = self.knowledge_acquired_ids[:5]
            return cv_warning(_("Sólo se pueden seleccionar 5 tipos de conocimientos"))

    def _get_json_dict(self):
        json_dict = super(ONSCCVWorkInvestigation, self)._get_json_dict()
        json_dict.extend([
            "hours_worked_monthly",
            "currently_working",
            "position",
            "is_paid_activity",
            "country_id",
            "company_type",
            "company_name",
            "description_tasks",
            "start_date",
            "end_date",
            "investigation_type",
            "name",
            "description",
            "participation_type",
            "category_type",
            "situation_type", "research_type_id",
            "other_research_type",
            "additional_information",
            "other_relevant_information",
            "receipt_description",
            "conditional_validation_state",
            "conditional_validation_reject_reason",
            ("country_id", ['id', 'name']),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
            ("member_ids", [
                'id',
                'member',
                'is_responsible',
                'citation',
            ]),
            ("education_area_ids", self.env['onsc.cv.education.area.investigation']._get_json_dict()),
            ("knowledge_acquired_ids", ['id', 'name']),
        ])
        return json_dict


class ONSCCVWorkInvestigationMember(models.Model):
    _name = 'onsc.cv.work.investigation.member'
    _description = 'Integrante de la investigación'

    investigation_id = fields.Many2one('onsc.cv.work.investigation', 'Investigación', ondelete='cascade')
    member = fields.Char('Integrante', required=True, default=lambda self: self.get_default_member())
    is_responsible = fields.Boolean('¿Responsable?')
    citation = fields.Text('Citación')

    @api.model
    def get_default_member(self):
        """
        Si en la lista de integrantes no se ha adicionado el nombre del usuario entonces el valor por defecto
        es el nombre del usuario
        :return:
        """
        member_ids = self._context.get('member_ids')
        if not list(filter(lambda x: (x[0] == 0 and x[2]['member'] or x[0] in [1, 4] and self.browse(
                x[1]).member) == self.env.user.name, member_ids)):
            return self.env.user.name
        return False

    @api.model
    def create(self, values):
        _investigation_id = values.get('investigation_id')
        _member = values.get('member')
        _citation = values.get('citation')
        all_values_tocheck = _investigation_id and _member and _citation
        if all_values_tocheck and self.search_count([
            ('investigation_id', '=', _investigation_id),
            ('member', '=', _member),
            ('citation', '=', _citation),
        ]):
            return self
        return super(ONSCCVEducationAreaCourse, self).create(values)


class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.investigation'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (Investigación)'

    investigation_id = fields.Many2one('onsc.cv.work.investigation', 'Investigación', ondelete='cascade')

    @api.model
    def create(self, values):
        _investigation_id = values.get('investigation_id')
        _educational_area_id = values.get('educational_area_id')
        _educational_subarea_id = values.get('educational_subarea_id')
        _discipline_educational_id = values.get('discipline_educational_id')
        all_values_tocheck = _investigation_id and _educational_area_id and _educational_subarea_id and _discipline_educational_id
        if all_values_tocheck and self.search_count([
            ('investigation_id', '=', _investigation_id),
            ('educational_area_id', '=', _educational_area_id),
            ('educational_subarea_id', '=', _educational_subarea_id),
            ('discipline_educational_id', '=', _discipline_educational_id),
        ]):
            return self
        return super(ONSCCVEducationAreaCourse, self).create(values)

    def _get_json_dict(self):
        return [
            ("educational_area_id", ['id', 'name']),
            ("educational_subarea_id", ['id', 'name']),
            ("discipline_educational_id", ['id', 'name']),
        ]


class ONSCCVWorkInvestigationReceiptFile(models.Model):
    _name = 'onsc.cv.work.investigation.receipt.file'
    _description = 'Comprobantes de investigación'
    _inherit = 'onsc.cv.work.abstract.receipt.file'

    investigation_id = fields.Many2one('onsc.cv.work.investigation', 'Investigación', ondelete='cascade')

    @api.model
    def create(self, values):
        _investigation_id = values.get('investigation_id')
        _receipt_filename = values.get('receipt_filename')
        _receipt_description = values.get('receipt_description')
        all_values_tocheck = _investigation_id and _receipt_filename and _receipt_description
        if all_values_tocheck and self.search_count([
            ('investigation_id', '=', _investigation_id),
            ('receipt_filename', '=', _receipt_filename),
            ('receipt_description', '=', _receipt_description)
        ]):
            return self
        return super(ONSCCVEducationAreaCourse, self).create(values)
