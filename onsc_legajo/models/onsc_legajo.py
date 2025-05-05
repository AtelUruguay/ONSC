# -*- coding: utf-8 -*-
import json

from lxml import etree

from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError


class ONSCLegajo(models.Model):
    _name = "onsc.legajo"
    _inherit = ['onsc.legajo.abstract.legajo.security', 'model.history']
    _history_model = 'onsc.legajo.history'
    _rec_name = "employee_id"
    _order = "employee_id"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        valid_groups = self.user_has_groups(
            'onsc_legajo.group_legajo_configurador,onsc_legajo.group_legajo_hr_admin,onsc_legajo.group_legajo_hr_inciso,onsc_legajo.group_legajo_hr_ue')
        if view_type in ['form', 'tree', 'kanban'] and not valid_groups:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Funcionario",
        required=True,
        index=True)

    emissor_country_id = fields.Many2one('res.country', u'País emisor del documento',
                                         related='employee_id.cv_emissor_country_id', store=True)
    document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento',
                                       related='employee_id.cv_document_type_id', store=True)
    nro_doc = fields.Char(u'Número de documento', related='employee_id.cv_nro_doc', store=True)

    full_name = fields.Char(u'Nombre', related='employee_id.full_name', store=True)
    first_name = fields.Char(u'Primer nombre', related='employee_id.cv_first_name', store=True)
    second_name = fields.Char(u'Segundo nombre', related='employee_id.cv_second_name', store=True)
    last_name_1 = fields.Char(u'Primer apellido', related='employee_id.cv_last_name_1', store=True)
    last_name_2 = fields.Char(u'Segundo apellido', related='employee_id.cv_last_name_2', store=True)

    image_1920 = fields.Image(string='Foto', max_width=1920, max_height=1920,
                              related='employee_id.image_1920', store=True)
    avatar_128 = fields.Image(string='Avatar 128', max_width=128, max_height=128,
                              related='employee_id.avatar_128', store=True)

    public_admin_entry_date = fields.Date(string=u'Fecha de ingreso a la administración pública')
    public_admin_inactivity_years_qty = fields.Integer(string=u'Años de inactividad')

    contract_ids = fields.One2many('hr.contract', compute='_compute_contract_info')
    contracts_count = fields.Integer(string='Cantidad de contratos', compute='_compute_contract_info')

    is_mi_legajo = fields.Boolean(string="¿Es mi legajo?", compute='_compute_is_mi_legajo')
    is_any_regime_legajo = fields.Boolean(string=u'¿Algún Régimen de los Contratos tiene la marca Legajo?',
                                          compute='_compute_is_any_regime_legajo')
    show_legajo_info = fields.Boolean(string=u'¿Ver información de legajo?', compute='_compute_show_legajo_info')
    show_legajo_basic_info = fields.Boolean(string=u'¿Ver información de legajo?', compute='_compute_show_legajo_info')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_is_mi_legajo')
    should_hidde_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                            compute='_compute_is_mi_legajo')

    juramento_bandera_date = fields.Date(
        string='Fecha de Juramento de fidelidad a la Bandera nacional', history=True)
    juramento_bandera_presentacion_date = fields.Date(
        string='Fecha de presentación de documento digitalizado', history=True)
    juramento_bandera_file = fields.Binary("Documento digitalizado", history=True)
    juramento_bandera_filename = fields.Char('Nombre del Documento digitalizado')

    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado del funcionario',
        related='employee_id.legajo_state',
        store=True
    )

    job_ids = fields.One2many(
        comodel_name='hr.job',
        inverse_name='legajo_id',
        string='Puestos')

    declaration_law_ids = fields.One2many(
        comodel_name='onsc.legajo.declaration.law',
        inverse_name='legajo_id',
        string="Declaraciones de Ley")
    judicial_antecedents_ids = fields.One2many(
        comodel_name='onsc.legajo.judicial.antecedents',
        inverse_name='legajo_id',
        string="Antecedentes judiciales")
    other_information_ids = fields.One2many(
        comodel_name='onsc.legajo.other.information',
        inverse_name='legajo_id',
        string="Otra información")
    merito_ids = fields.One2many(
        comodel_name="onsc.legajo.merito",
        inverse_name="legajo_id",
        string="Méritos")
    demerito_ids = fields.One2many(
        comodel_name="onsc.legajo.demerito",
        inverse_name="legajo_id",
        string="Deméritos")
    vote_registry_ids = fields.One2many(
        comodel_name="onsc.legajo.vote.registry",
        inverse_name="legajo_id",
        string="Registro de votos",
        context={'ignore_restrict': True, 'ignore_base_restrict': True}
    )
    is_vote_registry_editable = fields.Boolean(
        string='¿Control de votos editable desde Legajo?',
        compute='_compute_is_vote_registry_editable'
    )
    # helper para pasar un domain dinamico al o2m de control de votos
    electoral_act_ids_domain = fields.Char(
        string='Elecciones disponibles',
        compute="_compute_electoral_act_ids_domain")

    summary_ids = fields.One2many(
        comodel_name="onsc.legajo.summary",
        inverse_name="legajo_id",
        string="Sumarios")
    show_legajo_summary = fields.Boolean(string=u'¿Ver información de Sumarios?', compute='_compute_show_legajo_info')
    last_sync_rve_date = fields.Date(u'Última sincronización con RVE', compute='_compute_last_sync_rve_date')

    @api.depends('vote_registry_ids', 'vote_registry_ids.electoral_act_ids')
    def _compute_electoral_act_ids_domain(self):
        ElectoralAct = self.env['onsc.legajo.electoral.act'].suspend_security().with_context(active_test=False)
        if self._context.get('restrict_period'):
            electoral_act_ids = ElectoralAct.search([
                ('date_since_entry_control', '<=', fields.Date.today()),
                ('date_until_entry_control', '>=', fields.Date.today())])
        else:
            electoral_act_ids = ElectoralAct
        for rec in self:
            if self._context.get('restrict_period'):
                rec.electoral_act_ids_domain = json.dumps([
                    ("id", "in", electoral_act_ids.ids),
                    ("id", "not in", rec.vote_registry_ids.mapped('electoral_act_ids').ids)
                ])
            else:
                rec.electoral_act_ids_domain = json.dumps([
                    ("id", "not in", rec.vote_registry_ids.mapped('electoral_act_ids').ids)
                ])

    def _compute_contract_info(self):
        for record in self:
            available_contracts = record._get_user_available_contract(record.employee_id)
            record.contract_ids = available_contracts
            record.contracts_count = len(available_contracts)

    def _compute_is_vote_registry_editable(self):
        is_vote_registry_editable = self.user_has_groups('onsc_legajo.group_legajo_vote_control_gestor')
        for rec in self:
            rec.is_vote_registry_editable = is_vote_registry_editable

    @api.constrains('juramento_bandera_date', 'juramento_bandera_presentacion_date')
    def _check_juramento_bandera_date(self):
        for rec in self:
            if rec.juramento_bandera_date and rec.juramento_bandera_date > fields.Date.today():
                raise ValidationError(
                    _("La Fecha de Juramento de fidelidad a la Bandera nacional debe ser menor o igual a hoy"))
            if rec.juramento_bandera_presentacion_date and rec.juramento_bandera_presentacion_date > fields.Date.today():
                raise ValidationError(
                    _("La Fecha de presentación de documento digitalizado debe ser menor o igual a hoy"))
            _is_both_fields = rec.juramento_bandera_presentacion_date and rec.juramento_bandera_date
            if _is_both_fields and rec.juramento_bandera_presentacion_date < rec.juramento_bandera_date:
                raise ValidationError(
                    _("La Fecha de presentación de documento digitalizado debe ser mayor a la Fecha de juramento"))

    @api.model
    def create(self, vals):
        legajo = super(ONSCLegajo, self).create(vals)
        self.env['onsc.legajo.summary']._update_empty_legajo_records(legajo)
        return legajo

    def write(self, vals):
        keys_to_check = {'juramento_bandera_date', 'juramento_bandera_presentacion_date', 'juramento_bandera_file'}
        any_juramento_in_vals = any(key in vals for key in keys_to_check)
        if any_juramento_in_vals and 'eff_date' not in vals:
            vals['eff_date'] = fields.Date.today()
            return super(ONSCLegajo, self.suspend_security()).write(vals)
        else:
            return super(ONSCLegajo, self).write(vals)

    def button_open_contract(self):
        self.ensure_one()
        if self.contracts_count == 0:
            return True
        elif self.contracts_count == 1:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_hr_contract_action')
            action.update({
                'res_id': self.contract_ids[0].id
            })
        else:
            action = self.env["ir.actions.actions"]._for_xml_id(
                'onsc_legajo.onsc_legajo_hr_contract_list_readonly_action')
            _context = self._context.copy()
            _context.update({
                'create': False,
                'edit': False,
                'is_legajo': True,
                'filter_contracts': True,
                'from_smart_button': True
            })
            action.update({
                'context': str(_context),
                'domain': [('id', 'in', self.contract_ids.ids)]
            })
        return action

    def _compute_is_mi_legajo(self):
        for rec in self:
            is_mi_legajo = rec.employee_id.user_id.id == self.env.user.id
            rec.is_mi_legajo = is_mi_legajo
            rec.should_disable_form_edit = is_mi_legajo
            rec.should_hidde_form_edit = is_mi_legajo

    def _compute_is_any_regime_legajo(self):
        for rec in self:
            rec.is_any_regime_legajo = len(rec.sudo().contract_ids.filtered(lambda x: x.regime_id.is_legajo)) > 0

    def _compute_show_legajo_info(self):
        is_user_valid = self.user_has_groups('onsc_legajo.group_legajo_show_legajo_info')
        is_user_basic_valid = self.user_has_groups('onsc_legajo.group_legajo_show_basic_legajo_info')
        is_user_valid_summary = self.user_has_groups('onsc_legajo.group_legajo_summary_consulta')
        for rec in self:
            rec.show_legajo_info = is_user_valid or rec.employee_id.user_id.id == self.env.user.id
            rec.show_legajo_basic_info = is_user_basic_valid or rec.employee_id.user_id.id == self.env.user.id
            rec.show_legajo_summary = is_user_valid_summary or rec.employee_id.user_id.id == self.env.user.id

    def _compute_last_sync_rve_date(self):
        cron = self.env.ref("onsc_legajo.legajo_summary", raise_if_not_found=False)
        lastcall = cron and cron.lastcall or False
        for rec in self:
            rec.last_sync_rve_date = lastcall

    @api.depends('summary_ids.last_update_date')
    def _compute_last_sync_rve_date(self):
        for record in self:
            fechas = [d for d in record.summary_ids.mapped('last_update_date') if d]
            record.last_sync_rve_date = max(fechas) if fechas else False

    def button_open_employee(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_employee_action')
        action['res_id'] = self.employee_id.id
        return action

    def button_rve_history(self):
        try:
            self.ensure_one()
            rve_document = self.env['onsc.legajo.abstract.ws.rve'].suspend_security().syncronize(self)
            attachment_name = _("Historial RVE Funcionario %s.pdf") % self.full_name
            attachment = self.env["ir.attachment"].create({
                "name": attachment_name,
                "datas": bytes(rve_document, 'utf-8'),
                "type": "binary",
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": self.id,
            })
            url = "{}/web/content/ir.attachment/{}/datas/{}".format(
                self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
                attachment.id,
                attachment.name,
            )
            return {
                "type": "ir.actions.act_url",
                "target": "new",
                "url": url,
            }
        except Exception as e:
            raise ValidationError(_("Error al obtener la Historia laboral. Detalle: %s" % tools.ustr(e)))

    def button_rve_history_test(self):
        try:
            self.ensure_one()
            rve_document = self.env['onsc.legajo.abstract.ws.rve'].with_context(
                test=True).suspend_security().syncronize(self)
            attachment_name = _("Historial RVE Funcionario %s.pdf") % self.full_name
            attachment = self.env["ir.attachment"].create({
                "name": attachment_name,
                "datas": bytes(rve_document, 'utf-8'),
                "type": "binary",
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": self.id,
            })
            url = "{}/web/content/ir.attachment/{}/datas/{}?download=true".format(
                self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
                attachment.id,
                attachment.name,
            )
            return {
                "type": "ir.actions.act_url",
                "target": "new",
                "url": url,
            }
        except Exception as e:
            raise ValidationError(_("Error al obtener la Historia laboral. Detalle: %s" % tools.ustr(e)))

    def button_open_current_summary(self):
        action = self.sudo().env.ref('onsc_legajo.onsc_legajo_summary_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def _action_milegajo(self):
        ctx = self.env.context.copy()
        ctx['mi_legajo'] = True
        ctx['is_legajo'] = True
        mi_legajo = self.sudo().with_context(mi_legajo=True, is_legajo=True).search(
            [('employee_id', '=', self.env.user.employee_id.id)], limit=1).id
        if mi_legajo:
            view_mode = 'form'
        else:
            view_mode = 'kanban'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': self._name,
            'name': 'Mi legajo',
            'context': ctx,
            "target": "main",
            "res_id": mi_legajo,
        }

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador,onsc_legajo.group_legajo_hr_admin,onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_inciso,onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_ue,onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')

    # INTELIGENCIA DE ENTIDAD
    def _get_legajo(
            self,
            employee,
            entry_date=False,
            inactivity_years=False,
            juramento_bandera_date=False,
            juramento_bandera_presentacion_date=False,
            juramento_bandera_file=False,
            juramento_bandera_filename=False,
    ):
        """
        Si existe un legajo para ese Empleado lo devuelve sino lo crea
        :param employee: Recordset a hr.employee
        :param entry_date: Fecha de ingreso a la administracion publica
        :param inactivity_years: Cantidad de anios de inactividad
        :param juramento_bandera_.... : Info del juramento a la bandera
        :return: nuevo recordet de onsc.legajo
        """
        Legajo = self.suspend_security()
        legajo = Legajo.search([('employee_id', '=', employee.id)], limit=1)
        if not legajo:
            legajo = Legajo.create({
                'employee_id': employee.id,
                'public_admin_entry_date': entry_date,
                'public_admin_inactivity_years_qty': inactivity_years,
                'juramento_bandera_date': juramento_bandera_date,
                'juramento_bandera_presentacion_date': juramento_bandera_presentacion_date,
                'juramento_bandera_file': juramento_bandera_file,
                'juramento_bandera_filename': juramento_bandera_filename,
            })
        else:
            vals2update = {}
            if juramento_bandera_date and legajo.juramento_bandera_date != juramento_bandera_date:
                vals2update['juramento_bandera_date'] = juramento_bandera_date
            if juramento_bandera_presentacion_date and \
                    legajo.juramento_bandera_presentacion_date != juramento_bandera_presentacion_date:
                vals2update['juramento_bandera_presentacion_date'] = juramento_bandera_presentacion_date
            if juramento_bandera_file and legajo.juramento_bandera_file != juramento_bandera_file:
                vals2update['juramento_bandera_file'] = juramento_bandera_file
                vals2update['juramento_bandera_filename'] = juramento_bandera_filename
            legajo.write(vals2update)
        return legajo


class ONSCLegajoHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.legajo.history'
    _parent_model = 'onsc.legajo'
