# -*- coding: utf-8 -*-

from odoo import fields, models

MOV = [
    ('ASCENSO', 'Ascenso'),
    ('TRANSFORMA', 'Transformación'),
    ('REESTRUCTURA', 'Reestructura'),
    ('RESERVA', 'Reserva'),
    ('DESRESERVA', 'Desreserva'),
    ('RENOVACION', 'Renovación'),
    ('TRANSFORMA_REDUE', 'Transformación')
]


class ONSCLegajoPersonMovements(models.Model):
    _name = "onsc.legajo.other.movements"
    _description = "Otros movimientos de la UE/Inciso"

    token = fields.Char(string='Token', index=True)
    report_user_id = fields.Integer(string='Usuario que dió origen al reporte', index=True)

    # CONTRACT INFO
    nro_doc = fields.Char(u'Número de documento')
    employee = fields.Char(string="Funcionario")
    move_type = fields.Selection(MOV, string='Tipo de Movimiento')
    audit_date = fields.Date(string=u'Fecha de auditoría')
    from_date = fields.Date(string=u'Fecha desde del movimiento')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    department_id = fields.Many2one('hr.department', string="UO")
    puesto_plaza = fields.Char(string='Puesto - Plaza - Sec plaza')

    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1', )
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')
    public_admin_entry_date = fields.Date(string=u'Fecha ingreso administración pública ')
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva')
    graduation_date = fields.Date(string='Fecha de graduación')
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil")
    operating_unit_origin_id = fields.Many2one(
        "operating.unit",
        string="UE anterior",

    )
    puesto_plaza_origin = fields.Char(string='Puesto - Plaza - Sec plaza anterior')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen anterior')
    descriptor1_origin_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1 anterior')
    descriptor2_origin_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2 anterior')
    descriptor3_origin_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3 anterior')
    descriptor4_origin_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4 anterior')
