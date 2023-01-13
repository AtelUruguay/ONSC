# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCOrganizationalWizard(models.TransientModel):
    _name = 'onsc.organizational.wizard'
    _description = 'Asistente de organigrama'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True)
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        ondelete='restrict')
    department_id = fields.Many2one(
        "hr.department",
        string="Unidad organizativa"
    )
    short_name = fields.Boolean(
        'Nombres Cortos'
    )
    responsible = fields.Boolean(
        'Visualizar Responsable UO'
    )
    date = fields.Date('Fecha', required=True, default=lambda *a: fields.Date.today())

    @api.onchange('date')
    def onchange_date(self):
        self.inciso_id = False

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        self.operating_unit_id = False

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        self.department_id = False

    def action_show_org(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'organization_dashboard',
            'params': {
                'operating_unit_id': self.operating_unit_id.id,
                'department_id': self.department_id.id,
                'short_name': self.short_name,
                'responsible': self.responsible,
                'end_date': self.date,
                'inciso': self.inciso_id.name or '',
                'ue': self.operating_unit_id.name or '',
            },
        }
