# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVStatusCivil(models.Model):
    _name = 'onsc.cv.status.civil'
    _description = 'Estado Civil'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del Estado Civil', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Estado Civil debe ser único'),
    ]


class ONSCCVDriversLicenseCategories(models.Model):
    _name = 'onsc.cv.drivers.license.categories'
    _description = 'Categoría de licencia de conducir'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre de la Categoría de licencia de conducir', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la Categoría de Licencia de conducir debe ser único'),
    ]


class ONSCCVGender(models.Model):
    _name = 'onsc.cv.gender'
    _description = 'Género'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del Género', required=True)
    active = fields.Boolean(string='Activo', default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción Otra/o ?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Género debe ser único'),
    ]


class ONSCCVRace(models.Model):
    _name = 'onsc.cv.race'
    _description = 'Raza'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la Raza', required=True)
    active = fields.Boolean(string='Activo', default=True)
    race_type = fields.Selection(
        string=u'Tipo',
        selection=[('race', u'Raza'),
                   ('recognition', u'Reconocimiento'),
                   ('both', u'Ambos')])
    is_option_other_enable = fields.Boolean(u'¿Permitir opción Otra/o ?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la Raza debe ser único'),
    ]


class ONSCCVDocumentType(models.Model):
    _name = 'onsc.cv.document.type'
    _description = 'Tipo de documento'

    code = fields.Char(string=u"Código")
    name = fields.Char(string=u"Nombre del Tipo de documento", required=True)
    active = fields.Boolean(string="Activo", default=True)
    code_other = fields.Char(string=u"Otro código")
    is_org = fields.Boolean(u'Aplica organismo')
    is_sice = fields.Boolean(u'Aplica SICE')
    code_sice = fields.Char(u'Código SICE')
    is_rupe = fields.Boolean(u'Aplica RUPE')
    code_rupe = fields.Char(u'Código RUPE')
    is_dgi = fields.Boolean(u'Aplica DGI')
    code_dgi = fields.Char(u'Código DGI')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Tipo de Documento debe ser único'),
    ]


class ONSCCVStudyLevel(models.Model):
    _name = 'onsc.cv.study.level'
    _description = 'Nivel de estudio'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del nivel de estudio', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Nivel de Estudio debe ser único'),
    ]


class ONSCCVEducationalAreas(models.Model):
    _name = 'onsc.cv.educational.areas'
    _description = 'Area educativa'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del área educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El Nombre del Área Educativa debe ser único'),
    ]


class ONSCCVExperienceHierarchicalLevel(models.Model):
    _name = 'onsc.cv.experience.hierarchical.level'
    _description = 'Nivel jeráquico de experiencia'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del Nivel jerárquico', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Nivel jeráquico de experiencia debe ser único'),
    ]


class ONSCCVSEducationalAreas(models.Model):
    _name = 'onsc.cv.educational.subarea'
    _description = 'Sub áreas educativas'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la sub área educativa', required=True)
    area_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área Educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El Nombre de la Sub Área Educativa debe ser único'),
    ]


class ONSCCVDisciplineEducational(models.Model):
    _name = 'onsc.cv.discipline.educational'
    _description = 'Disciplina educativa'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la disciplina educativa', required=True)
    area_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área Educativa', required=True)
    subarea_id = fields.Many2one('onsc.cv.educational.subarea', string=u'Sub área educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El Nombre de la Disciplina Educativa debe ser único'),
    ]

    @api.onchange('area_id')
    def onchange_area_id(self):
        if self.area_id != self.subarea_id.area_id or self.area_id is False:
            self.subarea_id = False


class ONSCCVKnowledge(models.Model):
    _name = 'onsc.cv.knowledge'
    _description = 'Conocimiento'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del conocimiento', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El Nombre del Conocimiento debe ser único'),
    ]


class ONSCCVKeyTask(models.Model):
    _name = 'onsc.cv.key.task'
    _description = 'Tarea clave'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre de la Tarea clave', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la Tarea clave debe ser único'),
    ]


class ONSCCVWorkArea(models.Model):
    _name = 'onsc.cv.work.area'
    _description = 'Área de trabajo'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del Área de trabajo', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Área de trabajo debe ser único'),
    ]
