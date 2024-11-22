# -*- coding:utf-8 -*-
import json

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.addons.onsc_base.onsc_useful_tools import to_timestamp as to_timestamp

_CUSTOM_ORDER = {
    'confirm': 1,
    'end': 2
}

FIELDS_TO_EXLUDE = [
    'norm_code_discharge_id',
    'reason_discharge'
]


class HrContract(models.Model):
    _name = 'hr.contract'
    _rec_name = 'legajo_name'
    _inherit = ['hr.contract', 'model.history']
    _history_model = 'hr.contract.model.history'
    _history_columns = ['date_start', 'date_end']
    _fields_to_exclude_insearch = FIELDS_TO_EXLUDE

    def init(self):
        self._cr.execute("""CREATE INDEX IF NOT EXISTS hr_contract_employee_id ON hr_contract (employee_id)""")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if not self._context.get('no_scale') and self._context.get('filter_contracts') and not self._context.get(
                'from_smart_button'):
            if self._context.get('active_id'):
                contract_ids = self.env['onsc.legajo'].with_context(no_scale=True).browse(
                    self._context.get('active_id')).contract_ids.ids
            else:
                contract_ids = []
            args = expression.AND([[('id', 'in', contract_ids)], args])
        return super(HrContract, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        doc = etree.fromstring(res['arch'])
        is_group_security = self.env.user.has_group(
            'onsc_legajo.group_legajo_editar_ocupacion_contrato') and not self.env.user.has_group(
            'onsc_legajo.group_legajo_configurador')
        if is_group_security:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
        if view_type == 'form':
            for t in doc.xpath("//field"):
                if t.get('name') != 'occupation_id' and is_group_security:
                    t.set('readonly', '1')
                    modifiers = json.loads(t.get("modifiers") or "{}")
                    modifiers['readonly'] = True
                    t.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc)
        return res

    # @api.model
    # def _default_state_square_id(self):
    #     try:
    #         return self.env.ref('onsc_legajo.onsc_legajo_o')
    #     except Exception:
    #         return self.env['onsc.legajo.state.square']

    legajo_name = fields.Char(string="Nombre", compute='_compute_legajo_name', store=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', history=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", history=True, index=True)

    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen', history=True)
    operating_unit_origin_id = fields.Many2one("operating.unit",
                                               string="Unidad ejecutora origen",
                                               domain="[('inciso_id','=', inciso_origin_id)]",
                                               history=True)
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    sec_position = fields.Char(string="Sec Plaza", history=True)
    state_square_id = fields.Many2one(
        'onsc.legajo.state.square',
        string='Estado plaza',
        # default=lambda s: s._default_state_square_id(),
        history=True)
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso', history=True)
    call_number = fields.Char(string='Número de llamado', history=True)
    legajo_state = fields.Selection(
        [('active', 'Activo'),
         ('baja', 'Baja'),
         ('reserved', 'Reservado'),
         ('outgoing_commission', 'Comisión saliente'),
         ('incoming_commission', 'Comisión entrante')],
        tracking=True, string='Estado del Contrato', history=True)
    cs_contract_id = fields.Many2one('hr.contract', string='Contrato relacionado', history=True)
    first_name = fields.Char(string=u'Primer nombre', related='employee_id.cv_first_name', store=True)
    second_name = fields.Char(string=u'Segundo nombre', related='employee_id.cv_second_name', store=True)
    last_name_1 = fields.Char(string=u'Primer apellido', related='employee_id.cv_last_name_1', store=True)
    last_name_2 = fields.Char(string=u'Segundo apellido', related='employee_id.cv_last_name_2', store=True)
    emissor_country_id = fields.Many2one('res.country', string=u'País emisor del documento',
                                         related='employee_id.cv_emissor_country_id', store=True)
    document_type_id = fields.Many2one('onsc.cv.document.type', string=u'Tipo de documento',
                                       related='employee_id.cv_document_type_id', store=True)
    nro_doc = fields.Char(u'Número de documento', related='employee_id.cv_nro_doc', store=True)
    program = fields.Char(string='Programa', history=True)
    project = fields.Char(string='Proyecto', history=True)
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', history=True)
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', history=True)
    occupation_date = fields.Date(string='Fecha desde Ocupación', history=True)
    is_occupation_visible = fields.Boolean(compute='_compute_is_occupation_visible')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1', history=True)
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2', history=True)
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3', history=True)
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4', history=True)
    graduation_date = fields.Date(string='Fecha de graduación', history=True)
    position = fields.Char(string='Puesto', history=True)
    workplace = fields.Char(string='Plaza', history=True)
    reason_description = fields.Char(string='Descripción del motivo alta', history=True)
    norm_code_id = fields.Many2one('onsc.legajo.norm', string='Código de norma alta', history=True)
    type_norm_discharge = fields.Char(string='Tipo de norma alta', related='norm_code_id.tipoNorma')
    reason_discharge = fields.Char(string='Descripción del motivo alta', history=True)
    norm_code_discharge_id = fields.Many2one('onsc.legajo.norm', string='Código de norma alta', history=True)
    norm_number_discharge = fields.Integer(string='Número de norma alta',
                                           related='norm_code_id.numeroNorma')
    norm_year_discharge = fields.Integer(string='Año de norma alta', related='norm_code_id.anioNorma')
    norm_article_discharge = fields.Integer(string='Artículo de norma alta',
                                            related='norm_code_id.articuloNorma')
    resolution_description = fields.Char(string='Descripción de la resolución', history=True)
    resolution_date = fields.Date(string='Fecha de la resolución', history=True)
    resolution_type = fields.Selection(
        [('M', 'Inciso'), ('P', 'Presidencia o Poder ejecutivo'), ('U', 'Unidad ejecutora')],
        string='Tipo de resolución alta', history=True)
    contract_expiration_date = fields.Date(string='Vencimiento del contrato', history=True)
    additional_information = fields.Char(string='Información adicional alta', history=True)
    code_day = fields.Char(string="Código de la jornada", history=True)
    description_day = fields.Char(string="Descripción de la Jornada", history=True)
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva', history=True)
    retributive_day_description = fields.Char(
        string='Descripción de jornada retributiva',
        related='retributive_day_id.descripcionJornada',
        store=True,
        history=True
    )
    id_alta = fields.Char(string='Id de alta', history=True)
    id_deregistration_discharge = fields.Char(string='Id de baja', history=True)
    reason_deregistration = fields.Char(string='Descripción del motivo baja', history=True)
    norm_code_deregistration_id = fields.Many2one('onsc.legajo.norm', string='Código de la norma de baja', history=True)
    type_norm_deregistration = fields.Char(string='Tipo de norma baja', related='norm_code_deregistration_id.tipoNorma')
    norm_number_deregistration = fields.Integer(string='Número de norma baja',
                                                related='norm_code_deregistration_id.numeroNorma')
    norm_year_deregistration = fields.Integer(string='Año de norma baja',
                                              related='norm_code_deregistration_id.anioNorma')
    norm_article_deregistration = fields.Integer(string='Artículo de norma baja',
                                                 related='norm_code_deregistration_id.articuloNorma')
    resolution_description_deregistration = fields.Char(string='Descripción de la resolución baja', history=True)
    resolution_date_deregistration = fields.Date(string='Fecha de la resolución baja', history=True)
    resolution_type_deregistration = fields.Selection(
        [('M', 'Inciso'), ('P', 'Presidencia o Poder ejecutivo'), ('U', 'Unidad ejecutora')],
        string='Tipo de resolución baja', history=True)
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string="Causal de egreso", history=True)
    causes_discharge_extended = fields.Many2one("onsc.legajo.causes.discharge.line",
                                                string="Causal de egreso extendido",
                                                domain="[('causes_discharge_id', '=', causes_discharge_id)]",
                                                history=True)

    is_require_extended = fields.Boolean(u"¿Requiere extendido?", related='causes_discharge_id.is_require_extended')
    additional_information_deregistration = fields.Char(string='Información adicional baja', history=True)
    alta_attached_document_ids = fields.One2many('onsc.legajo.attached.document',
                                                 'contract_id',
                                                 string='Documentos adjuntos alta',
                                                 domain=[('type', '=', 'discharge')])
    attached_document_deregistration_ids = fields.One2many('onsc.legajo.attached.document',
                                                           'contract_id',
                                                           string='Documentos adjuntos baja',
                                                           domain=[('type', '=', 'deregistration')])
    job_ids = fields.One2many('hr.job', 'contract_id', string='Puestos', context={'active_test': False})
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión', history=True)
    date_end_commission = fields.Date(string='Fecha hasta de la Comisión', copy=False, history=True)
    show_button_update_occupation = fields.Boolean(compute='_compute_show_button_update_occupation')
    is_mi_legajo = fields.Boolean(compute='_compute_is_mi_legajo')
    notify_sgh = fields.Boolean("Notificar SGH")
    last_notify_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario que dispara la notificación SGH')
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission",
                                               string="Motivo extinción de la comisión")

    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones',
        copy=False, history=True)

    legajo_id = fields.Many2one('onsc.legajo', string='Legajo', compute='_compute_legajo_id', store=True)
    show_law_legajo_legend = fields.Boolean(
        string='¿Mostrar leyenda de legajo?',
        compute='_compute_show_law_legajo_legend'
    )
    law_legajo_legend = fields.Char(
        string='Leyenda de legajo',
        compute='_compute_show_law_legajo_legend'
    )
    descriptor1_origin_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1 origen')
    descriptor2_origin_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2 origen')
    descriptor3_origin_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3 origen')
    descriptor4_origin_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4 origen')
    inciso_dest_id = fields.Many2one('onsc.catalog.inciso', string='Inciso destino', history=True)
    operating_unit_dest_id = fields.Many2one("operating.unit",
                                             string="Unidad ejecutora Destino",
                                             domain="[('inciso_id','=', inciso_dest_id)]",
                                             history=True)

    def name_get(self):
        res = []
        for record in self:
            if self._context.get('show_descriptors', False):
                descriptor1 = record.descriptor1_id and " - " + record.descriptor1_id.name or ''
                descriptor2 = record.descriptor2_id and " - " + record.descriptor2_id.name or ''
                descriptor3 = record.descriptor3_id and " - " + record.descriptor3_id.name or ''
                descriptor4 = record.descriptor4_id and " - " + record.descriptor4_id.name or ''
                name = "%s %s %s %s %s" % (
                    record.legajo_name,
                    descriptor1,
                    descriptor2,
                    descriptor3,
                    descriptor4)
            else:
                name = record.legajo_name
            res.append((record.id, name))
        return res

    @api.depends('employee_id')
    def _compute_legajo_id(self):
        for rec in self.filtered(lambda x: x.employee_id):
            rec.legajo_id = self.env['onsc.legajo'].sudo().search([('employee_id', '=', rec.employee_id.id)], limit=1)

    def test_legajo(self):
        self._compute_legajo_id()

    @api.depends('employee_id', 'position', 'workplace', 'sec_position', )
    def _compute_legajo_name(self):
        for rec in self:
            if rec.employee_id and (rec.position or rec.workplace or rec.sec_position):
                str_list = [rec.employee_id.cv_nro_doc or rec.employee_id.name]
                if rec.position:
                    str_list.append(rec.position)
                if rec.workplace:
                    str_list.append(rec.workplace)
                if rec.sec_position:
                    str_list.append(rec.sec_position)
                rec.legajo_name = ' - '.join(str_list)
            else:
                rec.legajo_name = rec.name

    @api.depends('date_start', 'date_end', 'inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            if rec.inciso_id.id is False:
                self.operating_unit_id_domain = json.dumps([('id', 'in', [])])
            else:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
                if rec.date_start:
                    domain = ['&'] + domain + [('start_date', '<=', fields.Date.to_string(rec.date_start))]
                if rec.date_end:
                    domain = ['&'] + domain + ['|', ('end_date', '>=', fields.Date.to_string(rec.date_end)),
                                               ('end_date', '=', False)]
                self.operating_unit_id_domain = json.dumps(domain)

    @api.depends('inciso_id', 'operating_unit_id', 'regime_id', 'descriptor1_id')
    def _compute_is_occupation_visible(self):
        has_valid_group = self.user_has_groups('onsc_legajo.group_legajo_hr_inciso,onsc_legajo.group_legajo_hr_ue')
        ue_code = ['13', '5', '7', '8']
        for rec in self:
            cond1 = not (rec.inciso_id.budget_code == '5' and rec.operating_unit_id.budget_code in ue_code)
            cond2 = rec.descriptor1_id.is_occupation_required or not rec.descriptor1_id.id
            rec.is_occupation_visible = has_valid_group and cond1 and rec.regime_id.is_public_employee and cond2

    @api.depends('inciso_id', 'operating_unit_id', 'regime_id', 'descriptor1_id', 'legajo_state')
    def _compute_show_button_update_occupation(self):
        for rec in self:
            is_valid_group = self.env.user.has_group(
                'onsc_legajo.group_legajo_editar_ocupacion_contrato')
            is_valid_state = rec.legajo_state != 'baja'
            rec.show_button_update_occupation = is_valid_group and is_valid_state and rec.is_occupation_visible

    @api.depends('regime_id', 'descriptor1_id')
    def _compute_show_law_legajo_legend(self):
        Legend = self.env['onsc.legajo.legend']
        for rec in self:
            legend = Legend._get_legajo_legend(rec.regime_id.id, rec.descriptor1_id.id)
            if legend:
                rec.show_law_legajo_legend = True
                rec.law_legajo_legend = legend.name
            else:
                rec.show_law_legajo_legend = False
                rec.law_legajo_legend = False

    def _compute_is_mi_legajo(self):
        for rec in self:
            rec.is_mi_legajo = rec.employee_id.user_id.id == self.env.user.id

    @api.constrains("reason_description", "resolution_description", "reason_discharge", "reason_deregistration",
                    "resolution_description_deregistration")
    def _check_len_description(self):
        for record in self:
            if record.reason_description and len(record.reason_description) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.reason_discharge and len(record.reason_discharge) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.reason_deregistration and len(record.reason_deregistration) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.resolution_description and len(record.resolution_description) > 100:
                raise ValidationError(_("El campo Descripción de la resolución no puede tener más de 100 caracteres."))
            if record.resolution_description_deregistration and len(record.resolution_description_deregistration) > 100:
                raise ValidationError(_("El campo Descripción de la resolución no puede tener más de 100 caracteres."))

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        self.operating_unit_id = False

    @api.model
    def create(self, vals):
        if not vals.get('name', False) and vals.get('employee_id', False) and vals.get('sec_position', False):
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            vals.update({"name": employee.name + ' - ' + vals.get('sec_position')})
        if 'legajo_state' in vals.keys() and 'state_square_id' not in vals.keys():
            vals['state_square_id'] = self._get_state_square(vals.get('legajo_state'))
        return super(HrContract, self).create(vals)

    def write(self, values):
        if 'legajo_state' in values.keys() and 'state_square_id' not in values.keys():
            values['state_square_id'] = self._get_state_square(values.get('legajo_state')).id
        result = super(HrContract, self.suspend_security()).write(values)
        self._notify_sgh(values)
        return result

    def button_update_occupation(self):
        ctx = self._context.copy()
        ctx['default_contract_id'] = self.id
        return {
            'name': _('Actualizar ocupación'),
            'view_mode': 'form',
            'res_model': 'onsc.legajo.update.occupation.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    @api.model
    def get_history_record_action(self, history_id, res_id):
        return super(HrContract, self.with_context(model_view_form_id=self.env.ref(
            'onsc_legajo.onsc_legajo_hr_contract_view_form').id)).get_history_record_action(history_id, res_id)

    def activate_legajo_contract(self, legajo_state='active', eff_date=False, clean_destination_info=False):
        if self.eff_date and eff_date and self.eff_date > eff_date:
            raise ValidationError(_("No se puede modificar la historia del contrato para la fecha enviada."))
        vals = {'legajo_state': legajo_state}
        if eff_date:
            vals.update({'eff_date': str(eff_date)})
        else:
            vals.update({'eff_date': fields.Date.today()})
        if clean_destination_info:
            vals.update({'inciso_dest_id': False, 'operating_unit_dest_id': False})
        self.write(vals)

    def deactivate_legajo_contract(self, date_end, legajo_state='baja', eff_date=False, inciso_dest_id=False,
                                   operating_unit_dest_id=False):
        if self.eff_date and eff_date and self.eff_date > eff_date:
            raise ValidationError(_("No se puede modificar la historia del contrato para la fecha enviada."))
        vals = {'legajo_state': legajo_state}
        if legajo_state == 'baja':
            vals.update({'date_end': date_end})
        if eff_date:
            vals.update({'eff_date': str(eff_date)})
        else:
            vals.update({'eff_date': fields.Date.today()})

        vals.update({'inciso_dest_id': inciso_dest_id})
        vals.update({'operating_unit_dest_id': operating_unit_dest_id})
        self.suspend_security().write(vals)
        self.job_ids.deactivate(date_end)

    def _notify_sgh(self, values):
        for modified_field in ['sec_position', 'workplace', 'occupation_id']:
            if modified_field in values:
                self.filtered(lambda x: x.legajo_state != 'baja').write({
                    'notify_sgh': True,
                    'last_notify_user_id': self.env.user.id,
                })

    def _get_state_square(self, legajo_state):
        if legajo_state == 'incoming_commission':
            return self.env.ref('onsc_legajo.onsc_legajo_e')
        elif legajo_state == 'outgoing_commission':
            return self.env.ref('onsc_legajo.onsc_legajo_s')
        elif legajo_state == 'reserved':
            return self.env.ref('onsc_legajo.onsc_legajo_r')
        elif legajo_state == 'active':
            return self.env.ref('onsc_legajo.onsc_legajo_o')
        else:
            return self.env['onsc.legajo.state.square']

            # LEGAJO REPORT UTILITIES

    def _get_role_assignments_sorted(self, only_most_recent=False):
        current_jobs = self.job_ids.filtered(lambda x: not x.end_date or x.end_date > fields.Date.today())

        role_assignments_sorted = current_jobs.mapped('role_assignment_ids').sorted(key=lambda role_assignment_id: (
            -to_timestamp(role_assignment_id.date_start)
        ))
        if only_most_recent and len(role_assignments_sorted):
            return role_assignments_sorted[0].role_assignment_id
        else:
            return role_assignments_sorted.role_assignment_id


class HrContractHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.contract.model.history'
    _parent_model = 'hr.contract'
