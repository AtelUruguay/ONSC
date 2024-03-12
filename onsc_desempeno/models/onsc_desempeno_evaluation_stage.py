# -*- coding: utf-8 -*-
import json
import logging
import random

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluationStage(models.Model):
    _name = 'onsc.desempeno.evaluation.stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Etapa de evaluaciones 360° por UE'

    def _get_domain(self, args):
        user_contract_id = self.env.user.employee_id.job_id.contract_id
        if self.user_has_groups('onsc_desempeno.group_desempeno_configurador_gh_inciso'):
            args = expression.AND([[('inciso_id', '=', user_contract_id.inciso_id.id), ], args])
        else:
            args = expression.AND([[('operating_unit_id', '=', user_contract_id.operating_unit_id.id), ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluationStage, self)._search(args, offset=offset, limit=limit, order=order,
                                                                 count=count,
                                                                 access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def default_get(self, fields):
        res = super(ONSCDesempenoEvaluationStage, self).default_get(fields)
        if self.user_has_groups('onsc_desempeno.group_desempeno_configurador_gh_ue'):
            operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
            res['operating_unit_id'] = operating_unit_id.id
        return res

    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", required=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string=u'Año a evaluar',
                                       domain=[("active", "=", True)],
                                       required=True, tracking=True)
    year = fields.Integer(
        u'Año a evaluar',
        related="general_cycle_id.year",
        store=True)
    inciso_id = fields.Many2one(
        "onsc.catalog.inciso",
        string="Inciso",
        related="operating_unit_id.inciso_id",
        store=True)
    start_date = fields.Date(string=u'Fecha inicio', required=True, tracking=True)
    end_date_environment = fields.Date(string=u'Fecha fin def. entorno', required=True, tracking=True)
    end_date = fields.Date(string=u'Fecha fin', required=True, tracking=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True)
    closed_stage = fields.Boolean(string="Etapa cerrada", default=False, tracking=True)
    show_buttons = fields.Boolean(string="Editar datos de contrato", compute='_compute_show_buttons')

    is_edit_start_date = fields.Boolean(
        string="Editar datos de destino",
        compute='_compute_is_edit_start_date')
    is_edit_end_date_environment = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_end_date_environment')
    is_edit_end_date = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_end_date')
    is_edit_general_cycle_id = fields.Boolean(
        string="Editar año a evaluar",
        default='_compute_is_edit_general_cycle_id',
        compute='_compute_is_edit_general_cycle_id')

    name = fields.Char('Nombre', compute='_compute_name', store=True)
    is_operating_unit_readonly = fields.Boolean(
        compute=lambda s: s._compute_is_operating_unit_readonly(),
        default=lambda s: s._compute_is_operating_unit_readonly(True))
    operating_unit_id_domain = fields.Char(
        compute=lambda s: s._compute_operating_unit_id_domain(),
        default=lambda s: s._compute_operating_unit_id_domain(True))

    def _compute_is_operating_unit_readonly(self, is_default=False):
        is_operating_unit_readonly = self.user_has_groups(
            'onsc_desempeno.group_desempeno_configurador_gh_ue') and not self.user_has_groups(
            'onsc_desempeno.group_desempeno_configurador_gh_inciso')
        if is_default:
            return is_operating_unit_readonly
        for rec in self:
            second_condition = rec.start_date and rec.start_date <= fields.Date.today()
            rec.is_operating_unit_readonly = is_operating_unit_readonly or second_condition

    def _compute_operating_unit_id_domain(self, is_default=False):
        user_contract_id = self.env.user.employee_id.job_id.contract_id
        is_user_inciso = self.user_has_groups('onsc_desempeno.group_desempeno_configurador_gh_inciso')
        is_user_ue = self.user_has_groups('onsc_desempeno.group_desempeno_configurador_gh_ue')
        if is_user_inciso:
            domain = [('inciso_id', '=', user_contract_id.inciso_id.id)]
        elif is_user_ue:
            domain = [('id', '=', user_contract_id.operating_unit_id.id)]
        else:
            domain = [('id', 'in', [])]
        if is_default:
            return json.dumps(domain)
        for rec in self:
            rec.operating_unit_id_domain = json.dumps(domain)

    @api.depends('end_date')
    def _compute_show_buttons(self):
        for record in self:
            record.show_buttons = record.end_date and record.end_date <= fields.Date.today()

    @api.depends('start_date')
    def _compute_is_edit_start_date(self):
        for record in self:
            record.is_edit_start_date = not record.id or record.start_date > fields.Date.today()

    @api.depends('end_date_environment')
    def _compute_is_edit_end_date_environment(self):
        for record in self:
            record.is_edit_end_date_environment = not record.id or record.end_date_environment > fields.Date.today()

    @api.depends('end_date')
    def _compute_is_edit_end_date(self):
        for record in self:
            record.is_edit_end_date = not record.id or record.end_date > fields.Date.today()

    def _compute_is_edit_general_cycle_id(self):
        EvaluationList = self.env['onsc.desempeno.evaluation.list'].sudo()
        for record in self:
            record.is_edit_general_cycle_id = EvaluationList.search_count(
                [('evaluation_stage_id', '=', record.id)]) == 0

    @api.depends('operating_unit_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            record.name = "%s - %s" % (record.operating_unit_id.name or '', record.general_cycle_id.year)

    @api.constrains('general_cycle_id', 'operating_unit_id')
    def _check_unique_config(self):
        EvalutionStage = self.env['onsc.desempeno.evaluation.stage'].suspend_security()
        for record in self:
            evaluations_qty = EvalutionStage.search_count(
                [("general_cycle_id", "=", record.general_cycle_id.id),
                 ("operating_unit_id", "=", record.operating_unit_id.id), ("id", "!=", record.id)])
            if evaluations_qty > 0:
                raise ValidationError(_(u"Solo se puede tener una configuración para el año"))

    @api.constrains('start_date')
    def _check_start_date_today(self):
        for record in self:
            if record.start_date < fields.Date.today():
                raise ValidationError(_("La fecha inicio debe ser mayor o igual a la fecha actual"))

    @api.constrains('end_date')
    def _check_end_date_today(self):
        for record in self:
            if record.end_date < fields.Date.today():
                raise ValidationError(_("La fecha fin debe ser mayor o igual a la fecha actual"))

    @api.constrains("start_date", "general_cycle_id.start_date", "general_cycle_id.start_date_max")
    def _check_start_dates(self):
        for record in self:
            if record.start_date < record.general_cycle_id.start_date:
                raise ValidationError(
                    _(u"La fecha inicio de las Etapas de evaluaciones 360° por UE debe ser mayor o igual a la fecha de inicio del Ciclo General"))
            if record.start_date > record.general_cycle_id.start_date_max:
                raise ValidationError(
                    _(u"La fecha inicio de las Etapas de evaluaciones 360° por UE debe ser menor o igual a la fecha de inicio máxima del Ciclo General"))

    @api.constrains("end_date", "general_cycle_id.end_date_max")
    def _check_end_dates(self):
        for record in self:
            if record.end_date > record.general_cycle_id.end_date_max:
                raise ValidationError(
                    _(u"La fecha de fin de las Etapas de evaluaciones 360° por UE debe ser menor o igual a la fecha de fin máxima del Ciclo General"))

    @api.constrains("start_date", "end_date", "end_date_environment")
    def _check_dates(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.end_date_environment > record.end_date:
                raise ValidationError(
                    _(u"La Fecha fin def. entorno debe ser menor o igual a la fecha de fin"))
            if int(record.start_date.strftime('%Y')) != record.general_cycle_id.year:
                raise ValidationError(
                    _("La fecha inicio debe estar dentro del año %s") % record.general_cycle_id.year)

    @api.onchange('general_cycle_id')
    def onchange_general_cycle_id(self):
        if self.general_cycle_id:
            self.end_date = self.general_cycle_id.end_date_max

    def toggle_active(self):
        self._check_toggle_active()
        return super(ONSCDesempenoEvaluationStage, self.with_context(no_check_write=True)).toggle_active()

    def action_close_stage(self):
        self._process_end_stage()
        self._process_create_consolidated()
        self._process_gap_deal()
        self.write({'closed_stage': True})
        return True

    def _check_toggle_active(self):
        if not self.active:
            if self.env['onsc.desempeno.general.cycle'].suspend_security().search_count(
                    [('id', '=', self.general_cycle_id.id)]) == 0:
                raise ValidationError(
                    _("No se pueden desarchivar Etapa de evaluaciones 360° si no esta activa la configuración"))
            self._check_unique_config()
            self._check_date()
        return True

    def _process_create_consolidated(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security().with_context(ignore_security_rules=True)
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security().with_context(
            ignore_security_rules=True)

        search_domain = [('evaluation_stage_id', '=', self.id), ('state', '=', 'finished'),
                         ('evaluation_type', 'in', ['environment_evaluation', 'collaborator'])]

        results = Evaluation.search(search_domain)
        for res in results:
            if res.evaluation_type == 'environment_evaluation':
                evaluation_type = 'environment'
            elif res.evaluation_type == 'collaborator':
                evaluation_type = 'collaborator'
            search_domain_consolidated = [('evaluated_id', '=', res.evaluated_id.id),
                                          ('evaluation_stage_id', '=', self.id)]
            if len(results.filtered(
                    lambda r: r.evaluation_type == res.evaluation_type and r.evaluated_id.id == res.evaluated_id.id)) > 1:
                if Consolidated.search_count(search_domain_consolidated) == 0:
                    data = {
                        'general_cycle_id': res.general_cycle_id.id,
                        'current_job_id': res.current_job_id.id,
                        'evaluated_id': res.evaluated_id.id,
                        'inciso_id': res.inciso_id.id,
                        'operating_unit_id': res.operating_unit_id.id,
                        'uo_id': res.uo_id.id,
                        'occupation_id': res.occupation_id.id,
                        'level_id': res.level_id.id,
                        'evaluation_stage_id': res.evaluation_stage_id.id,
                        'evaluation_type': evaluation_type,
                        'evaluator_ids': [(4, res.evaluator_id.id)]
                    }

                    consolidate = Consolidated.create(data)

                    for competency in res.evaluation_competency_ids:
                        number = random.randint(1, 1000)
                        competency.write({'consolidate_id': consolidate.id,
                                          'order': number})

                else:
                    consolidate = Consolidated.search(search_domain_consolidated)
                    consolidate.write({'evaluator_ids': [(4, res.evaluator_id.id)]})

                    for competency in res.evaluation_competency_ids:
                        number = random.randint(1, 1000)
                        competency.write({'consolidate_id': consolidate.id,
                                          'order': number})

    def _process_end_stage(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()

        for record in Evaluation.search(
                [('evaluation_stage_id', '=', self.id), ('state', 'not in', ['canceled', 'finished', 'uncompleted']),
                 ('evaluation_type', 'in', ['environment_evaluation', 'collaborator'])]):
            if record.state == 'completed':
                record.write({'state': 'finished', 'locked': False})
            else:
                record.write({'state': 'uncompleted', 'locked': False})

    def _process_gap_deal(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security().with_context(ignore_security_rules=True)
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security().with_context(
            ignore_security_rules=True)
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security().with_context(
            ignore_security_rules=True)

        valid_days = (self.general_cycle_id.end_date - fields.Date.from_string(fields.Date.today())).days
        _valid_360_types = ['self_evaluation', 'leader_evaluation', 'environment_evaluation', 'collaborator']

        if self.env.user.company_id.days_gap_deal_eval_creation < valid_days:
            partners_to_notify = self.env["res.partner"]
            for record in Evaluation.with_context(ignore_security_rules=True).search([
                ('evaluation_stage_id', '=', self.id),
                ('evaluation_type', 'in', ['leader_evaluation'])]):
                evaluations_360 = Evaluation.search([
                    ('evaluation_stage_id', '=', self.id),
                    ('evaluated_id', '=', record.evaluated_id.id),
                    ('evaluation_type', 'in', _valid_360_types)])
                evaluations_360_states = evaluations_360.mapped('state')
                if any(evaluations_360_state != 'canceled' for evaluations_360_state in evaluations_360_states):
                    evaluation = record.copy_data()
                    evaluation[0]["evaluation_type"] = "gap_deal"
                    evaluation[0]["is_gap_deal_not_generated"] = False
                    evaluation[0]["evaluator_uo_id"] = record.evaluator_uo_id.id
                    evaluation[0]["current_job_id"] = record.current_job_id.id
                    evaluation[0]["general_comments"] = False
                    evaluation[0]["reason_cancel"] = False

                    if record.current_job_id:
                        manager_department = record.current_job_id.department_id.get_first_department_withmanager_in_tree()
                        evaluation[0]["evaluator_id"] = manager_department.manager_id.id
                        evaluation[0]["uo_id"] = record.current_job_id.department_id.id

                    gap_deal = Evaluation.with_context(gap_deal=True).create(evaluation)

                    for competency in record.evaluation_competency_ids:
                        Competency.create({'gap_deal_id': gap_deal.id,
                                           'skill_id': competency.skill_id.id,
                                           'skill_line_ids': [(6, 0, competency.skill_id.skill_line_ids.filtered(
                                               lambda r: r.level_id.id == record.level_id.id).ids)]
                                           })

                    partners_to_notify |= record.evaluated_id.partner_id
                    partners_to_notify |= record.evaluator_id.partner_id
                else:
                    evaluations_360.suspend_security().write({'is_gap_deal_not_generated': True})
                    Consolidated.with_context(ignore_security_rules=True).search([
                        ('evaluation_stage_id', '=', self.id),
                        ('evaluated_id', '=', record.evaluated_id.id),
                    ]).write({'is_gap_deal_not_generated': True})
            self.with_context(partners_to_notify=partners_to_notify)._send_start_stage_2_notification()
        else:
            Evaluation.with_context(ignore_security_rules=True).search([
                ('evaluation_stage_id', '=', self.id),
                ('evaluation_type', 'in', _valid_360_types),
            ]).write({'is_gap_deal_not_generated': True})
            Consolidated.with_context(ignore_security_rules=True).search([
                ('evaluation_stage_id', '=', self.id)
            ]).write({'is_gap_deal_not_generated': True})

    def _send_start_stage_2_notification(self):
        generated_form_email_template_id = self.env.ref('onsc_desempeno.email_template_start_stage_2_form')
        generated_form_email_template_id.send_mail(self.id, force_send=True)

    def get_followers_mails(self):
        return self._context.get('partners_to_notify').get_onsc_mails()

    def get_start_stage_2(self):
        return fields.Datetime.today().strftime('%d/%m/%Y')
