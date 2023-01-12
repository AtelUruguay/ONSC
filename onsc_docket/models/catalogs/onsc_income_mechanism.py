# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning


class ONSCDocketIncomeMechanism(models.Model):
    _name = 'onsc.docket.income.mechanism'
    _description = 'Mecanismos de Ingreso'

    code = fields.Char(u"Código", required=True)
    name = fields.Char("Nombre del mecanismos de ingreso", required=True)
    start_date = fields.Date(string="Fecha desde")
    end_date = fields.Date(string="Fecha hasta")
    change_date = fields.Date(string="Fecha de cambio")
    is_call_number_required = fields.Boolean(string="¿Requiere número de llamado?", default=False)

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.start_date > fields.Date.today():
            self.start_date = False
            return cv_warning(_(u"La fecha desde debe ser menor que la fecha hasta"))
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return cv_warning(_(u"La fecha de desde no puede ser mayor que la fecha de hasta"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.end_date > fields.Date.today():
            self.end_date = False
            return cv_warning(_(u"La fecha de hasta debe ser menor que la fecha desde"))
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return cv_warning(_(u"La fecha de hasta no puede ser menor que la fecha de desde"))


    _sql_constraints = [
            ('code_uniq', 'unique(code)', u'El código del mecanismos de ingreso debe ser único'),
            ('name_uniq', 'unique(name)', u'El nombre del mecanismos de ingreso debe ser único'),
        ]


