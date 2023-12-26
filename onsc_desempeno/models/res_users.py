# pylint: disable=E8102
# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUser(models.Model):
    _inherit = "res.users"

    def _get_action(self, jobs):
        employee = self.employee_id
        year = fields.Date.from_string(fields.Date.today()).year
        scores = self.env['onsc.desempeno.score'].search([
            ('employee_id','=',employee.id),
            ('evaluation_stage_id.year', '=', year)
        ])
        if scores:
            message = ''
            for score in scores:
                message += ". %s" % (str(score.score))
            action = self.sudo().env.ref('onsc_desempeno.onsc_user_notification_atlogin_action').read()[0]
            message = self.env['onsc.user.notification.atlogin'].create({
                'message': message
            })
            action.update({'res_id': message.id})
            return action
        else:
            return super(ResUser, self)._get_action(jobs)
