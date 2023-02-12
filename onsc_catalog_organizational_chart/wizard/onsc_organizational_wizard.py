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
        inciso_withhistory = self.inciso_id.with_context(find_history=True, as_of_date=self.date)
        operating_unit_withhistory = self.operating_unit_id.with_context(find_history=True, as_of_date=self.date)
        if inciso_withhistory:
            inciso_name = inciso_withhistory.name_get()[0][1]
        else:
            inciso_name = self.inciso_id.name
        if operating_unit_withhistory:
            operating_unit_name = operating_unit_withhistory.name_search(
                args=[('id', '=', operating_unit_withhistory.id)])[0][1]
        else:
            operating_unit_name = self.operating_unit_id.name

        return {
            'type': 'ir.actions.client',
            'tag': 'organization_dashboard',
            'params': {
                'title': 'Organigrama',
                'operating_unit_id': self.operating_unit_id.id,
                'department_id': self.department_id.id,
                'short_name': self.short_name,
                'responsible': self.responsible,
                'end_date': self.date,
                'inciso': inciso_name or '',
                'ue': operating_unit_name or '',
            },
        }
