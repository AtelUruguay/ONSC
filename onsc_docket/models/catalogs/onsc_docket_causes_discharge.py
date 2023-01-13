# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCDocketCausesDischarge(models.Model):
    _name = 'onsc.docket.causes.discharge'
    _description = 'Causal de egreso'

    name = fields.Char("Nombre del causal de egreso", required=True)
    code = fields.Char(u"Código", required=True)
    code_bps = fields.Char(u"Código BPS")
    description_bps = fields.Char(u"Descripción BPS")
    code_cgn = fields.Char(u"Código CGN")
    description_cgn = fields.Char(u"Descripción CGN")
    code_rve = fields.Char(u"Código RVE")
    description_rve = fields.Char(u"Descripción RVE")
    is_by_inciso = fields.Boolean(u"Por inciso")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    is_require_extended = fields.Boolean(u"¿Requiere extendido?")
    causes_discharge_line_ids = fields.One2many("onsc.docket.causes.discharge.line", "causes_discharge_id",
                                                string="Motivos de causal de egreso extendido")
    active = fields.Boolean('Active', default=True)

    @api.onchange('is_require_extended')
    def onchange_require_extended(self):
        if not self.is_require_extended:
            self.causes_discharge_line_ids = [(5, 0, 0)]

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código del causal de egreso debe ser único'),
        ('name_uniq', 'unique(name)', u'El nombre del causal de egreso debe ser único'),
    ]


class ONSCDocketCausesDischargeLine(models.Model):
    _name = 'onsc.docket.causes.discharge.line'
    _description = 'Causal de egreso Linea'

    name = fields.Char("Nombre", required=True)
    description = fields.Char(u"Descripción", required=True)
    causes_discharge_id = fields.Many2one("onsc.docket.causes.discharge", string="Causal de egreso")
