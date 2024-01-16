# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.user.notification.atlogin'
    _description = 'Mensaje al usuario al login'

    message = fields.Html(string="Mensaje")

    def action_confirm(self):
        employee = self.env.user.employee_id
        year = fields.Date.from_string(fields.Date.today()).year
        self.env['onsc.desempeno.score'].sudo().search([
            ('is_employee_notified', '=', False),
            ('employee_id', '=', employee.id),
            ('year', '=', year)
        ]).write({'is_employee_notified': True})

        action_dict = self.env['res.users'].sudo()._get_default_action().read()[0]
        self.env.user.sudo().action_id = action_dict.get('id')
        return action_dict
