# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

MODELS_TOCHECK = [
    'onsc.legajo.alta.vl',
    'onsc.legajo.baja.vl',
    'onsc.legajo.role.assignment'
]
class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    def _default_send_mail(self):
        if self._context.get('default_res_model', '') in MODELS_TOCHECK:
            return False
        return True

    send_mail = fields.Boolean('Send Email', default=_default_send_mail,
                               help="If checked, the partners will receive an email warning they have been added in the document's followers.")

    @api.depends('res_model', 'res_id')
    def _get_domain_partner_ids(self):
        context = self.env.context.copy()
        model = context.get('default_res_model', '')
        res_id = context.get('default_res_id', False)
        if model not in MODELS_TOCHECK:
            return [('type', '!=', 'private')]

        if model == 'onsc.legajo.alta.vl' and res_id:
            record_id = self.env[model].browse(res_id)
            recursos_humanos_inciso = self.env.ref('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso')
            recursos_humanos_ue = self.env.ref('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')
        elif model == 'onsc.legajo.baja.vl' and res_id:
            record_id = self.env[model].browse(res_id)
            recursos_humanos_inciso = self.env.ref('onsc_legajo.group_legajo_baja_vl_recursos_humanos_inciso')
            recursos_humanos_ue = self.env.ref('onsc_legajo.group_legajo_baja_vl_recursos_humanos_ue')
        elif model == 'onsc.legajo.role.assignment' and res_id:
            record_id = self.env[model].browse(res_id)
            recursos_humanos_inciso = self.env.ref('onsc_legajo.group_legajo_role_assignment_recursos_humanos_inciso')
            recursos_humanos_ue = self.env.ref('onsc_legajo.group_legajo_role_assignment_recursos_humanos_ue')
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
                                                                                                  'outgoing_commission'] and c.inciso_id == record_id.inciso_id)
        contracts |= jobs_roles_ue.mapped('contract_id').filtered(lambda c: c.legajo_state in ['active',
                                                                                               'outgoing_commission'] and c.operating_unit_id == record_id.operating_unit_id)
        partners = contracts.mapped('employee_id.user_id.partner_id')
        return [('id', 'in', partners.ids)]

    partner_ids = fields.Many2many('res.partner', string='Recipients',
                                   help="List of partners that will be added as follower of the current document.",
                                   domain=_get_domain_partner_ids)
