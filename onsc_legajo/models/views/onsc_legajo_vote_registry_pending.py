# -*- coding: utf-8 -*-

import json

from odoo import fields, models, tools, api


class ONSCLegajoVoteRegistryPendingConsult(models.Model):
    _name = "onsc.legajo.vote.registry.pending.consult"
    _inherit = "onsc.legajo.abstract.legajo.security"
    _description = "Legajo - Consulta Registro de votos pendientes"
    _auto = False
    _order = "legajo_id"
    _rec_name = 'nro_doc'

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_legajo.group_legajo_vote_control_consulta,onsc_legajo.group_legajo_vote_control_administrar')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_recursos_humanos_inciso')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_recursos_humanos_ue')

    def _get_abstract_responsable_uo(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_responsable_uo')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoVoteRegistryPendingConsult, self).fields_get(allfields, attributes)
        hide = ['legajo_id']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    nro_doc = fields.Char(string='CI')
    legajo_id = fields.Many2one('onsc.legajo', string="Funcionario")
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    # conc_valid_electoral_act_id = fields.Char(string='Actos electorales (ids concatenados)', )
    # conc_valid_electoral_act_name = fields.Char(string='Actos electorales')

    # electoral_act_ids = fields.Many2many(
    #     comodel_name='onsc.legajo.electoral.act',
    #     string='Elecciones pendientes',
    #     compute='_compute_electoral_act_ids'
    # )
    electoral_act_id = fields.Many2one(
        comodel_name='onsc.legajo.electoral.act',
        string='Elección pendiente',
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT
    row_number() OVER(ORDER BY employee_id, electoral_act_id) AS id, *
FROM
(SELECT nro_doc, employee_id,legajo_id, electoral_act_id, electoral_act_name FROM
(
    --PRODUCTO FUNCIONARIO,ELECCIONES VIGENTES
    SELECT
        nro_doc,
        employee_id AS employee_id,
        onsc_legajo.id AS legajo_id,
        onsc_legajo_electoral_act.id AS electoral_act_id,
        onsc_legajo_electoral_act.name AS electoral_act_name,
        CONCAT('EMP:', employee_id, ',EA:', onsc_legajo_electoral_act.id) AS manual_key
    FROM onsc_legajo, onsc_legajo_electoral_act
    WHERE
        onsc_legajo.legajo_state = 'active' AND
        onsc_legajo_electoral_act.date_since_entry_control <= CURRENT_DATE AND
        onsc_legajo_electoral_act.date_until_entry_control >= CURRENT_DATE) AS employee_all_electoral_act
WHERE
    manual_key NOT IN (
    --VOTOS REGISTRADOS
        SELECT
            CONCAT('EMP:', employee_id, ',EA:', onsc_legajo_vote_registry_electoral_act.onsc_legajo_electoral_act_id)
        FROM
            onsc_legajo_vote_registry_electoral_act INNER JOIN
            onsc_legajo_vote_registry
        ON
            onsc_legajo_vote_registry_electoral_act.onsc_legajo_vote_registry_id = onsc_legajo_vote_registry.id
        ) ORDER BY employee_id, electoral_act_id) as main_query
)''' % (self._table,))

    # def _compute_electoral_act_ids(self):
    #     ElectoralAct = self.env['onsc.legajo.electoral.act'].sudo()
    #     for rec in self:
    #         valid_ids = [int(x) for x in rec.conc_valid_electoral_act_id.split(",")]
    #         rec.electoral_act_ids = ElectoralAct.search([('id', 'in', valid_ids)])

    def button_create_registry(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_vote_registry_wizard_action').suspend_security()
        _context = action._context.copy()

        # valid_ids = [int(x) for x in self.conc_valid_electoral_act_id.split(",")]
        _context.update({
            'default_employee_id': self.employee_id.id,
            'default_electoral_act_ids': [(6, 0, [self.electoral_act_id.id])],
            'default_default_electoral_act_ids_domain': json.dumps([('id', 'in', [self.electoral_act_id.id])])
        })
        action.context = _context
        return action.read()[0]

    def button_view_registry(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_vote_registry_pending_consult_wizard_action').suspend_security()
        action.res_id = self.id
        return action.read()[0]
