# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCOrganizationalWizard(models.TransientModel):
    _name = 'onsc.organizational.wizard'
    _description = 'Asistente de organigrama'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso',
                                required=True, history=True)
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        ondelete='restrict',
                                        tracking=True, history=True)
    department_id = fields.Many2one(
        "hr.department",
        string="Unidad organizativa",
        tracking=True,
        history=True
    )
    short_name = fields.Boolean(
        'Nombres Cortos'
    )
    responsible = fields.Boolean(
        'Visualizar Responsable UO'
    )

    def action_show_org(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'organization_dashboard',
            'params': {
                'operating_unit_id': self.operating_unit_id.id,
                'department_id': self.department_id.id,
                'short_name': self.short_name,
                'responsible': self.responsible,
            },
        }
