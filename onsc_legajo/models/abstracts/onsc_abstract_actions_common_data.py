# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name


STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
]



class ONSCActionsCommonData(models.AbstractModel):
    _name = 'onsc.legajo.actions.common.data'
    _description = 'Modelo abstracto común para los datos de las acciones'


    reason_discharge = fields.Char(string='Descripción del motivo', copy=True)
    norm_code_discharge_id = fields.Many2one('onsc.legajo.norm', string='Tipo de norma', copy=True)
    norm_number_discharge = fields.Integer(string='Número de norma', related="norm_code_discharge_id.numeroNorma",
                                           store=True, readonly=True)
    norm_year_discharge = fields.Integer(string='Año de norma', related="norm_code_discharge_id.anioNorma", store=True,
                                         readonly=True)
    norm_article_discharge = fields.Integer(string='Artículo de norma', related="norm_code_discharge_id.articuloNorma",
                                            store=True, readonly=True)
    resolution_description_discharge = fields.Char(string='Descripción de la resolución', copy=True)
    resolution_date_discharge = fields.Date(string='Fecha de la resolución', copy=True)
    resolution_type_discharge = fields.Selection(
        [
            ('m', 'Inciso'),
            ('p', 'Presidencia o Poder ejecutivo'),
            ('u', 'Unidad ejecutora')
        ],
        copy=True,
        string='Tipo de resolución'
    )
    state = fields.Selection(STATES, string='Estado', default='borrador', copy=False)


    additional_information_discharge = fields.Text(string='Información adicional', copy=False)

