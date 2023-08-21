# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api
from odoo.osv import expression


class ONSCLegajoDepartment(models.Model):
    _name = "onsc.legajo.department"
    _description = "Legajo - UO"
    _auto = False

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCLegajoDepartment, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count,
                                                         access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def _is_group_responsable_uo_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo')

    def _get_domain(self, args):
        Legajo = self.env['onsc.legajo']
        not_abstract_security = not Legajo._get_abstract_inciso_security() and not Legajo._get_abstract_ue_security() and not Legajo._get_abstract_config_security()
        if not_abstract_security is False:
            legajos = Legajo.search([])
            args = expression.AND([[
                ('legajo_id', 'in', legajos.ids)
            ], args])
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            args = expression.AND([[
                ('department_id', 'in', department_ids)
            ], args])
        return args

    legajo_id = fields.Many2one('onsc.legajo', string="Legajo")
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado del funcionario',
    )
    contract_legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato')
    job_id = fields.Many2one('hr.job', string="Puesto")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    department_id = fields.Many2one('hr.department', string="UO")
    start_date = fields.Date(string='Fecha desde')
    end_date = fields.Date(string='Fecha hasta')
    type = fields.Selection(
        string='Tipo',
        selection=[('system', 'Sistema'),
                   ('joker', 'Comodity')],
        required=False, )

    is_job_open = fields.Boolean(string='¿Puesto vigente?', compute='_compute_is_job_open',
                                 search='_search_is_job_open')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT 
row_number() OVER (ORDER BY legajo_id, contract_id, type, job_id) AS id, * 
FROM
(SELECT
	contract.legajo_id,
	contract.id AS contract_id,
	legajo.legajo_state AS legajo_state,
	contract.legajo_state AS contract_legajo_state,
	job.id AS job_id,
	contract.inciso_id,
	contract.operating_unit_id,
	contract.employee_id,
	job.department_id,
	job.start_date AS start_date,
    job.end_date AS end_date,
	'system' AS type
FROM
	hr_contract contract
LEFT JOIN hr_job job ON job.contract_id = contract.id
LEFT JOIN onsc_legajo legajo ON contract.legajo_id = legajo.id
UNION ALL
SELECT
	legajo.id AS legajo_id,
	contract.id AS contract_id,
	legajo.legajo_state AS legajo_state,
	contract.legajo_state AS contract_legajo_state,
	NULL AS job_id,
	contract.inciso_id,
	contract.operating_unit_id,
	contract.employee_id,
	NULL AS department_id,
	NULL AS start_date,
    NULL AS end_date,
	'joker' AS type
FROM
	hr_contract contract
RIGHT JOIN onsc_legajo legajo ON contract.legajo_id = legajo.id
	) AS main_query
)''' % (self._table,))

    def _search_is_job_open(self, operator, value):
        system_records = self.search([('type', '=', 'system')])
        _today = fields.Date.today()
        open_system_records = system_records.filtered(
            lambda x: x.start_date and x.start_date <= _today and (x.end_date is False or x.end_date >= _today))

        joker_records = self.search([('type', '=', 'joker')])
        joker_valid_records = joker_records.filtered(lambda x: x.legajo_state == 'egresed')
        joker_valid_records |= joker_records.filtered(lambda x: x.legajo_state != 'egresed' and len(x.legajo_id.job_ids) == 0)

        if operator == '=' and value is False:
            _operator = 'not in'
        else:
            _operator = 'in'

        final_records = open_system_records
        final_records |= joker_valid_records
        return [('id', _operator, final_records.ids)]

    @api.depends('start_date', 'end_date')
    def _compute_is_job_open(self):
        _today = fields.Date.today()
        for record in self:
            record.is_job_open = record.start_date <= _today and (record.end_date is False or record.end_date >= _today)

    def get_uo_tree(self, contract=False):
        Department = self.env['hr.department'].sudo()
        department_ids = []
        if self.user_has_groups('onsc_legajo.group_legajo_hr_inciso,onsc_legajo.group_legajo_hr_ue'):
            contract_id = contract or self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            args = []
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    ('operating_unit_id', '=', operating_unit_id.id)
                ], args])
            department_ids = Department.search(args).ids
        elif self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo'):
            department_id = self.env.user.employee_id.job_id.department_id.id
            department_ids = Department.search(['|', ('id', 'child_of', department_id),
                                                ('id', '=', department_id)]).ids
        return department_ids

    def button_open_legajo(self):
        ctx = self.env.context.copy()
        ctx.update({'edit': False})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'onsc.legajo',
            'name': 'Editar puesto',
            'context': ctx,
            "target": "current",
            "res_id": self.legajo_id.id,
        }
