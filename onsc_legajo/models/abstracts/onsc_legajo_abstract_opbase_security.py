# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractOpBaseSecurity(models.AbstractModel):
    _name = 'onsc.legajo.abstract.opbase.security'
    _description = 'Modelo base para la seguridad de operaciones'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and not self._context.get('ignore_base_restrict'):
            args = self._get_domain(args)
        return super(ONSCLegajoAbstractOpBaseSecurity, self)._search(args, offset=offset, limit=limit, order=order,
                                                                     count=count,
                                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and not self._context.get('ignore_base_restrict'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def _get_domain(self, args, use_employee=False, user_partner=True):
        if use_employee:
            args = expression.AND([[
                ('employee_id', '!=', self.env.user.employee_id.id)
            ], args])
        elif user_partner:
            args = expression.AND([[
                ('partner_id', '!=', self.env.user.partner_id.id)
            ], args])
        if self._is_group_inciso_security():
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
        elif self._is_group_ue_security():
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    ('operating_unit_id', '=', operating_unit_id.id)
                ], args])
        return args

    def _is_group_inciso_security(self):
        return False

    def _is_group_ue_security(self):
        return False


class ONSCLegajoAbstractOpAddModifySecurity(models.AbstractModel):
    _name = 'onsc.legajo.abstract.opaddmodify.security'
    _description = 'Modelo base para la seguridad de operaciones: solamente gestión'

    def _default_inciso_id(self):
        return self.env.user.employee_id.job_id.contract_id.inciso_id.id

    def _default_operating_unit_id(self):
        return self.env.user.employee_id.job_id.contract_id.operating_unit_id.id

    inciso_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso',
        copy=False,
        default=_default_inciso_id,
        history=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora",
        copy=False,
        domain="[('inciso_id', '=', inciso_id)]",
        default=_default_operating_unit_id,
        history=True
    )
    is_user_admin = fields.Boolean(
        string="¿Es usuario admin?",
        compute='_compute_user_security_level', store=False)
    is_user_inciso = fields.Boolean(
        string="¿Es usuario Inciso?",
        compute='_compute_user_security_level', store=False)
    is_user_operating_unit = fields.Boolean(
        string="¿Es usuario UE?",
        compute='_compute_user_security_level', store=False)
    is_user_consulta = fields.Boolean(
        string="¿Es usuario Consulta?",
        compute='_compute_user_security_level', store=False)

    @api.depends('inciso_id', 'operating_unit_id')
    def _compute_user_security_level(self):
        _is_admin = self._is_group_admin_security()
        _is_inciso = self._is_group_inciso_security()
        _is_ue = self._is_group_ue_security()
        user_contract = self.env.user.employee_id.job_id.contract_id
        for rec in self:
            is_iam_inciso = rec.inciso_id and rec.inciso_id == user_contract.inciso_id
            is_iam_operating_unit = rec.operating_unit_id and rec.operating_unit_id == user_contract.operating_unit_id
            rec.is_user_admin = _is_admin
            rec.is_user_inciso = not rec.is_user_admin and _is_inciso and is_iam_inciso
            rec.is_user_operating_unit = not rec.is_user_admin and not rec.is_user_inciso and _is_ue and is_iam_operating_unit
            rec.is_user_consulta = not (rec.is_user_admin or rec.is_user_inciso or rec.is_user_operating_unit)

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        if self.operating_unit_id and self.operating_unit_id.inciso_id != self.inciso_id:
            self.operating_unit_id = False

    def _is_group_admin_security(self):
        return False

    def _is_group_inciso_security(self):
        return False

    def _is_group_ue_security(self):
        return False

    def _is_group_consulta_security(self):
        return False
