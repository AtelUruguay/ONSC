# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    @api.depends('res_model', 'res_id')
    def _get_domain_partner_ids(self):
        context = self.env.context.copy()
        model = context.get('default_res_model', '')
        res_id = context.get('default_res_id', False)
        if model == 'onsc.legajo.alta.vl' and res_id:
            alta_id = self.env[model].browse(res_id)
            recursos_humanos_inciso = self.env.ref('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso')
            recursos_humanos_ue = self.env.ref('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')
            roles_inciso_ids = recursos_humanos_inciso.role_ids.ids
            roles_ue_ids = recursos_humanos_ue.role_ids.ids
            today = fields.Date.today()
            job_role_ids = self.env['hr.job.role.line'].search([
                '|',
                ('user_role_id', 'in', roles_inciso_ids),
                ('user_role_id', 'in', roles_ue_ids),
                ('active', '=', True),
                ('start_date', '<=', today),
                '|',
                ('end_date', '>=', today),
                ('end_date', '=', False)
            ])
            jobs_roles_inciso = job_role_ids.filtered(lambda r: r.user_role_id.id in roles_inciso_ids).mapped('job_id')
            jobs_roles_ue = job_role_ids.filtered(lambda r: r.user_role_id.id in roles_ue_ids).mapped('job_id')
            contracts = jobs_roles_inciso.mapped('contract_id').filtered(lambda c: c.legajo_state in ['active',
                                                                                                      'outgoing_commission'] and c.inciso_id == alta_id.inciso_id)
            contracts |= jobs_roles_ue.mapped('contract_id').filtered(lambda c: c.legajo_state in ['active',
                                                                                                   'outgoing_commission'] and c.operating_unit_id == alta_id.operating_unit_id)
            partners = contracts.mapped('employee_id.user_id.partner_id')
            return [('id', 'in', partners.ids)]
        return [('type', '!=', 'private')]

    partner_ids = fields.Many2many('res.partner', string='Recipients',
                                   help="List of partners that will be added as follower of the current document.",
                                   domain=_get_domain_partner_ids)
