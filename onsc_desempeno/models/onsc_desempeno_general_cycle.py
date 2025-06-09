# -*- coding: utf-8 -*-
import logging

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoGeneralCycle(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Ciclo general de evaluación de desempeño'
    _rec_name = 'year'
    _order = 'year DESC'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCDesempenoGeneralCycle, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                     toolbar=toolbar,
                                                                     submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_config = self.env.user.has_group(
            'onsc_desempeno.group_desempeno_configurador_gh_ue') or self.user_has_groups(
            'onsc_desempeno.group_desempeno_configurador_gh_inciso')
        is_user_admin = self.env.user.has_group('onsc_desempeno.group_desempeno_administrador')
        if view_type in ['form', 'tree', 'kanban'] and is_user_config and not is_user_admin:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(ONSCDesempenoGeneralCycle, self).default_get(fields_list)
        res['year'] = fields.Date.today().strftime('%Y')
        return res

    year = fields.Integer(u'Año a evaluar', required=True, tracking=True)
    start_date = fields.Date(string=u'Fecha inicio', required=True, tracking=True)
    end_date = fields.Date(string=u'Fecha fin', required=True, tracking=True)
    start_date_max = fields.Date(string=u'Fecha inicio máx.', required=True, tracking=True)
    end_date_max = fields.Date(string=u'Fecha fin máx.', required=True, tracking=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True)
    is_score_generated = fields.Boolean(string='¿Puntajes calculados?')

    is_edit_start_date = fields.Boolean(
        string="Editar datos de destino",
        compute='_compute_is_edit_start_date')
    is_edit_start_date_max = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_start_date_max')
    is_edit_end_date_max = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_end_date_max')
    is_edit_end_date = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_end_date')
    is_pilot = fields.Boolean(string="Piloto 2024")
    date_limit_toextend_360 = fields.Date(string='Fecha límite para la extensión de Etapa 360°')
    whitout_impact = fields.Boolean(string="Sin impacto en legajo")

    @api.depends('start_date')
    def _compute_is_edit_start_date(self):
        for record in self:
            record.is_edit_start_date = not record.id or record.start_date > fields.Date.today()

    @api.depends('start_date_max')
    def _compute_is_edit_start_date_max(self):
        for record in self:
            record.is_edit_start_date_max = not record.id or record.start_date_max > fields.Date.today()

    @api.depends('end_date_max')
    def _compute_is_edit_end_date_max(self):
        for record in self:
            record.is_edit_end_date_max = not record.id or record.end_date_max > fields.Date.today()

    @api.depends('end_date')
    def _compute_is_edit_end_date(self):
        for record in self:
            record.is_edit_end_date = not record.id or record.end_date > fields.Date.today()

    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if record.start_date < fields.Date.today():
                raise ValidationError(_("La fecha inicio debe ser mayor o igual a la fecha actual"))

    @api.constrains('date_limit_toextend_360', 'start_date_max', 'end_date_max')
    def _check_date_limit_toextend_360(self):
        for record in self:
            if record.date_limit_toextend_360 and record.start_date_max and record.end_date_max:
                rule1 = record.date_limit_toextend_360 >= record.end_date_max
                rule2 = record.date_limit_toextend_360 <= record.start_date_max
                if rule1 or rule2:
                    raise ValidationError(_("La fecha límite para la extensión de la Etapa 360°"
                                            "debe estar entre las fechas de inicio y fin máximas"))

    @api.constrains('end_date')
    def _check_end_date_today(self):
        for record in self:
            if record.end_date < fields.Date.today():
                raise ValidationError(_("La fecha fin debe ser mayor o igual a la fecha actual"))

    @api.constrains("start_date", "end_date", "start_date_max", "end_date_max", "year")
    def _check_date(self):
        self._check_unique_config()
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.start_date_max > record.end_date_max:
                raise ValidationError(_(u"La fecha inicio máxima debe ser menor o igual a la fecha de fin máxima"))
            if record.start_date_max < record.start_date:
                raise ValidationError(_(u"La fecha inicio máxima debe ser mayor o igual a la fecha de inicio"))
            if record.end_date_max > record.end_date:
                raise ValidationError(_(u"La fecha fin máxima debe ser menor o igual a la fecha de fin"))

            if int(record.start_date.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha inicio debe estar dentro del año %s") % record.year)

            if int(record.start_date_max.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha inicio máxima debe estar dentro del año %s") % record.year)

    @api.constrains('year')
    def _check_unique_config(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        for record in self:
            general_qty = GeneralCycle.search_count(
                [("year", "=", record.year), ("id", "!=", record.id)])
            if general_qty > 0:
                raise ValidationError(_(u"Solo se puede tener una configuración para el mismo año"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        year = self.search([], limit=1, order="year desc").year + 1

        default['year'] = _("%s") % year
        default['start_date'] = _("%s") % '%s-' % year + self.start_date.strftime('%m-%d')
        default['end_date'] = _("%s") % '%s-' % year + self.end_date.strftime('%m-%d')
        default['start_date_max'] = _("%s") % '%s-' % year + self.start_date_max.strftime('%m-%d')
        default['end_date_max'] = _("%s") % '%s-' % year + self.end_date_max.strftime('%m-%d')

        return super(ONSCDesempenoGeneralCycle, self).copy(default=default)

    def disable_evaluation(self):
        self.search([('end_date', '<', fields.Date.today())]).write({'active': False})
        self.env['onsc.desempeno.evaluation.stage'].suspend_security().search(
            [('general_cycle_id.end_date', '<', fields.Date.today())]).write({'active': False, 'closed_stage': True})

    def toggle_active(self):
        self._check_toggle_active()
        return super(ONSCDesempenoGeneralCycle, self.with_context(no_check_write=True)).toggle_active()

    def _check_toggle_active(self):
        if not self.env.user.has_group('onsc_desempeno.group_desempeno_administrador'):
            raise ValidationError(_("No tiene permiso para archivar o desarchivar"))

        if self.active and self.env['onsc.desempeno.evaluation.stage'].search_count(
                [('general_cycle_id', 'in', self.ids)]):
            raise ValidationError(_("No se puede archivar si ya tiene Etapas de evaluaciones 360° por UE cargadas"))

        if not self.active:
            self._check_unique_config()
        return True

    def unlink(self):
        self._check_can_unlink()
        return super(ONSCDesempenoGeneralCycle, self).unlink()

    def _check_can_unlink(self):
        if self.env['onsc.desempeno.evaluation.stage'].suspend_security().search_count(
                [('general_cycle_id', 'in', self.ids)]) > 0:
            raise ValidationError(
                _("No se pueden eliminar configuraciones mientras se tenga una Etapa de evaluaciones 360° activa"))

    def process_score_calculator(self):
        """
        Proceso de calculo de puntajes al fin del ciclo general. Debe disparase por un Cron
        :return: True
        """
        Score = self.env['onsc.desempeno.score'].sudo()
        Evaluation = self.env['onsc.desempeno.evaluation'].with_context(ignore_security_rules=True).sudo()
        EvaluationStage = self.env['onsc.desempeno.evaluation.stage'].sudo()

        valid_records = self.sudo().search([
            ('is_score_generated', '=', False),
            ('end_date', '<=', fields.Date.today())
        ])
        stages_360 = EvaluationStage.search([
            ('general_cycle_id', 'in', valid_records.ids),
        ])

        EVALUATION_TYPES = [
            'self_evaluation',
            'leader_evaluation',
            'environment_evaluation',
            'collaborator',
            'environment_definition',
            'gap_deal',
            'development_plan',
            'tracing_plan',
        ]
        EVALUATION_360_TYPES = [
            'self_evaluation',
            'leader_evaluation',
            'environment_evaluation',
            'collaborator',
            'environment_definition'
        ]

        evaluations = Evaluation.search([
            ('evaluator_id.legajo_state', '!=', 'egresed'),
            ('evaluation_stage_id', 'in', stages_360.ids),
            ('evaluation_type', 'in', EVALUATION_TYPES),
            ('state', '!=', 'canceled'),
            ('state_gap_deal', '!=', 'canceled'),
            ('evaluator_current_job_id', '!=', False)
        ])
        scores_dict = {}
        for evaluation in evaluations:
            key = '%s;;%s;;%s;;%s;;%s' % (
                evaluation.evaluator_id.id,
                evaluation.evaluator_current_job_id.id,
                evaluation.evaluator_current_job_id.inciso_id.id,
                evaluation.evaluator_current_job_id.operating_unit_id.id,
                evaluation.evaluation_stage_id.year,
            )

            if key not in scores_dict.keys():
                scores_dict[key] = self._get_evaluation_key_default_dict(evaluation)

            if evaluation.evaluation_type in EVALUATION_360_TYPES:
                scores_dict[key]['evaluations_360_total_qty'] += 1
                if evaluation.state == 'finished':
                    scores_dict[key]['evaluations_360_finished_qty'] += 1
            elif evaluation.evaluation_type == 'gap_deal':
                scores_dict[key]['evaluations_gap_deal_qty'] += 1
                if evaluation.state_gap_deal == 'finished':
                    scores_dict[key]['evaluations_gap_deal_finished_qty'] += 1
            elif evaluation.evaluation_type == 'development_plan':
                scores_dict[key]['evaluations_develop_plan_qty'] += 1
                if evaluation.state_gap_deal == 'finished':
                    scores_dict[key]['evaluations_develop_plan_finished_qty'] += 1
            else:
                scores_dict[key]['evaluations_tracing_plan_qty'] += 1
                if evaluation.state == 'finished':
                    scores_dict[key]['evaluations_tracing_plan_finished_qty'] += 1
                    # COMPETENCIAS
                    development_means_ids = evaluation.tracing_plan_ids.mapped('development_means_ids')
                    development_means_ids = development_means_ids.filtered(
                        lambda x: not x.is_canceled and x.last_tracing_plan_id.id is not False)
                    scores_dict[key]['evaluations_tracing_plan_activity_qty'] = len(development_means_ids)
                    for development_mean_id in development_means_ids:
                        porcent = development_mean_id.last_tracing_plan_id.degree_progress_id.porcent
                        scores_dict[key]['evaluations_tracing_plan_percent_list'].append(porcent)

        bulked_vals = self._get_score_data(scores_dict)
        Score.create(bulked_vals)
        # TODO: marcar evaluaciones que ya hicieron puntajes
        valid_records.write({'is_score_generated': True})
        return True

    def _get_evaluation_key_default_dict(self, evaluation):
        evaluator_current_job_id = evaluation.evaluator_current_job_id
        return {
            'employee_id': evaluation.evaluator_id.id,
            'department_id': evaluator_current_job_id.department_id.id,
            'operating_unit_id': evaluator_current_job_id.operating_unit_id.id,
            'inciso_id': evaluator_current_job_id.inciso_id.id,
            'evaluation_stage_id': evaluation.evaluation_stage_id.id,
            'year': evaluation.evaluation_stage_id.year,
            'evaluation_list_id': evaluation.evaluation_list_id.id,
            'is_pilot': evaluation.general_cycle_id.is_pilot,
            'is_employee_notified': evaluation.general_cycle_id.whitout_impact,
            'whitout_impact': evaluation.general_cycle_id.whitout_impact,
            # 360
            'evaluations_360_total_qty': 0,
            'evaluations_360_finished_qty': 0,
            # gap deal
            'evaluations_gap_deal_qty': 0,
            'evaluations_gap_deal_finished_qty': 0,
            # develop_plan
            'evaluations_develop_plan_qty': 0,
            'evaluations_develop_plan_finished_qty': 0,
            # tracing plan
            'evaluations_tracing_plan_qty': 0,
            'evaluations_tracing_plan_finished_qty': 0,
            'evaluations_tracing_plan_activity_qty': 0,
            'evaluations_tracing_plan_percent_list': [],
        }

    def _get_score_data(self, scores_dict):
        bulked_vals = []
        config_eval_360_score = self.env.user.company_id.eval_360_score
        config_gap_deal_score = self.env.user.company_id.gap_deal_score
        config_develop_plan_score = self.env.user.company_id.development_plan_score
        config_tracing_plan_score = self.env.user.company_id.tracing_plan_score
        config_tracing_plan_activity_score = self.env.user.company_id.tracing_plan_activity_score
        for key, value in scores_dict.items():
            if value['evaluations_360_total_qty'] > 0:
                eval_360_score = config_eval_360_score / value['evaluations_360_total_qty']
            else:
                eval_360_score = float(0)
            eval_360_finished_score = value['evaluations_360_finished_qty'] * eval_360_score

            if value.get('evaluations_gap_deal_finished_qty') > 0 and value.get('evaluations_gap_deal_qty') > 0:
                eval_gap_deal_finished_score = float(config_gap_deal_score) / value['evaluations_gap_deal_qty']
            else:
                eval_gap_deal_finished_score = float(0)
            eval_gap_deal_finished_score = value['evaluations_gap_deal_finished_qty'] * eval_gap_deal_finished_score

            if value.get('evaluations_develop_plan_finished_qty') > 0 and value.get('evaluations_develop_plan_qty') > 0:
                eval_develop_plan_finished_score = float(config_develop_plan_score) / value[
                    'evaluations_develop_plan_qty']
            else:
                eval_develop_plan_finished_score = float(0)
            eval_develop_plan_finished_score = value['evaluations_develop_plan_finished_qty'] * eval_develop_plan_finished_score

            if value.get('evaluations_tracing_plan_finished_qty') > 0 and value.get('evaluations_tracing_plan_qty') > 0:
                eval_tracing_plan_finished_score = float(config_tracing_plan_score) / value[
                    'evaluations_tracing_plan_qty']
            else:
                eval_tracing_plan_finished_score = float(0)
            eval_tracing_plan_finished_score = value['evaluations_tracing_plan_finished_qty'] * eval_tracing_plan_finished_score

            percap_tracing_plan_activity_qty = len(value['evaluations_tracing_plan_percent_list'])
            if percap_tracing_plan_activity_qty > 0:
                percap_tracing_plan_activity_score = config_tracing_plan_activity_score / percap_tracing_plan_activity_qty
            else:
                percap_tracing_plan_activity_score = float(0)
            tracing_plan_activity_score = float(0)
            for percent in value['evaluations_tracing_plan_percent_list']:
                tracing_plan_activity_score += percent * percap_tracing_plan_activity_score

            bulked_vals.append({
                'evaluation_stage_id': value['evaluation_stage_id'],
                'evaluation_list_id': value['evaluation_list_id'],
                'year': value['year'],
                'department_id': value['department_id'],
                'operating_unit_id': value['operating_unit_id'],
                'inciso_id': value['inciso_id'],
                'employee_id': value['employee_id'],
                # 360
                'evaluations_360_total_qty': value['evaluations_360_total_qty'],
                'evaluations_360_finished_qty': value['evaluations_360_finished_qty'],
                'evaluations_360_score': eval_360_score,
                'evaluations_360_finished_score': eval_360_finished_score,
                # gap deal
                'evaluations_gap_deal_finished_score': eval_gap_deal_finished_score,
                # develop_plan
                'evaluations_develop_plan_finished_score': eval_develop_plan_finished_score,
                # tracing plan
                'evaluations_tracing_plan_finished_score': eval_tracing_plan_finished_score,
                'evaluations_tracing_plan_activity_score': tracing_plan_activity_score,
                # total
                'score': eval_360_finished_score + eval_gap_deal_finished_score + eval_tracing_plan_finished_score + tracing_plan_activity_score + eval_develop_plan_finished_score,
                'is_pilot': value['is_pilot'],
                'is_employee_notified': value['is_employee_notified'],
                'whitout_impact': value['whitout_impact'],
            })
        return bulked_vals
