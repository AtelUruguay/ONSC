# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoOffice(models.Model):
    _name = 'onsc.legajo.office'
    _description = 'Oficina'
    _rec_name = 'code'

    code = fields.Char(string="Código", required=True)
    inciso = fields.Many2one("onsc.catalog.inciso", string="Inciso", required=True)
    unidadEjecutora = fields.Many2one("operating.unit", string="Unidad ejecutora", required=True)
    programa = fields.Char(string="Código del programa")
    programaDescripcion = fields.Char(string="Descripción del programa")
    proyecto = fields.Char(string="Código del proyecto")
    proyectoDescripcion = fields.Char(string="Descripción del proyecto")

    jornada_retributiva_ids = fields.One2many("onsc.legajo.jornada.retributiva",
                                              inverse_name="office_id",
                                              string="Jornadas retributivas")

    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código de la oficina debe ser único')
    ]

    def syncronize(self):
        return True


class ONSCLegajoJornadaRetributiva(models.Model):
    _name = 'onsc.legajo.jornada.retributiva'
    _description = 'Jornada retributiva'
    _rec_name = 'codigoJornada'

    office_id = fields.Many2one("onsc.legajo.office", string="Oficina", required=True, ondelete='cascade')
    codigoJornada = fields.Char(string="Código de la jornada", required=True)
    descripcionJornada = fields.Char(string="Descripción de la Jornada", required=True)

    _sql_constraints = [
        ('codigoJornada_uniq', 'unique("codigoJornada")',
         u'El código de la jornada retributiva debe ser único por oficina')
    ]
