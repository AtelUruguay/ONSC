# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCVDigitalWorkExperience(models.Model):
    _name = 'onsc.cv.work.experience'
    _description = 'Experiencia laboral'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    position = fields.Char("Cargo", required=True)
    country_id = fields.Many2one("res.country", string="País donde desempeñó", required=True)
    city_id = fields.Many2one("onsc.cv.location", string="Ciudad donde desempeñó", required=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    company_type = fields.Selection([('public', 'Pública'), ('private', 'Privada')], string="Tipo de empresa",
                                    required=True)
    #TO-DO: Revisar este campo, No esta en catalogo
    # inciso = fields.Char("Inciso")
    #TO-DO: Revisar este campo, No esta en catalogo
    # executing_unit = fields.Char("Unidad ejecutora")
    company_name = fields.Char("Empresa")
    unit_name = fields.Char("Área/Unidad")
    entry_institution_id = fields.Many2one("onsc.cv.entry", string="Rubro de la institución", required=True)
    hierarchical_level_id = fields.Many2one("onsc.cv.experience.hierarchical.level", string="Nivel jerárquico",
                                            required=True)
    take_decisions = fields.Selection([('operative', 'Toma decisiones de la operativa'),
                                       ('strategic', 'Toma decisiones a nivel estratégico y de dirección')],
                                      string="Toma decisiones", required=True)
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=[('si', 'Si'), ('no', 'No'), ],
                                        required=True, )
    people_charge = fields.Integer("Cantidad de personas a cargo", required=True)
    organizational_units_charge = fields.Integer("Cantidad de unidades organizativas a cargo", required=True)
    start_date = fields.Date("Período desde", required=True)
    currently_working = fields.Selection(string="Actualmente trabajando", selection=[('si', 'Si'), ('no', 'No')],
                                         required=True, )
    end_date = fields.Date("Período hasta", required=True)
    #TO-DO: Revisar este campo, No esta en catalogo
    # reason_discharge = fields.Char("Causal de egreso")
    hours_worked_monthly = fields.Integer("Cantidad de horas trabajadas mensualmente", required=True)
    description_tasks = fields.Char(string="Descripción de tareas", required=True)
    experience_task_ids = fields.One2many("onsc.cv.work.experience.task", inverse_name="work_experience_id",
                                          string="Tareas", required=False, )
    receipt_file = fields.Binary("Comprobante", required=True)

    @api.constrains('start_date', 'end_date')
    def _date_validation(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(_('El período de inicio debe ser anterior a la período de finalización'))


class ONSCCVDigitalWorkExperienceTask(models.Model):
    _name = 'onsc.cv.work.experience.task'
    _description = 'Tareas realizadas'

    work_experience_id = fields.Many2one("onsc.cv.work.experience", string="Experiencia laboral", index=True)
    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    work_area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                                   required=True)
