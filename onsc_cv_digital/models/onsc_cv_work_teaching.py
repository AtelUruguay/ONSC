# -*- coding: utf-8 -*-
from odoo import fields, models

POSITION_TYPES = [('effective', 'Efectivo'), ('interim', 'Interino'), ('honorary', 'Honorario')]
RESPONSIBLE_TYPES = [('yes', 'Sí'), ('no', 'No')]


class ONSCCVWorkTeaching(models.Model):
    _name = 'onsc.cv.work.teaching'
    _description = 'Docencia'
    _inherit = ['onsc.cv.abstract.work', 'onsc.cv.abstract.conditional.state', 'onsc.cv.abstract.institution']
    _catalogs2validate = ['institution_id', 'subinstitution_id', 'professional_link_id']

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade', required=True)
    professional_link_id = fields.Many2one('onsc.cv.professional.link', 'Vínculo profesional', required=True)
    position_type = fields.Selection(POSITION_TYPES, 'Tipo de cargo')
    is_full_time = fields.Boolean('¿Dedicación total?')
    responsible_type = fields.Selection(RESPONSIBLE_TYPES, '¿Es responsable de cátedra o de programa académico?',
                                        required=True)
    program_name = fields.Char('Nombre de la cátedra o programa académico')
    # Grilla Materias
    program_ids = fields.Many2many('onsc.cv.academic.program', relation='onsc_cv_work_teaching_program_rel',
                                   string='Materias')
    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.cv.education.area.teaching', inverse_name='teaching_id',
                                         string="Áreas relacionadas con esta educación")
    other_relevant_information = fields.Text(string="Otra información relevante")
    digital_doc_file = fields.Binary('Comprobantes', required=True)
    digital_doc_name = fields.Char('Nombre del comprobante')
    digital_doc_description = fields.Char('Descripción del comprobante')


class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.teaching'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (Docencia)'

    teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia')
