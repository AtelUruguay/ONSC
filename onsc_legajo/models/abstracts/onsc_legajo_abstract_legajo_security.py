# -*- coding: utf-8 -*-

from odoo import models, api

from odoo.osv import expression


class ONSCLegajoAbstractLegajoSecurity(models.AbstractModel):
    _name = 'onsc.legajo.abstract.legajo.security'
    _description = 'Modelo abstracto para la seguridad'

    @api.model
    def _get_expression_domain(self, args):
        available_contracts = self._get_user_available_contract()
        sql_query = """SELECT DISTINCT employee_id FROM hr_contract WHERE id IN %s AND employee_id IS NOT NULL"""
        self.env.cr.execute(sql_query, [tuple(available_contracts.ids)])
        results = self.env.cr.fetchall()
        employee_ids = [item[0] for item in results]
        args = expression.AND([[
            ('employee_id', 'in', employee_ids)
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
            # employees = self.env.user.employee_id
            base_employee_domain = [('id', '=', self.env.user.employee_id.id)]
            employee_domain = [('employee_id', '=', self.env.user.employee_id.id)]
        elif employee_id:
            # employees = employee_id
            base_employee_domain = [('id', '=', employee_id.id)]
            employee_domain = [('employee_id', '=', employee_id.id)]
        else:
            # employees = self.env['hr.employee'].search([('id', '!=', self.env.user.employee_id.id)])
            base_employee_domain = [('id', '!=', self.env.user.employee_id.id)]
            employee_domain = [('employee_id', '!=', self.env.user.employee_id.id)]

        if self._context.get('mi_legajo'):
            available_contracts = self.env['hr.contract'].search(employee_domain)
            # available_contracts = employees.mapped('contract_ids')
        elif self._get_abstract_config_security():
            available_contracts = self.env['hr.contract'].search(employee_domain)
            # available_contracts = employees.mapped('contract_ids')
        elif self._get_abstract_inciso_security():
            contract = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract.inciso_id.id
            available_contracts = self._get_available_contracts(
                employee_domain,
                base_employee_domain,
                inciso_id,
                'inciso_id'
            )
        elif self._get_abstract_ue_security():
            contract = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract.operating_unit_id.id
            if operating_unit_id:
                available_contracts = self._get_available_contracts(
                    employee_domain,
                    base_employee_domain,
                    operating_unit_id,
                    'operating_unit_id'
                )
        elif self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo'):
            department_ids = self.env['onsc.legajo.department'].get_uo_tree()
            available_jobs_domain = expression.AND([[('department_id', 'in', department_ids)], employee_domain])
            available_contracts = self.env['hr.job'].search(available_jobs_domain).mapped('contract_id')
            # available_contracts = employees.mapped('contract_ids').mapped('job_ids').filtered(
            #     lambda x: x.department_id.id in department_ids).mapped('contract_id')
        return available_contracts

    def _get_available_contracts(self, employee_domain, base_employee_domain, security_hierarchy_value, security_hierarchy_level):
        # LEGAJOS VIGENTES
        if self._context.get('only_active_contracts'):
            base_args = [
                (security_hierarchy_level, '=', security_hierarchy_value),
                # ('employee_id', 'in', employees.ids),
                ('legajo_state', 'in', ['active']),
            ]
        else:
            base_args = [
                (security_hierarchy_level, '=', security_hierarchy_value),
                # ('employee_id', 'in', employees.ids),
                ('legajo_state', 'not in', ['baja']),
            ]
        contract_domain = expression.AND([base_args, employee_domain])
        available_contracts = self.env['hr.contract'].search(contract_domain)
        available_contracts_employees_ids = available_contracts.mapped('employee_id').ids

        # NO VIGENTES

        second_employee_domain = expression.AND(
            [[('id', 'not in', available_contracts_employees_ids)], base_employee_domain])
        employees = self.env['hr.employee'].search(second_employee_domain)
        # TODO: filtrar partner is_legajo activado
        for employee in employees:
            employee_contracts = employee.contract_ids
            is_any_active_contract = len(employee_contracts.filtered(
                lambda x: x.legajo_state not in ['baja'] or x.legajo_state == 'baja' and not x.date_end)) > 0
            if is_any_active_contract:
                continue
            last_baja_contract = employee_contracts.sorted(key=lambda x: x.date_end, reverse=True)
            if last_baja_contract and eval(
                    'last_baja_contract[0].%s.id == %s' % (security_hierarchy_level, security_hierarchy_value)):
                available_contracts |= last_baja_contract[0]
        return available_contracts
