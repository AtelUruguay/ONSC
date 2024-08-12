# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCLegajoCausesDischarge(models.Model):
    _name = 'onsc.legajo.causes.discharge'
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
    inciso_ids = fields.Many2many('onsc.catalog.inciso', string='Incisos')
    is_require_extended = fields.Boolean(u"¿Requiere extendido?")
    causes_discharge_line_ids = fields.One2many("onsc.legajo.causes.discharge.line", "causes_discharge_id",
                                                string="Motivos de causal de egreso extendido")
    reason_description = fields.Char(string='Descripción del motivo')
    resolution_description = fields.Char(string='Descripción de la resolución')
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma')
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código del causal de egreso debe ser único'),
        ('name_uniq', 'unique(name)', u'El nombre del causal de egreso debe ser único'),
    ]

    @api.constrains("reason_description", "resolution_description")
    def _check_len_description(self):
        for record in self:
            if record.reason_description and len(record.reason_description) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.resolution_description and len(record.resolution_description) > 100:
                raise ValidationError(_("El campo Descripción de la resolución no puede tener más de 100 caracteres."))

    @api.onchange('is_require_extended')
    def onchange_require_extended(self):
        if not self.is_require_extended:
            self.causes_discharge_line_ids = [(5, 0, 0)]
        else:
            self.reason_description = False
            self.resolution_description = False
            self.norm_id = False

    @api.onchange('is_by_inciso')
    def onchange_is_by_inciso(self):
        if not self.is_by_inciso:
            self.inciso_ids = [(5, 0, 0)]


class ONSCLegajoCausesDischargeLine(models.Model):
    _name = 'onsc.legajo.causes.discharge.line'
    _description = 'Causal de egreso Linea'
    _rec_name = 'description'

    name = fields.Char("Código", required=True)
    description = fields.Char(u"Descripción", required=True)
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge",
                                          string="Causal de egreso",
                                          ondelete='cascade')
    reason_description = fields.Char(string='Descripción del motivo')
    resolution_description = fields.Char(string='Descripción de la resolución')
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma')

    @api.constrains("reason_description", "resolution_description")
    def _check_len_description(self):
        for record in self:
            if record.reason_description and len(record.reason_description) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.resolution_description and len(record.resolution_description) > 100:
                raise ValidationError(_("El campo Descripción de la resolución no puede tener más de 100 caracteres."))
