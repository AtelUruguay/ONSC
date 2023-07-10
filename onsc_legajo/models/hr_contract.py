# -*- coding:utf-8 -*-
import json

from lxml import etree

from odoo import fields, models, api, _
from odoo.osv import expression


class HrContract(models.Model):
    _name = 'hr.contract'
    _rec_name = 'legajo_name'
    _inherit = ['hr.contract', 'model.history']
    _history_model = 'hr.contract.model.history'

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
            'onsc_legajo.group_legajo_configurador_legajo')
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

    legajo_name = fields.Char(string="Nombre", compute='_compute_legajo_name', store=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', history=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", history=True)

    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen', history=True)
    operating_unit_origin_id = fields.Many2one("operating.unit", string="Unidad ejecutora origen", history=True)
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    sec_position = fields.Char(string="Sec Plaza", required=True, history=True)
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso', history=True)
    call_number = fields.Char(string='Número de llamado', history=True)
    legajo_state = fields.Selection(
        [('active', 'Activo'), ('baja', 'Baja'), ('outgoing_commission', 'Comisión saliente'),
         ('incoming_commission', 'Comisión entrante')], string='Estado', history=True)
    cs_contract_id = fields.Many2one('hr.contract', string='Contrato comisión', history=True)
    first_name = fields.Char(string=u'Primer nombre', related='employee_id.cv_first_name')
    second_name = fields.Char(string=u'Segundo nombre', related='employee_id.cv_second_name')
    last_name_1 = fields.Char(string=u'Primer apellido', related='employee_id.cv_last_name_1')
    last_name_2 = fields.Char(string=u'Segundo apellido', related='employee_id.cv_last_name_2')
    emissor_country_id = fields.Many2one('res.country', string=u'País emisor del documento',
                                         related='employee_id.cv_emissor_country_id')
    document_type_id = fields.Many2one('onsc.cv.document.type', string=u'Tipo de documento',
                                       related='employee_id.cv_document_type_id')
    nro_doc = fields.Char(u'Número de documento', related='employee_id.cv_nro_doc')
    program = fields.Char(string='Programa', history=True)
    project = fields.Char(string='Proyecto', history=True)
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', history=True)
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', history=True)
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
    workplace_state = fields.Char(string='Estado de la plaza', history=True)
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
    job_ids = fields.One2many('hr.job', 'contract_id', string='Puestos')
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión', history=True)

    show_button_update_occupation = fields.Boolean(compute='_compute_show_button_update_occupation')
    is_mi_legajo = fields.Boolean(compute='_compute_is_mi_legajo')
    notify_sgh = fields.Boolean("Notificar SGH")

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

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        self.operating_unit_id = False

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

    def _compute_show_button_update_occupation(self):
        for rec in self:
            is_valid_group = self.env.user.has_group(
                'onsc_legajo.group_legajo_editar_ocupacion_contrato')
            is_valid_state = rec.legajo_state != 'baja'
            rec.show_button_update_occupation = is_valid_group and is_valid_state

    def _compute_is_mi_legajo(self):
        for rec in self:
            rec.is_mi_legajo = rec.employee_id.user_id.id == self.env.user.id

    @api.model
    def get_history_record_action(self, history_id, res_id):
        return super(HrContract, self.with_context(model_view_form_id=self.env.ref(
            'onsc_legajo.onsc_legajo_hr_contract_view_form').id)).get_history_record_action(history_id, res_id)

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

    def activate_legajo_contract(self, legajo_state='active'):
        self.write({'legajo_state': legajo_state})

    def deactivate_legajo_contract(self, date_end, legajo_state='baja'):
        vals = {'legajo_state': legajo_state}
        if legajo_state == 'baja':
            vals.update({'date_end': date_end})
        self.suspend_security().write(vals)
        self.suspend_security().job_ids.deactivate(date_end)

    @api.model
    def create(self, vals):
        if not vals.get('name', False) and vals.get('employee_id', False) and vals.get('sec_position', False):
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            vals.update({"name": employee.name + ' - ' + vals.get('sec_position')})

        return super(HrContract, self).create(vals)

    def write(self, values):
        for modified_field in ['sec_position', 'workplace', 'occupation_id']:
            if modified_field in values:
                values.update({
                    'notify_sgh': True
                })
        return super(HrContract, self.suspend_security()).write(values)


class HrContractHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.contract.model.history'
    _parent_model = 'hr.contract'
