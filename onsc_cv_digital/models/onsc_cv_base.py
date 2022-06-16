# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVStatusCivil(models.Model):
    _name = 'onsc.cv.status.civil'
    _description = 'Estado Civil'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del estado civil', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del estado civil debe ser único'),
    ]


class ONSCCVDriversLicenseCategories(models.Model):
    _name = 'onsc.cv.drivers.license.categories'
    _description = 'Categoría de licencia de conducir'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre de la categoría de licencia de conducir', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la categoría de licencia de conducir debe ser único'),
    ]


class ONSCCVGender(models.Model):
    _name = 'onsc.cv.gender'
    _description = 'Género'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del género', required=True)
    active = fields.Boolean(string='Activo', default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')
    record = fields.Boolean(u'Constancia')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del género debe ser único'),
    ]


class ONSCCVRace(models.Model):
    _name = 'onsc.cv.race'
    _description = 'Raza'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la raza', required=True)
    active = fields.Boolean(string='Activo', default=True)
    race_type = fields.Selection(
        string=u'Tipo',
        selection=[('race', u'Raza'),
                   ('recognition', u'Reconocimiento'),
                   ('both', u'Ambos')])
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la raza debe ser único'),
    ]


class ONSCCVDocumentType(models.Model):
    _name = 'onsc.cv.document.type'
    _description = 'Tipo de documento'

    code = fields.Char(string=u"Código")
    name = fields.Char(string=u"Nombre del tipo de documento", required=True)
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
         u'El nombre del tipo de documento debe ser único'),
    ]


class ONSCCVStudyLevel(models.Model):
    _name = 'onsc.cv.study.level'
    _description = 'Nivel de estudio'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del nivel de estudio', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del nivel de estudio debe ser único'),
    ]


class ONSCCVEducationalAreas(models.Model):
    _name = 'onsc.cv.educational.areas'
    _description = 'Area educativa'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del área educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del área educativa debe ser único'),
    ]


class ONSCCVExperienceHierarchicalLevel(models.Model):
    _name = 'onsc.cv.experience.hierarchical.level'
    _description = 'Nivel jeráquico de experiencia'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del nivel jerárquico', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del nivel jeráquico de experiencia debe ser único'),
    ]


class ONSCCVSEducationalAreas(models.Model):
    _name = 'onsc.cv.educational.subarea'
    _description = 'Sub área educativa'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la sub área educativa', required=True)
    area_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la sub área educativa debe ser único'),
    ]


class ONSCCVDisciplineEducational(models.Model):
    _name = 'onsc.cv.discipline.educational'
    _description = 'Disciplina educativa'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la disciplina educativa', required=True)
    area_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área educativa', required=True)
    subarea_id = fields.Many2one('onsc.cv.educational.subarea', string=u'Sub área educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la disciplina educativa debe ser único'),
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
         u'El nombre del conocimiento debe ser único'),
    ]


class ONSCCVKeyTask(models.Model):
    _name = 'onsc.cv.key.task'
    _description = 'Tarea clave'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre de la tarea clave', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la tarea clave debe ser único'),
    ]


class ONSCCVWorkArea(models.Model):
    _name = 'onsc.cv.work.area'
    _description = 'Área de trabajo'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del área de trabajo', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del área de trabajo debe ser único'),
    ]


class ONSCCVTypeTutor(models.Model):
    _name = 'onsc.cv.type.tutor'
    _description = 'Tipo de tutoría'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del tipo de tutoría', required=True)
    active = fields.Boolean(string="Activo", default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del tipo de tutoría debe ser único')
    ]


class ONSCCVTypeOrientation(models.Model):
    _name = 'onsc.cv.type.orientation'
    _description = 'Tipo de orientación'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del tipo de orientación', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del tipo de orientación debe ser único')
    ]


class ONSCCVDivulgationMedia(models.Model):
    _name = 'onsc.cv.divulgation.media'
    _description = 'Medio de divulgación'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del medio de divulgación', required=True)
    active = fields.Boolean(string="Activo", default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del medio de divulgación debe ser único')
    ]


class ONSCCVResearchTypesClasses(models.Model):
    _name = 'onsc.cv.research.types.classes'
    _description = 'Tipos o clase de investigación'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de clase de investigación', required=True)
    active = fields.Boolean(string='Activo', default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la clase de investigación debe ser único'),
    ]


class ONSCCVLanguage(models.Model):
    _name = 'onsc.cv.language'
    _description = 'Idioma'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del idioma', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del idioma debe ser único'),
    ]


class ONSCCVTypeSupport(models.Model):
    _name = 'onsc.cv.type.support'
    _description = 'Tipo de apoyo'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del apoyo', required=True)
    active = fields.Boolean(string="Activo", default=True)
    see = fields.Boolean(string="Ver, ¿aún si usa anteojos o lentes?")
    hear = fields.Boolean(string="Oír, ¿aún si usa audífono?")
    walk = fields.Boolean(string="¿Caminar o subir escalones?")
    slide = fields.Boolean(string="¿Realizar tareas de cuidado personal como comer, bañarse o vestirse solo?")
    understand = fields.Boolean(string="Entender/ y o aprender?")
    interaction = fields.Boolean(string="¿Interacciones y/o relaciones interpersonales?")
    talk = fields.Boolean(string="Hablar o comunicarse aun usando lengua de señas")

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del tipo de apoyo debe ser único'),
    ]


class ONSCCVRollEvent(models.Model):
    _name = 'onsc.cv.roll.event'
    _description = 'Rol en evento'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del rol en el evento', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del rol en evento debe ser único'),
    ]
