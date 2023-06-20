# -*- coding: utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

REQUIRED_FIELDS = ['date_start_commission', 'reason_description', 'norm_id', 'resolution_description',
                   'resolution_date', 'resolution_type', 'regime_commission_id']


class ONSCLegajoAltaCS(models.Model):
    _name = 'onsc.legajo.alta.cs'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Alta de Comisión Saliente'
    _rec_name = 'partner_id'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_alta_vl = self.env.user.has_group('onsc_legajo.group_legajo_consulta_altas_cs')
        is_user_administrar_altas_vl = self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
        if view_type in ['form', 'tree', 'kanban'] and is_user_alta_vl and not is_user_administrar_altas_vl:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    def read(self, fields=None, load="_classic_read"):
        Partner = self.env['res.partner'].sudo()
        Office = self.env['onsc.legajo.office'].sudo()
        LegajoNorm = self.env['onsc.legajo.norm'].sudo()
        result = super().read(fields, load)
        for item in result:
            if item.get('partner_id'):
                partner_id = item['partner_id'][0]
                item['partner_id'] = (item['partner_id'][0], Partner.browse(partner_id)._custom_display_name())
            if item.get('program_project_origin_id'):
                program_project_id = item['program_project_origin_id'][0]
                item['program_project_origin_id'] = (
                    item['program_project_origin_id'][0], Office.browse(program_project_id)._custom_display_name())
            if item.get('program_project_destination_id'):
                program_project_id = item['program_project_destination_id'][0]
                item['program_project_destination_id'] = (
                    item['program_project_destination_id'][0], Office.browse(program_project_id)._custom_display_name())
            if item.get('norm_id'):
                norm_id = item['norm_id'][0]
                item['norm_id'] = (item['norm_id'][0], LegajoNorm.browse(norm_id)._custom_display_name())
        return result

    def _get_domain(self, args):
        args = expression.AND([[
            ('partner_id', '!=', self.env.user.partner_id.id)
        ], args])
        if self.user_has_groups('onsc_legajo.group_legajo_hr_inciso_alta_cs'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    '|', ('inciso_origin_id', '=', inciso_id.id),
                    '&', ('inciso_destination_id', '=', inciso_id.id), ('state', '!=', 'draft')
                ], args])
        if self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[
                    '|', ('inciso_origin_id', '=', inciso_id.id),
                    '&', ('inciso_destination_id', '=', inciso_id.id), ('state', '!=', 'draft')
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    '|', ('operating_unit_origin_id', '=', operating_unit_id.id),
                    '&', ('operating_unit_destination_id', '=', operating_unit_id.id), ('state', '!=', 'draft')
                ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super()._search(args, offset=offset, limit=limit, order=order, count=count,
                               access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def _get_default_inciso_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs') or \
                self.user_has_groups('onsc_legajo.group_legajo_hr_inciso_alta_cs'):
            return self.env.user.employee_id.job_id.contract_id.inciso_id
        return False

    @api.model
    def _get_default_ue_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs'):
            return self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return False

    partner_id = fields.Many2one('res.partner', string='CI', required=True)
    partner_id_domain = fields.Char(compute='_compute_partner_id_domain')
    employee_id = fields.Many2one('hr.employee', 'Empleados', compute='_compute_employee_id', store=True)
    cv_birthdate = fields.Date(string=u'Fecha de nacimiento', copy=False)
    cv_sex = fields.Selection([('male', 'Masculino'), ('feminine', 'Femenino')], string=u'Sexo', copy=False)
    # ORIGIN
    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True,
                                       default=lambda self: self._get_default_inciso_id(), copy=False)
    inciso_origin_id_domain = fields.Char(compute='_compute_inciso_origin_id_domain')
    is_inciso_origin_ac = fields.Boolean("El inciso de origen es AC?",
                                         related='inciso_origin_id.is_central_administration')
    operating_unit_origin_id = fields.Many2one("operating.unit", string="Unidad ejecutora", required=True,
                                               default=lambda self: self._get_default_ue_id(), copy=False)
    operating_unit_origin_id_domain = fields.Char(compute='_compute_operating_unit_origin_id_domain')
    sequence_position_origin = fields.Char(string='Secuencia Plaza')
    contract_id = fields.Many2one('hr.contract', 'Contrato', copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    program_project_origin_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto',
                                                compute='_compute_program_project_origin_id', store=True)
    program_origin = fields.Char(string='Programa', related='program_project_origin_id.programaDescripcion')
    project_origin = fields.Char(string='Proyecto', related='program_project_origin_id.proyectoDescripcion')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen', related='contract_id.regime_id')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1',
                                     related='contract_id.descriptor1_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2',
                                     related='contract_id.descriptor2_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3',
                                     related='contract_id.descriptor3_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4',
                                     related='contract_id.descriptor4_id')
    type_commission_selection = fields.Selection(
        [('1', 'Comisión de Servicio'), ('2', 'Pase en Comisión')],
        string='Tipo de comisión', compute='_compute_type_commission_selection')
    # DESTINATION
    inciso_destination_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    inciso_destination_id_domain = fields.Char(compute='_compute_inciso_destination_id_domain')
    operating_unit_destination_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    operating_unit_destination_id_domain = fields.Char(compute='_compute_operating_unit_destination_id_domain')

    program_project_destination_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto',
                                                     domain="[('inciso', '=', inciso_destination_id),('unidadEjecutora', '=', operating_unit_destination_id)]")
    program_destination = fields.Char(string='Programa',
                                      related='program_project_destination_id.programaDescripcion')
    project_destination = fields.Char(string='Proyecto',
                                      related='program_project_destination_id.proyectoDescripcion')
    regime_destination = fields.Char(string='Régimen', default='3001')
    date_start_commission = fields.Date(string='Fecha desde de la Comisión')
    department_id = fields.Many2one('hr.department', string='UO')
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión')
    reason_description = fields.Text(string='Descripción del motivo')
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma')
    norm_type = fields.Char(string="Tipo norma", related="norm_id.tipoNorma", store=True, readonly=True)
    norm_number = fields.Integer(string='Número de norma', related="norm_id.numeroNorma",
                                 store=True, readonly=True)
    norm_year = fields.Integer(string='Año de norma', related="norm_id.anioNorma", store=True,
                               readonly=True)
    norm_article = fields.Integer(string='Artículo de norma', related="norm_id.articuloNorma",
                                  store=True, readonly=True)
    resolution_description = fields.Text(string='Descripción de la resolución')
    resolution_date = fields.Date(string='Fecha de la resolución')
    resolution_type = fields.Selection(
        [('M', 'Inciso'), ('P', 'Presidencia o Poder ejecutivo'), ('U', 'Unidad ejecutora')],
        string='Tipo de resolución')
    code_regime_start_commission_id = fields.Many2one('onsc.legajo.commission.regime',
                                                      string='Código del régimen de Inicio de Comisión')
    state = fields.Selection(
        [('draft', 'Borrador'), ('to_process', 'A procesar en destino'), ('returned', 'Devuelto a origen'),
         ('cancelled', 'Cancelado'), ('error_sgh', 'Error SGH'), ('confirmed', 'Confirmado')],
        string='Estado', default='draft')
    additional_information = fields.Text(string='Información adicional')
    attached_document_ids = fields.One2many('onsc.legajo.attached.document',
                                            'alta_cs_id',
                                            string='Documentos adjuntos')
    error_reported_integration_id = fields.Many2one('onsc.legajo.integration.error',
                                                    string='Error reportado integración')

    type_cs = fields.Selection([
        ('undefined', 'No determinado'),
        ('ac2ac', 'AC a AC'),
        ('ac2out', 'AC a fuera de AC'),
        ('out2ac', 'Fuera de AC a AC ')],
        string='Tipo de movimiento',
        compute='_compute_type_cs',
        store=True
    )

    # DEFINICION COMPORTAMIENTOS
    is_edit_destination = fields.Boolean(string="Editar datos de destino", compute='_compute_is_edit_destination')
    is_edit_origin = fields.Boolean(string="Editar datos de origen", compute='_compute_is_edit_origin')
    is_available_send_to_sgh = fields.Boolean(string="Disponible para enviar a SGH",
                                              compute='_compute_is_available_send_to_sgh')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    is_available_send_origin = fields.Boolean(string="Disponible para enviar a origen",
                                              compute='_compute_is_available_send_origin')
    is_available_send_destination = fields.Boolean(string="Disponible para enviar a destino",
                                                   compute='_compute_is_available_send_destination')
    is_available_cancel = fields.Boolean(string="Disponible para cancelar",
                                         compute='_compute_is_available_cancel')
    is_edit_contract = fields.Boolean(string="Editar datos de contrato", compute='_compute_contract_id_domain')

    filter_destination = fields.Boolean(string="Filtrar destino", compute='_compute_filter_destination',
                                        search='_search_filter_destination')

    def _compute_filter_destination(self):
        for record in self:
            record.filter_destination = False

    def _search_filter_destination(self, operator, value):
        return ['|',
                '&', ('state', 'in', ['draft', 'to_process', 'error_sgh']),
                ('inciso_destination_id', '=', self.env.user.employee_id.job_id.contract_id.inciso_id.id),
                '|',
                '&', ('state', 'in', ['draft', 'returned']),
                ('inciso_origin_id', '=', self.env.user.employee_id.job_id.contract_id.inciso_id.id),
                '&', ('state', '=', 'error_sgh'),
                ('type_cs', 'in', ['ac2out', 'out2ac'])
                ]

    # DATOS DEL WS10
    nroPuesto = fields.Char(string='Puesto', copy=False)
    nroPlaza = fields.Char(string='Plaza', copy=False, )
    secPlaza = fields.Char(string="Sec Plaza")
    is_error_synchronization = fields.Boolean(copy=False)
    error_message_synchronization = fields.Char(string="Mensaje de Error", copy=False)

    @api.constrains("date_start_commission")
    def _check_date(self):
        for record in self:
            if record.date_start_commission and record.date_start_commission > fields.Date.today():
                raise ValidationError("La fecha debe ser menor o igual al día de alta")

    @api.depends('state', 'type_cs', 'inciso_origin_id')
    def _compute_should_disable_form_edit(self):
        for record in self:
            inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
            if record.state in ['draft', 'to_process', 'returned', 'error_sgh'] and self.user_has_groups(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                record.should_disable_form_edit = False
            elif record.state not in ['draft', 'to_process', 'returned', 'error_sgh']:
                record.should_disable_form_edit = True
            elif record.state == 'to_process' and record.type_cs == 'ac2ac' and record.inciso_origin_id == inciso_id:
                record.should_disable_form_edit = True
            elif record.state == 'returned' and record.type_cs == 'ac2ac' and record.inciso_destination_id == inciso_id:
                record.should_disable_form_edit = True
            else:
                record.should_disable_form_edit = False

    @api.depends('inciso_origin_id', 'inciso_destination_id')
    def _compute_type_commission_selection(self):
        for record in self:
            if record.inciso_origin_id and record.inciso_destination_id:
                if record.inciso_origin_id == record.inciso_destination_id:
                    record.type_commission_selection = '1'
                else:
                    record.type_commission_selection = '2'
            else:
                record.type_commission_selection = False

    @api.depends('employee_id')
    def _compute_contract_id_domain(self):
        Contract = self.env['hr.contract'].sudo()
        for rec in self:
            if rec.employee_id:
                contracts = Contract.search([
                    ("legajo_state", "=", 'active'),
                    ('employee_id', '=', rec.employee_id.id),
                    ('regime_id.presupuesto', '=', True),
                    ('operating_unit_id', '=', rec.operating_unit_origin_id.id)])
                if len(contracts) == 1:
                    rec.is_edit_contract = False
                else:
                    rec.is_edit_contract = True
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
            else:
                rec.contract_id_domain = json.dumps([('id', '=', False)])
                rec.is_edit_contract = False

    @api.depends('operating_unit_origin_id')
    def _compute_partner_id_domain(self):
        for record in self:
            user_partner_id = self.env.user.partner_id
            if not record.operating_unit_origin_id:
                record.partner_id_domain = json.dumps([('id', 'in', [])])
            elif record.is_inciso_origin_ac:
                partner_ids = self.env['hr.contract'].sudo().search(
                    [('operating_unit_id', '=', record.operating_unit_origin_id.id),
                     ('legajo_state', '=', 'active'),
                     ('regime_id.presupuesto', '=', True)]).mapped('employee_id.partner_id').ids
                record.partner_id_domain = json.dumps([('id', 'in', partner_ids), ('id', '!=', user_partner_id.id)])
            else:
                record.partner_id_domain = json.dumps(
                    [('is_partner_cv', '=', True), ('is_cv_uruguay', '=', True), ('id', '!=', user_partner_id.id)])

    # COMPUTES ORIGIN AND DESTINATION DOMAIN
    @api.depends('inciso_origin_id')
    def _compute_inciso_origin_id_domain(self):
        for rec in self:
            domain = []
            # Si no es admin de altas de CS, el inciso origen es el del contrato del usuario: unico que es AC
            if not self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
                inciso_id = contract.inciso_id.id if contract else False
                domain = ['|', ('id', '=', inciso_id), ('is_central_administration', '=', False)]
            rec.inciso_origin_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id')
    def _compute_inciso_destination_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            # Si el inciso origen es AC, el destino puede ser cualquier inciso
            if rec.inciso_origin_id and rec.inciso_origin_id.is_central_administration:
                domain = []
            else:
                if not self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                    # si no eres admin CSC y el inciso origen es No es AC, el inciso destino es el del contrato del usuario: unico que es AC
                    contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
                    inciso_id = contract.inciso_id.id if contract else False
                    domain = [('id', '=', inciso_id)]
                else:
                    # si eres admin CSC y el inciso origen es No es AC, todos los incisos destino son AC
                    domain = [('is_central_administration', '=', True)]
            rec.inciso_destination_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id')
    def _compute_operating_unit_origin_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_origin_id:
                domain = [('inciso_id', '=', rec.inciso_origin_id.id)]
                if rec.inciso_origin_id.is_central_administration and self.user_has_groups(
                        'onsc_legajo.group_legajo_hr_ue_alta_cs') and not (self.env.user.has_group(
                    'onsc_legajo.group_legajo_hr_inciso_alta_cs') or self.env.user.has_group(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')):
                    contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
                    operating_unit = contract.operating_unit_id.id if contract else False
                    domain = [('id', '=', operating_unit)]
            self.operating_unit_origin_id_domain = json.dumps(domain)

    @api.depends('inciso_destination_id')
    def _compute_operating_unit_destination_id_domain(self):
        for rec in self:
            contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
            operating_unit_id = contract.operating_unit_id.id if contract else False
            domain = [('inciso_id', '=', rec.inciso_destination_id.id),
                      ('id', '!=', rec.operating_unit_origin_id.id)]
            if self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs') and not (self.env.user.has_group(
                    'onsc_legajo.group_legajo_hr_inciso_alta_cs') or self.env.user.has_group(
                'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')):
                if rec.type_cs == 'out2ac':
                    domain = [('id', '=', operating_unit_id), ('id', '!=', rec.operating_unit_origin_id.id)]
            self.operating_unit_destination_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id', 'inciso_destination_id')
    def _compute_type_cs(self):
        for record in self:
            if record.inciso_origin_id and record.inciso_destination_id:
                if record.inciso_origin_id.is_central_administration and record.inciso_destination_id.is_central_administration:
                    record.type_cs = 'ac2ac'
                elif record.inciso_origin_id.is_central_administration and not record.inciso_destination_id.is_central_administration:
                    record.type_cs = 'ac2out'
                elif not record.inciso_origin_id.is_central_administration and record.inciso_destination_id.is_central_administration:
                    record.type_cs = 'out2ac'
                else:
                    record.type_cs = 'undefined'
            else:
                record.type_cs = 'undefined'

    @api.depends('contract_id')
    def _compute_program_project_origin_id(self):
        for rec in self:
            if rec.contract_id:
                rec.program_project_origin_id = self.env['onsc.legajo.office'].sudo().search(
                    [('inciso', '=', rec.contract_id.inciso_id.id),
                     ('unidadEjecutora', '=', rec.contract_id.operating_unit_id.id),
                     ('programa', '=', rec.contract_id.program), ('proyecto', '=', rec.contract_id.project)]).id
            else:
                rec.program_project_origin_id = False

    # COMPUTES COMPORTAMIENTOS
    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_origin(self):
        for record in self:
            if record.state == 'draft':
                record.is_edit_origin = True
            else:
                record.is_edit_origin = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_destination(self):
        for record in self:
            inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
            administrator_security = self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
            inciso_security = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs')
            operating_unit_security = self.env.user.has_group('onsc_legajo.group_legajo_hr_ue_alta_cs')
            if administrator_security:
                record.is_edit_destination = True
            elif record.state == 'returned':
                record.is_edit_destination = False
            # Editar por el usuario Destino
            # El Usuario logueado tiene permiso por inciso y el inciso de destino es el mismo que el del usuario
            elif record.type_cs == 'ac2ac' and inciso_security and record.inciso_destination_id == inciso_id:
                record.is_edit_destination = True
            # El Usuario logueado tiene permiso por ue y la ue de destino es el mismo que el del usuario
            elif record.type_cs == 'ac2ac' and operating_unit_security and record.operating_unit_destination_id == operating_unit_id:
                record.is_edit_destination = True
            # Editar por el usuario Origen
            # El Usuario logueado tiene permiso por ue y la ue de destino es el mismo que el del usuario
            elif record.type_cs == 'ac2ac' and record.inciso_destination_id == record.inciso_origin_id:
                record.is_edit_destination = True
            # Siempre poder editar si no es ac2ac
            elif record.type_cs != 'ac2ac':
                record.is_edit_destination = True
            else:
                record.is_edit_destination = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs')
    def _compute_is_available_send_to_sgh(self):
        for record in self:
            # AC2AC siendo tu mismo inciso origen y destino
            if record.state in ['draft', 'error_sgh'] and self.env.user.has_group(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                record.is_available_send_to_sgh = True
            elif record.state in ['draft', 'to_process',
                                  'error_sgh'] and record.type_cs == 'ac2ac' and record.inciso_origin_id == record.inciso_destination_id:
                record.is_available_send_to_sgh = True
            # No AC2AC siempre enviar a SGH
            elif record.type_cs != 'ac2ac' and record.state in ['draft',
                                                                'error_sgh'] and record.inciso_origin_id and record.inciso_destination_id:
                record.is_available_send_to_sgh = True
            # Si eres el destino y esta en estado to_process o error_sgh
            elif record.is_edit_destination and record.state in ['to_process',
                                                                 'error_sgh'] and record.type_cs == 'ac2ac':
                record.is_available_send_to_sgh = True
            else:
                record.is_available_send_to_sgh = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state')
    def _compute_is_available_send_origin(self):
        for record in self:
            if record.state == 'to_process' and record.is_edit_destination and record.type_cs == 'ac2ac':
                record.is_available_send_origin = True
            elif record.state == 'to_process' and record.type_cs == 'ac2ac' and self.env.user.has_group(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                record.is_available_send_origin = True
            else:
                record.is_available_send_origin = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state')
    def _compute_is_available_send_destination(self):
        for record in self:
            # Enviar a destino si es ac2ac y no es el mismo inciso en estado borrador o devuelto a origen
            inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
            if record.state in ['draft',
                                'returned'] and record.type_cs == 'ac2ac' and not record.is_edit_destination and record.inciso_origin_id == inciso_id:
                record.is_available_send_destination = True
            elif record.state in ['draft', 'returned'] and record.type_cs == 'ac2ac' and self.env.user.has_group(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                record.is_available_send_destination = True
            else:
                record.is_available_send_destination = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state')
    def _compute_is_available_cancel(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            if record.state not in ['draft', 'cancelled'] and self.env.user.has_group(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                record.is_available_cancel = True
            elif record.state == 'returned' and record.type_cs == 'ac2ac' and record.inciso_origin_id == inciso_id:
                record.is_available_cancel = True
            elif record.state == 'to_process' and record.type_cs == 'ac2ac' and record.inciso_destination_id == inciso_id:
                record.is_available_cancel = True
            elif record.state == 'error_sgh' and record.type_cs == 'ac2ac' and record.inciso_destination_id == inciso_id:
                record.is_available_cancel = True
            elif record.state not in ['draft', 'confirmed'] and record.type_cs != 'ac2ac':
                record.is_available_cancel = True
            else:
                record.is_available_cancel = False

    @api.depends('partner_id')
    def _compute_employee_id(self):
        Employee = self.env['hr.employee'].sudo()
        for record in self:
            if record.partner_id:
                record.employee_id = Employee.search([
                    ('partner_id', '=', record.partner_id.id)
                ], limit=1)
            else:
                record.employee_id = False

    @api.onchange('employee_id', 'partner_id')
    def onchange_employee_id(self):
        contracts = self.env['hr.contract'].sudo().search([
            ("legajo_state", "=", 'active'),
            ('employee_id', '=', self.employee_id.id),
            ('regime_id.presupuesto', '=', True),
            ('operating_unit_id', '=', self.operating_unit_origin_id.id)])
        if len(contracts) == 1:
            self.contract_id = contracts.id
        else:
            self.contract_id = False

    def get_inciso_operating_unit_by_user(self):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return inciso_id, operating_unit_id

    @api.onchange('inciso_origin_id')
    def onchange_inciso_origin_id(self):
        self.operating_unit_origin_id = False
        self.partner_id = False
        self.inciso_destination_id = False
        self.operating_unit_destination_id = False
        self.contract_id = False

    @api.onchange('operating_unit_origin_id')
    def onchange_operating_unit_origin_id(self):
        self.operating_unit_destination_id = False
        self.inciso_destination_id = False
        self.partner_id = False
        self.contract_id = False

    @api.onchange('operating_unit_origin_id', 'operating_unit_destination_id')
    def onchange_operating_units(self):
        self.program_project_destination_id = False
        self.program_destination = False
        self.project_destination = False
        self.regime_destination = False
        self.date_start_commission = False
        self.department_id = False
        self.security_job_id = False
        self.occupation_id = False
        self.regime_commission_id = False
        self.reason_description = False
        self.norm_id = False
        self.resolution_description = False
        self.resolution_date = False
        self.code_regime_start_commission_id = False
        self.additional_information = False

    @api.onchange('inciso_destination_id')
    def onchange_inciso_destination_id(self):
        self.operating_unit_destination_id = False

    @api.onchange('operating_unit_destination_id')
    def onchange_operating_unit_destination_id(self):
        self.department_id = False

    @api.onchange('operating_unit_origin_id', 'operating_unit_destination_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_destination_id and rec.operating_unit_origin_id and rec.operating_unit_origin_id == rec.operating_unit_destination_id:
                raise ValidationError('La unidad ejecutora de origen y destino no pueden ser iguales')

    def check_send_sgh(self):
        for record in self:
            message = []
            for required_field in REQUIRED_FIELDS:
                if not eval('record.%s' % required_field):
                    message.append(record._fields[required_field].string)
            if record.inciso_origin_id.is_central_administration and not record.contract_id.sec_position:
                message.append(record._fields['secPlaza'].string)
            if record.inciso_origin_id.is_central_administration and not record.inciso_origin_id:
                message.append(record._fields['inciso_origin_id'].string)
            if not record.partner_id.cv_last_name_1:
                message.append("Primer Apellido")
            if not record.partner_id.cv_first_name:
                message.append("Primer Nombre")
            if not record.operating_unit_destination_id:
                message.append(record._fields['operating_unit_destination_id'].string)
            if not record.program_project_destination_id and record.type_cs != 'ac2out':
                message.append(record._fields['program_project_destination_id'].string)
            if not record.inciso_destination_id:
                message.append(record._fields['inciso_destination_id'].string)
            if not record.attached_document_ids:
                message.append(_("Debe haber al menos un documento adjunto"))
            if not record.cv_birthdate:
                message.append(_("Fecha de nacimiento"))
            if record.type_cs != 'ac2out' and not record.department_id:
                message.append(record._fields['department_id'].string)
            if record.type_cs != 'ac2out' and not record.security_job_id:
                message.append(record._fields['security_job_id'].string)
            if record.type_cs != 'ac2out' and not record.occupation_id:
                message.append(record._fields['occupation_id'].string)
            if not record.cv_sex:
                message.append(_("Sexo"))
            if record.regime_commission_id and not record.regime_commission_id.cgn_code:
                message.append(
                    _("Falta el Código de CGN en la configuración del Régimen de comisión seleccionado. Contactar al administrador del sistema."))
            if record.is_inciso_origin_ac and record.contract_id and not record.contract_id.legajo_state == 'active':
                message.append(_("El contrato debe estar activo"))
            if record.security_job_id.is_uo_manager and record.department_id.manager_id or not self.env[
                'hr.job'].is_job_available_for_manager(
                record.department_id, record.security_job_id, record.date_start_commission):
                message.append("La UO ya tiene un responsable")
        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))
        return True

    def action_send_destination(self):
        self.state = 'to_process'
        if not self.inciso_destination_id:
            raise ValidationError(_("Debe seleccionar inciso de destino"))
        if not self.operating_unit_destination_id:
            raise ValidationError(_("Debe seleccionar una unidad ejecutora de destino"))

    def action_send_origin(self):
        self.state = 'returned'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_send_sgh(self):
        self.check_send_sgh()
        self.env['onsc.legajo.abstract.alta.cs.ws10'].with_context(
            log_info=True, altas_cs=self).suspend_security().syncronize(self)

    def action_aprobado_cgn(self):
        if self.type_cs == 'out2ac':
            employee = self._get_legajo_employee()
            self._get_legajo(employee)
        else:
            employee = self.employee_id
        new_contract = self._get_legajo_contract(employee)
        self.contract_id.suspend_security().write({'cs_contract_id': new_contract.id})
        date_start = fields.Date.from_string(self.date_start_commission)
        self.contract_id.deactivate_legajo_contract(
            date_end=date_start - relativedelta(days=1),
            legajo_state='outgoing_commission'
        )
        self.write({
            'state': 'confirmed',
            'is_error_synchronization': False,
            'error_message_synchronization': ''
        })

    def _get_legajo_employee(self):
        cv_emissor_country_id = self.env.ref('base.uy')
        cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([
            ('code', '=', 'ci')], limit=1)
        return self.env['hr.employee']._get_legajo_employee(cv_emissor_country_id, cv_document_type_id, self.partner_id)

    def _get_legajo(self, employee):
        return self.env['onsc.legajo']._get_legajo(employee)

    def _get_legajo_contract(self, employee_id=False):
        Contract = self.env['hr.contract']
        origin_contract_id = self.contract_id
        employee = employee_id or self.employee_id
        vals = {
            'employee_id': employee.id,
            'name': employee.name,
            'date_start': self.date_start_commission or fields.Date.today(),
            'inciso_id': self.inciso_destination_id.id,
            'operating_unit_id': self.operating_unit_destination_id.id,
            'income_mechanism_id': origin_contract_id.income_mechanism_id.id,
            'program': self.program_project_destination_id.programa,
            'project': self.program_project_destination_id.proyecto,
            'regime_id': origin_contract_id.regime_id.id,
            'occupation_id': self.occupation_id.id,
            'descriptor1_id': origin_contract_id.descriptor1_id.id,
            'descriptor2_id': origin_contract_id.descriptor2_id.id,
            'descriptor3_id': origin_contract_id.descriptor3_id.id,
            'descriptor4_id': origin_contract_id.descriptor4_id.id,
            'position': self.nroPuesto,
            'workplace': self.nroPlaza,
            'sec_position': self.secPlaza,
            'graduation_date': origin_contract_id.graduation_date,
            'reason_description': self.reason_description,
            'norm_code_id': self.norm_id.id,
            'resolution_description': self.resolution_description,
            'resolution_date': self.resolution_date,
            'resolution_type': self.resolution_type,
            'call_number': origin_contract_id.call_number,
            'additional_information': self.additional_information,
            'code_day': origin_contract_id.retributive_day_id.codigoJornada,
            'description_day': origin_contract_id.retributive_day_id.descripcionJornada,
            'retributive_day_id': origin_contract_id.retributive_day_id.id,
            'wage': 1,
            'cs_contract_id': origin_contract_id.id,
            'commission_regime_id': self.regime_commission_id.id,
        }
        contract = Contract.suspend_security().create(vals)

        for document_record in self.attached_document_ids:
            document_record.write({
                'contract_id': contract.id,
                'type': 'discharge'})

        contract.activate_legajo_contract(legajo_state='incoming_commission')
        return contract

    def _get_legajo_job(self, contract):
        return self.env['hr.job'].create_job(contract, self.department_id, self.date_start_commission,
                                             self.security_job_id)

    def unlink(self):
        if self.filtered(lambda x: x.state != 'draft'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super().unlink()
