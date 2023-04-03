# -*- coding: utf-8 -*-

from odoo import models, api, fields

from odoo.osv import expression


class ONSCLegajoAbstractLegajoSecurity(models.AbstractModel):
    _name = 'onsc.legajo.abstract.legajo.security'
    _description = 'Modelo abstracto para la seguridad'

    @api.model
    def _get_expression_domain(self, args):
        available_contracts = self._get_user_available_contract()
        args = expression.AND([[
            ('employee_id', 'in', available_contracts.mapped('employee_id').ids)
        ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_legajo'):
            args = self._get_expression_domain(args)
        return super(ONSCLegajoAbstractLegajoSecurity, self)._search(args, offset=offset, limit=limit, order=order,
                                                                     count=count,
                                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_legajo'):
            domain = self._get_expression_domain(domain)
        return super(ONSCLegajoAbstractLegajoSecurity, self).read_group(domain, fields, groupby, offset=offset,
                                                                        limit=limit, orderby=orderby,
                                                                        lazy=lazy)

    def _get_abstract_config_security(self):
        return False

    def _get_abstract_inciso_security(self):
        return False

    def _get_abstract_ue_security(self):
        return False

    def _get_user_available_contract(self, employee_id=False):
        available_contracts = self.env['hr.contract']
        if self._context.get('mi_legajo'):
            employees = self.env.user.employee_id
        else:
            employees = employee_id or self.env['hr.employee'].search([])
        if self._context.get('mi_legajo'):
            available_contracts = employees.mapped('contract_ids').filtered(
                lambda x: x.legajo_state in ['active', 'outgoing_commission', 'incoming_commission'])
        elif self._get_abstract_config_security():
            available_contracts = employees.mapped('contract_ids')
        elif self._get_abstract_inciso_security():
            contract = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract.inciso_id.id
            available_contracts = self._get_available_contracts(employees, inciso_id, 'inciso_id')
        elif self._get_abstract_ue_security():
            contract = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract.operating_unit_id.id
            if operating_unit_id:
                available_contracts = self._get_available_contracts(employees, operating_unit_id, 'operating_unit_id')
        return available_contracts

    def _get_available_contracts(self, employees, security_hierarchy_value, security_hierarchy_level):
        if self._context.get('only_active_contracts'):
            base_args = [
                (security_hierarchy_level, '=', security_hierarchy_value),
                ('employee_id', 'in', employees.ids),
                ('legajo_state', 'in', ['active']),
            ]
        else:
            base_args = [
                (security_hierarchy_level, '=', security_hierarchy_value),
                ('employee_id', 'in', employees.ids),
                '|','|',
                ('legajo_state', 'in', ['active']),
                '&', ('legajo_state', '=', 'incoming_commission'),'|',('date_end', '=', False),('date_end', '>', fields.Date.today()),
                '&', ('legajo_state', '=', 'outgoing_commission'),('inciso_id.is_central_administration', '=', True)
            ]
        available_contracts = self.env['hr.contract'].search(base_args)
        available_contracts_employees = available_contracts.mapped('employee_id')
        for employee in employees.filtered(
                lambda x: x.id not in available_contracts_employees.ids and len(x.contract_ids)):
            last_baja_contract = employee.contract_ids.filtered(lambda x: x.legajo_state == 'baja')
            if last_baja_contract:
                last_baja_contract = last_baja_contract.sorted(key=lambda x: x.date_end, reverse=True)[0]
            is_any_active_contract = len(employee.contract_ids.filtered(
                lambda x: x.legajo_state in ['active', 'outgoing_commission', 'incoming_commission'])) > 0
            if not is_any_active_contract and eval('last_baja_contract.%s.id == %s' % (security_hierarchy_level, security_hierarchy_value)):
                available_contracts |= last_baja_contract
        return available_contracts