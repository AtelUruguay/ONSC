# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('communication_error', 'Error de comunicación'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
    ('confirmado', 'Confirmado'),
]


class ONSCActionsCommonData(models.AbstractModel):
    _name = 'onsc.legajo.actions.common.data'
    _description = 'Modelo abstracto común para los datos de las acciones'

    partner_id = fields.Many2one("res.partner", string="Contacto")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)
    reason_description = fields.Char(string='Descripción del motivo', copy=True)

    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma', copy=True)
    norm_id_domain = fields.Char(compute='_compute_norm_id_domain')
    norm_type = fields.Char(string='Tipo de norma', related="norm_id.tipoNorma",
                            store=True, readonly=True)
    norm_number = fields.Integer(string='Número de norma', related="norm_id.numeroNorma",
                                 store=True, readonly=True)
    norm_year = fields.Integer(string='Año de norma', related="norm_id.anioNorma", store=True,
                               readonly=True)
    norm_article = fields.Integer(string='Artículo de norma', related="norm_id.articuloNorma",
                                  store=True, readonly=True)
    resolution_description = fields.Char(string='Descripción de la resolución', copy=True)
    resolution_date = fields.Date(string='Fecha de la resolución', copy=True)
    resolution_type = fields.Selection(
        [
            ('M', 'Inciso'),
            ('P', 'Presidencia o Poder ejecutivo'),
            ('U', 'Unidad ejecutora')
        ],
        copy=True,
        string='Tipo de resolución'
    )
    state = fields.Selection(STATES, string='Estado', default='borrador', copy=False, tracking=True)
    additional_information = fields.Text(string='Información adicional', copy=False)

    is_error_synchronization = fields.Boolean(string="Error en la sincronización (interno)", copy=False)
    error_message_synchronization = fields.Char(string="Mensaje de Error", copy=False)
    is_communicaton_error = fields.Boolean(string="Error de comunicación", copy=False)

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['borrador', 'error_sgh']

    @api.depends('inciso_id')
    def _compute_norm_id_domain(self):
        for rec in self:
            rec.norm_id_domain = json.dumps([('inciso_ids', 'in', [rec.inciso_id.id])])

    @api.constrains("reason_description", "resolution_description")
    def _check_len_description(self):
        for record in self:
            if record.reason_description and len(record.reason_description) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.resolution_description and len(record.resolution_description) > 100:
                raise ValidationError(_("El campo Descripción de la resolución no puede tener más de 100 caracteres."))

    @api.onchange('inciso_id')
    def onchange_component_inciso_id(self):
        self.norm_id = False
