# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class ONSCLegajoCommissionRegime(models.Model):
    _name = 'onsc.legajo.commission.regime'
    _description = 'Régimen comisión'

    name = fields.Char(string='Descripción', required=True)
    code = fields.Char(string='Código', required=True)
    cgn_code = fields.Char(string='Código CGN')
    start_date = fields.Date(string='Fecha desde')
    end_date = fields.Date(string='Fecha hasta')
    date_change = fields.Date(string='Fecha de cambio')
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código del régimen comisión debe ser único'),
        ('name_uniq', 'unique(name)',
         u'La descripción del régimen comisión debe ser única'),
    ]

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
