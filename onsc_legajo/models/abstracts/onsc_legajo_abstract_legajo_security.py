# -*- coding: utf-8 -*-

from odoo import models, api

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
            if inciso_id:
                available_contracts = employees.mapped('contract_ids').filtered(
                    lambda x: x.inciso_id.id == inciso_id and x.legajo_state in ['active', 'outgoing_commission',
                                                                                 'incoming_commission'])
        elif self._get_abstract_ue_security():
            contract = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract.operating_unit_id.id
            if operating_unit_id:
                available_contracts = employees.mapped('contract_ids').filtered(
                    lambda x: x.operating_unit_id.id == operating_unit_id and x.legajo_state in ['active',
                                                                                                 'outgoing_commission',
                                                                                                 'incoming_commission'])
        return available_contracts
