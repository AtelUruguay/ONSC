# pylint: disable=E8102
# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUser(models.Model):
    _inherit = "res.users"

    def _get_action(self, jobs):
        employee = self.employee_id
        year = fields.Date.from_string(fields.Date.today()).year
        scores = self.env['onsc.desempeno.score'].search([
            ('employee_id', '=', employee.id),
            ('is_employee_notified', '=', False)
        ])
        if scores:
            message = """<p style="box-sizing:border-box;font-weight:bolder;font-size: 16px;">
El ciclo de evaluación para el año %s ha concluido.
</p>""" % (str(year))
            for score in scores:
                message += """<p style="box-sizing:border-box;font-size: 14px;">
Para %s, %s, %s el Puntaje es: %s </p>""" % (
                    score.inciso_id.display_name,
                    score.operating_unit_id.display_name,
                    score.department_id.display_name,
                    str(score.score)
                )
            notification = self.env['onsc.user.notification.atlogin'].sudo().create({
                'message': message
            })
            action = self.sudo().env.ref('onsc_desempeno.onsc_user_notification_atlogin_action')
            action.res_id = notification
            return action.id
        else:
            return super(ResUser, self)._get_action(jobs)
