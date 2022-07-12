# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVDigitalWorkExperience(models.Model):
    _name = 'onsc.cv.work.experience'
    _description = 'Experiencia laboral'
    _inherit = 'onsc.cv.abstract.work'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    company_type = fields.Selection([('public', 'Pública'), ('private', 'Privada')], string="Tipo de empresa",
                                    required=False)
    country_id = fields.Many2one("res.country", string="País", required=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    city_id = fields.Many2one("onsc.cv.location", string="Ciudad donde desempeñó", required=True)
    unit_name = fields.Char("Área/Unidad")
    company_name = fields.Char("Empresa")
    entry_institution_id = fields.Many2one("onsc.cv.entry", string="Rubro de la institución", required=True)
    hierarchical_level_id = fields.Many2one("onsc.cv.experience.hierarchical.level", string="Nivel jerárquico",
                                            required=True)
    receipt_file = fields.Binary("Comprobante", required=True)
    take_decisions = fields.Selection([('operative', 'Toma decisiones de la operativa'),
                                       ('strategic', 'Toma decisiones a nivel estratégico y de dirección')],
                                      string="Toma decisiones", required=True)
    people_charge = fields.Integer("Cantidad de personas a cargo", required=True)
    organizational_units_charge = fields.Integer("Cantidad de unidades organizativas a cargo", required=True)

    # TO-DO: Revisar este campo, No esta en catalogo
    # reason_discharge = fields.Char("Causal de egreso")
    task_ids = fields.One2many("onsc.cv.work.experience.task", inverse_name="work_experience_id",
                               string="Tareas", required=False, )


class ONSCCVDigitalOriginInstitutionTask(models.Model):
    _name = 'onsc.cv.work.experience.task'
    _description = 'Tareas realizadas'

    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                              required=True)
    work_experience_id = fields.Many2one("onsc.cv.work.experience", string="Experiencia laboral", index=True)
