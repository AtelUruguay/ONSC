# -*- coding: utf-8 -*-

from odoo import models, api

from odoo.osv import expression


class ONSCLegajoAbstractLegajoSecurity(models.AbstractModel):
    _name = 'onsc.legajo.abstract.legajo.security'
    _description = 'Modelo abstracto para la seguridad'

    @api.model
    def _get_expression_domain(self, args, config_use_only_active=False):
        if self._context.get('is_legajo') and not self._context.get('ignore_restrict'):
            available_contracts = self._get_user_available_contract(config_use_only_active=config_use_only_active)
            if not available_contracts:
                employee_ids = []
            else:
                sql_query = """SELECT DISTINCT employee_id FROM hr_contract WHERE id IN %s AND employee_id IS NOT NULL"""
                self.env.cr.execute(sql_query, [tuple(available_contracts.ids)])
                results = self.env.cr.fetchall()
                employee_ids = [item[0] for item in results]
            return expression.AND([[('employee_id', 'in', employee_ids)], args])
        else:
            return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_legajo') and not self._context.get('ignore_restrict'):
            args = self._get_expression_domain(args)
        return super(ONSCLegajoAbstractLegajoSecurity, self)._search(args, offset=offset, limit=limit, order=order,
                                                                     count=count,
                                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_legajo') and not self._context.get('ignore_restrict'):
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

    def _get_abstract_responsable_uo(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo')

    def _get_user_available_contract(self, employee_id=False, config_use_only_active=False):
        available_contracts = self.env['hr.contract']
        if self._context.get('mi_legajo'):
            base_employee_domain = [('id', '=', self.env.user.employee_id.id)]
            employee_domain = [('employee_id', '=', self.env.user.employee_id.id)]
        elif employee_id:
            base_employee_domain = [('id', '=', employee_id.id)]
            employee_domain = [('employee_id', '=', employee_id.id)]
        else:
            base_employee_domain = [('id', '!=', self.env.user.employee_id.id)]
            employee_domain = [('employee_id', '!=', self.env.user.employee_id.id)]
        if self._context.get('mi_legajo'):
            available_contracts = self.env['hr.contract'].sudo().search(employee_domain)
        elif self._get_abstract_config_security():
            if config_use_only_active:
                employee_domain = expression.AND([[('legajo_state', '=', 'active')], employee_domain])
            available_contracts = self.env['hr.contract'].sudo().search(employee_domain)
        elif self._get_abstract_inciso_security():
            contract = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract.inciso_id.id
            available_contracts = self._get_available_contracts(
                base_employee_domain,
                employee_domain,
                inciso_id,
                'inciso_id'
            )
        elif self._get_abstract_ue_security():
            contract = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract.operating_unit_id.id
            if operating_unit_id:
                available_contracts = self._get_available_contracts(
                    base_employee_domain,
                    employee_domain,
                    operating_unit_id,
                    'operating_unit_id'
                )
        elif self._get_abstract_responsable_uo():
            employees = employee_id or self.env['hr.employee'].search([('id', '!=', self.env.user.employee_id.id)])
            department_ids = self.env['onsc.legajo.department'].get_uo_tree()
            available_contracts = employees.mapped('contract_ids').mapped('job_ids').filtered(
                lambda x: x.department_id.id in department_ids).mapped('contract_id')
        return available_contracts

    def _get_available_contracts(
            self,
            base_employee_domain,
            employee_domain,
            security_hierarchy_value,
            security_hierarchy_level
    ):
        base_args = employee_domain
        # LEGAJOS VIGENTES
        if self._context.get('only_active_contracts'):
            base_args = expression.AND([[
                (security_hierarchy_level, '=', security_hierarchy_value),
                ('legajo_state', 'in', ['active'])],
                base_args])
        else:
            base_args = expression.AND([[
                (security_hierarchy_level, '=', security_hierarchy_value),
                ('legajo_state', 'not in', ['baja'])],
                base_args])
        available_contracts = self.env['hr.contract'].search(base_args)

        if not available_contracts:
            available_contracts_employees_ids = []
        else:
            sql_query = """SELECT DISTINCT employee_id FROM hr_contract WHERE id IN %s AND employee_id IS NOT NULL"""
            self.env.cr.execute(sql_query, [tuple(available_contracts.ids)])
            results = self.env.cr.fetchall()
            available_contracts_employees_ids = [item[0] for item in results]
        # NO VIGENTES
        # TODO: filtrar partner is_legajo activado

        base_employee_domain = expression.AND([
            [('id', 'not in', available_contracts_employees_ids),
             ('legajo_state', '=', 'egresed')],
            base_employee_domain])
        employees = self.env['hr.employee'].search(base_employee_domain)
        for employee in employees:
            employee_contracts = employee.contract_ids
            last_baja_contract = employee_contracts.sorted(key=lambda x: x.date_end, reverse=True)
            if last_baja_contract and eval(
                    'last_baja_contract[0].%s.id == %s' % (security_hierarchy_level, security_hierarchy_value)):
                available_contracts |= last_baja_contract[0]
        return available_contracts
