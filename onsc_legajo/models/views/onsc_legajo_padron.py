# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCLegajoPadron(models.Model):
    _name = "onsc.legajo.padron"
    _description = "Legajo - Padrón"
    _order = "legajo_id"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoPadron, self).fields_get(allfields, attributes)
        hide = [
            'end_date',
            'employee_id',
            'job_id',
            'type',
            'active_job_qty',
            'job_end_date',
            'token',
            'report_user_id',
            'create_uid',
            'write_uid',
            'create_date',
            'write_date',
            'legajo_state',
            'level_0',
            'level_1',
            'level_2',
            'level_3',
            'level_4',
            'level_5',
        ]
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    # CONTRACT INFO
    token = fields.Char(string='Token', index=True)
    report_user_id = fields.Integer(string='Usuario que dió origen al reporte', index=True)

    legajo_id = fields.Many2one('onsc.legajo', string="Funcionario")
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    type = fields.Selection(string='Tipo', selection=[('active', 'Activo'), ('egresed', 'Egresado')])
    nro_doc = fields.Char(u'Número de documento')
    public_admin_entry_date = fields.Date(string=u'Fecha de ingreso AP')
    first_operating_unit_entry_date = fields.Date(string=u'Fecha de ingreso UE')

    # CONTRACT COMPUTED INFO
    contract_legajo_state = fields.Selection(
        [
            ('active', 'Activo'),
            ('baja', 'Baja'),
            ('reserved', 'Reservado'),
            ('outgoing_commission', 'Comisión saliente'),
            ('incoming_commission', 'Comisión entrante'),
        ],
        string='Estado del contrato'
    )
    job_id = fields.Many2one('hr.job', string="Puesto")
    job_name = fields.Char(string='Nombre del puesto')
    security_job_id = fields.Many2one('onsc.legajo.security.job', string="Seguridad de puesto")
    department_id = fields.Many2one('hr.department', string="UO")
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel jerárquico")
    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?')

    job_start_date = fields.Date(string='Fecha desde')
    job_end_date = fields.Date(string='Fecha hasta')
    # CONTRACT COMPUTED INFO - HISTORICAL DATA
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')

    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión')
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
    date_start = fields.Date(string=u'Fecha de alta')
    date_end = fields.Date(string=u'Fecha de baja')
    date_end_commission = fields.Date(string=u'Fecha hasta de la comisión')
    reason_description = fields.Char(string='Motivo de alta')
    reason_deregistration = fields.Char(string='Motivo de baja')
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string="Causal de egreso")
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission", string="Motivo de extinción de la comisión")
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones')

    # JOB COMPUTED INFO
    # organigram_joker = fields.Many2one('hr.department', string='Organigrama')
    level_0 = fields.Many2one('hr.department', string='Nivel 0')
    level_1 = fields.Many2one('hr.department', string='Nivel 1')
    level_2 = fields.Many2one('hr.department', string='Nivel 2')
    level_3 = fields.Many2one('hr.department', string='Nivel 3')
    level_4 = fields.Many2one('hr.department', string='Nivel 4')
    level_5 = fields.Many2one('hr.department', string='Nivel 5')
