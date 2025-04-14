# -*- coding: utf-8 -*-

from odoo import fields, models

MOV = [
    ('alta', 'Alta'),
    ('baja', 'Baja'),
    ('comision_alta', 'Comisión Alta'),
    ('comision_baja', 'Comisión Baja'),
    ('cambio_dpto', 'Cambio departamento'),
    ('ascenso', 'Ascenso'),
    ('transforma', 'Transformación'),
    ('reestructura', 'Reestructura'),
    ('reserva', 'Reserva'),
    ('desreserva', 'Desreserva'),
    ('renovacion', 'Renovación'),
    ('correcion_ascenso', 'Correción ascenso'),
    ('correcion_alta', 'Correción alta'),
    ('correcion_baja', 'Correción baja'),
    ('cambio_jornada', 'Cambio Jornada'),
    ('modfu', 'Modificación funcionario'),
]


class ONSCLegajoPersonMovements(models.Model):
    _name = "onsc.legajo.person.movements"
    _description = "Movimientos para una persona"
    _order = "date_start"

    token = fields.Char(string='Token', index=True)
    report_user_id = fields.Integer(string='Usuario que dió origen al reporte', index=True)

    # CONTRACT INFO
    nro_doc = fields.Char(u'Número de documento')
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    department_id = fields.Many2one('hr.department', string="UO")
    contract_legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato')
    date_start = fields.Date(string=u'Fecha de alta')
    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?')
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión')
    date_end = fields.Date(string=u'Fecha de baja')
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen')
    operating_unit_origin_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora origen",

    )
    inciso_dest_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso destino',

    )
    operating_unit_dest_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora destino",

    )
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1', )
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')
    public_admin_entry_date = fields.Date(string=u'Fecha ingreso administración pública ')
    first_operating_unit_entry_date = fields.Date(string=u'Fecha de ingreso UE')
    date_end_commission = fields.Date(string=u'Fecha hasta de la comisión')
    reason_description = fields.Char(string='Motivo de alta')
    reason_deregistration = fields.Char(string='Motivo de baja')
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string="Causal de egreso")
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission",
                                               string="Motivo de extinción de la comisión")
    legajo_id = fields.Many2one('onsc.legajo', string="Funcionario")

    history_id = fields.Many2one('hr.contract.state.transaction.history', string="Transacción (PARA TEST)")
    transaction_date = fields.Date(string='Fecha de transacción (PARA TEST)')
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel de UO")
    date_start_commission = fields.Date(string=u'Fecha desde la comisión')
    origin_department_id = fields.Many2one('hr.department', string="UO Origen")
    target_department_id = fields.Many2one('hr.department', 'UO Destino')
    move_type = fields.Selection(MOV, string='Tipo de Movimiento')
    transaction_date = fields.Date(string='Fecha de transacción (PARA TEST)')


