# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class ONSCLegajoIncomeMechanism(models.Model):
    _name = 'onsc.legajo.income.mechanism'
    _description = 'Mecanismo de ingreso'

    code = fields.Char(u"Código", required=True)
    name = fields.Char("Nombre del mecanismo de ingreso", required=True)
    start_date = fields.Date(string="Fecha desde")
    end_date = fields.Date(string="Fecha hasta")
    change_date = fields.Date(string="Fecha de cambio")
    is_call_number_required = fields.Boolean(string="¿Requiere número de llamado?")
    active = fields.Boolean('Activo', default=True)

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde"))

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código del mecanismo de ingreso debe ser único'),
        ('name_uniq', 'unique(name)', u'El nombre del mecanismo de ingreso debe ser único'),
    ]
