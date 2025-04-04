# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api
from odoo.osv import expression


class ONSCLegajoChangeUO(models.Model):
    _name = "onsc.legajo.change.uo.movements"
    _description = "Cambios de UO"
    _auto = False
    _order = "employee_id"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            args = self._get_domain(args)
        return super(ONSCLegajoChangeUO, self.with_context(avoid_recursion=True))._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid
        )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            domain = self._get_domain(domain)
        result = super(ONSCLegajoChangeUO, self.with_context(avoid_recursion=True)).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
        )

        return result

    def _get_domain(self, args):
        is_consult_security = self.user_has_groups('onsc_legajo.group_legajo_report_change_uo_consult')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_change_uo_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_change_uo_ue')
        inciso_id = self._context.get('inciso_id', False)
        operating_unit_id = self._context.get('operating_unit_id', False)
        is_any_group = is_consult_security or is_inciso_security or is_ue_security
        is_any_hierarchy = inciso_id or operating_unit_id
        if not is_any_group or not is_any_hierarchy:
            return expression.AND([[(True, '=', False)], args])
        date_from = self._context.get('date_from', fields.Date.today())
        date_to = self._context.get('date_to', fields.Date.today())
        _domain = [
            ('from_date', '>=', date_from),
            ('from_date', '<=', date_to),
            ('department_id', '!=', False),
        ]
        if operating_unit_id:
            _domain = expression.AND([[('operating_unit_id', '=', operating_unit_id)], _domain])
        else:
            _domain = expression.AND([[('inciso_id', '=', inciso_id)], _domain])

        args = expression.AND([_domain, args])
        return args

    nro_doc = fields.Char(u'Número de documento', related='contract_id.nro_doc')
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    contract_legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato',
        compute='_compute_contract_legajo_state')
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    from_date = fields.Date(string=u'Fecha desde')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    department_id = fields.Many2one('hr.department', string="UO Origen")
    target_department_id = fields.Many2one('hr.department', 'UO Destino')
    security_job_id = fields.Many2one('onsc.legajo.security.job', string="Seguridad de puesto", )
    is_responsable_uo = fields.Boolean(string='¿Es responsable de UO?')

    def _compute_contract_legajo_state(self):
        ContractState = self.env['hr.contract.state.transaction.history'].suspend_security()
        for record in self:
            record.contract_legajo_state = ContractState.search_read(
                [("transaction_date", "=", record.from_date)],
                ["to_state"],
                limit=1,
                order="transaction_date DESC",
            )

    def init(self):

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT row_number() OVER () AS id,
	uo.employee_id, 
	uo.contract_id ,
	uo.job_id,
	uo.date_start AS from_date,
	uo.inciso_id,
	uo.operating_unit_id,
	uo.department_id AS target_department_id,
	uo.security_job_id,
	uo.is_responsable_uo, 
	(SELECT department_id FROM hr_job WHERE contract_id = contract.id AND start_date < uo.date_start 
	ORDER BY start_date DESC LIMIT 1) as department_id
FROM onsc_legajo_cambio_uo uo left join hr_contract contract ON contract.id = uo.contract_id
WHERE uo.state = 'confirmado' AND uo.department_id != 
	(SELECT department_id FROM hr_job WHERE contract_id = contract.id AND start_date < uo.date_start 
	ORDER BY start_date DESC LIMIT 1))''' % (self._table,))
