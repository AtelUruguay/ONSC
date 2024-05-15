# pylint: disable=E8102
# -*- coding: utf-8 -*-
from odoo import models


class ResUser(models.Model):
    _inherit = "res.users"

    def _get_action(self, jobs):
        employee = self.employee_id
        scores = self.env['onsc.desempeno.score'].search([
            ('employee_id', '=', employee.id),
            ('is_employee_notified', '=', False)
        ])
        if scores:
            message = """<p style="box-sizing:border-box;font-weight:bolder;font-size: 16px;">
El ciclo de evaluación ha concluido.
</p>"""
            for score in scores:
                message += """<p style="box-sizing:border-box;font-size: 14px;">
Para el Año: %s, Inciso: %s, UE: %s, UO: %s el Puntaje es: %s </p>""" % (
                    str(score.year),
                    score.inciso_id.display_name,
                    score.operating_unit_id.display_name,
                    score.department_id.display_name,
                    str(round(score.score, 2))
                )
            notification = self.env['onsc.user.notification.atlogin'].sudo().create({
                'message': message
            })
            action = self.sudo().env.ref('onsc_desempeno.onsc_user_notification_atlogin_action')
            action.res_id = notification
            return action.id
        else:
            return super(ResUser, self)._get_action(jobs)
