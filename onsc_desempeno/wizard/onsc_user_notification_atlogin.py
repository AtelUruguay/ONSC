# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.user.notification.atlogin'
    _description = 'Mensaje al usuario al login'

    message = fields.Text(string="Mensaje")

    def action_confirm(self):
        a = 5
