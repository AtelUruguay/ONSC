# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCCVDigitalVacante(models.Model):
    _name = 'onsc.cv.digital.vacante'
    _description = 'Vacantes'
    _rec_name = 'nroPuesto'

    selected = fields.Boolean()
    nroPuesto = fields.Char(string="Puesto")
    nroPlaza = fields.Char(string="Plaza")
    estado = fields.Char(string="Estado")
    estadoDescripcion = fields.Char(string="Estado")
    situacionDeCobertura = fields.Char(string="Cobertura")
    situacionDeCoberturaDescripcion = fields.Char(string="Cobertura")
    fechaReserva = fields.Date(string="Fecha Reserva")
    fechaNotificacion = fields.Date(string="Fecha Notificación")
    fechaVacantePLaza = fields.Date(string="Fecha Vacante Plaza")
    codPartida = fields.Char(string="Código Partida")
    Dsc3Id = fields.Char(string="Código Descriptor 3")
    Dsc3Descripcion = fields.Char(string="Descriptor 3")
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3', compute="_compute_descriptor3", store=True)
    Dsc4Id = fields.Char(string="Código Descriptor 4")
    Dsc4Descripcion = fields.Char(string="Descriptor 4")
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4', compute="_compute_descriptor4", store=True)
    codRegimen = fields.Char(string="Código Régimen")
    descripcionRegimen = fields.Char(string="Descripción Régimen")
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', compute="_compute_regime", store=True)
    codigoJornadaFormal = fields.Integer(string="Código Jornada Formal")
    descripcionJornadaFormal = fields.Char(string="Jornada Formal")
    alta_vl_id = fields.Many2one('onsc.legajo.alta.vl', 'vacante_id')

    @api.depends('codRegimen')
    def _compute_regime(self):
        for rec in self:
            if rec.codRegimen:
                rec.regime_id = self.env['onsc.legajo.regime'].search([('codRegimen', '=', rec.codRegimen)], limit=1)
            else:
                rec.regime_id = False

    @api.depends('Dsc3Id')
    def _compute_descriptor3(self):
        for rec in self:
            if rec.Dsc3Id:
                descriptor3_id = self.env['onsc.catalog.descriptor3'].search([('code', '=', rec.Dsc3Id)], limit=1)
                rec.descriptor3_id = descriptor3_id.id if descriptor3_id else False

            else:
                rec.descriptor3_id = False

    @api.depends('Dsc4Id')
    def _compute_descriptor4(self):
        for rec in self:
            if rec.Dsc4Id:
                descriptor4_id = self.env['onsc.catalog.descriptor4'].search([('code', '=', rec.Dsc4Id)], limit=1)
                rec.descriptor4_id = descriptor4_id.id if descriptor4_id else False
            else:
                rec.descriptor4_id = False

    def write(self, vals):
        result = super(ONSCCVDigitalVacante, self).write(vals)
        for rec in self.filtered(lambda x: x.selected):
            rec.alta_vl_id.write({
                'nroPuesto': rec.nroPuesto,
                'nroPlaza': rec.nroPlaza,
                'descriptor3_id': rec.descriptor3_id.id,
                'descriptor4_id': rec.descriptor4_id.id,
                'regime_id': rec.regime_id.id,
            })
        return result
