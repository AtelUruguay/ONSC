# -*- coding: utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

REQUIRED_FIELDS = [
    'date_start_commission',
    'reason_description',
    'norm_id',
    'resolution_description',
    'regime_commission_id',
]


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
        if self.user_has_groups(
                'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs,onsc_legajo.group_legajo_consulta_altas_cs'):
            args = args
        elif self.user_has_groups('onsc_legajo.group_legajo_hr_inciso_alta_cs'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    '|', '|', ('inciso_origin_id', '=', inciso_id.id),
                    '&', ('is_inciso_origin_ac', '=', False), ('inciso_destination_id', '=', inciso_id.id),
                    '&', ('inciso_destination_id', '=', inciso_id.id), ('state', '!=', 'draft')
                ], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[
                    '|', '|', ('inciso_origin_id', '=', inciso_id.id),
                    '&', ('is_inciso_origin_ac', '=', False), ('inciso_destination_id', '=', inciso_id.id),
                    '&', ('inciso_destination_id', '=', inciso_id.id), ('state', '!=', 'draft')
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    '|', '|', ('operating_unit_origin_id', '=', operating_unit_id.id),
                    '&', ('is_inciso_origin_ac', '=', False),
                    ('operating_unit_destination_id', '=', operating_unit_id.id),
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

    partner_id = fields.Many2one('res.partner', string='CI', copy=False)
    partner_id_domain = fields.Char(compute='_compute_partner_id_domain')
    employee_id = fields.Many2one('hr.employee', 'Empleados', compute='_compute_employee_id', store=True)
    cv_birthdate = fields.Date(string=u'Fecha de nacimiento', copy=False)
    cv_sex = fields.Selection([('male', 'Masculino'), ('feminine', 'Femenino')], string=u'Sexo', copy=False)
    # ORIGIN
    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen',
                                       default=lambda self: self._get_default_inciso_id(), copy=False)
    inciso_origin_id_domain = fields.Char(compute='_compute_inciso_origin_id_domain')
    operating_unit_origin_id = fields.Many2one("operating.unit", string="Unidad ejecutora origen",
                                               default=lambda self: self._get_default_ue_id(), copy=False)
    operating_unit_origin_id_domain = fields.Char(compute='_compute_operating_unit_origin_id_domain')
    sequence_position_origin = fields.Char(string='Secuencia Plaza')
    contract_id = fields.Many2one('hr.contract', 'Contrato', copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    program_project_origin_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto',
                                                compute='_compute_program_project_origin_id', store=True)
    is_inciso_origin_ac = fields.Boolean(
        "El inciso de origen es AC?",
        related='inciso_origin_id.is_central_administration', store=True)
    program_origin = fields.Char(string='Programa', related='program_project_origin_id.programaDescripcion')
    project_origin = fields.Char(string='Proyecto', related='program_project_origin_id.proyectoDescripcion')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen', related='contract_id.regime_id')
    is_regime_manager = fields.Boolean(compute='_compute_is_regime_manager', store=True)
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
    inciso_destination_id = fields.Many2one('onsc.catalog.inciso', string='Inciso destino', copy=False)
    inciso_destination_id_domain = fields.Char(compute='_compute_inciso_destination_id_domain')
    operating_unit_destination_id = fields.Many2one("operating.unit", string="Unidad ejecutora destino", copy=False)
    operating_unit_destination_id_domain = fields.Char(compute='_compute_operating_unit_destination_id_domain')

    program_project_destination_id = fields.Many2one(
        'onsc.legajo.office',
        string='Programa - Proyecto',
        copy=False,
        domain="[('inciso', '=', inciso_destination_id),('unidadEjecutora', '=', operating_unit_destination_id)]",
        readonly=False, states={'confirmed': [('readonly', True)],
                                'cancelled': [('readonly', True)]})
    program_destination = fields.Char(string='Programa',
                                      related='program_project_destination_id.programaDescripcion')
    project_destination = fields.Char(string='Proyecto',
                                      related='program_project_destination_id.proyectoDescripcion')
    date_start_commission = fields.Date(string='Fecha desde de la Comisión', copy=False,
                                        readonly=False, states={'confirmed': [('readonly', True)],
                                                                'cancelled': [('readonly', True)]})
    date_end_commission = fields.Date(string='Fecha hasta de la Comisión', copy=False,
                                        readonly=False, states={'confirmed': [('readonly', True)],
                                                                'cancelled': [('readonly', True)]})
    department_id = fields.Many2one('hr.department', string='UO', copy=False,
                                    readonly=False, states={'confirmed': [('readonly', True)],
                                                            'cancelled': [('readonly', True)]})
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto", copy=False,
                                      readonly=False, states={'confirmed': [('readonly', True)],
                                                              'cancelled': [('readonly', True)]})
    security_job_id_domain = fields.Char(compute='_compute_security_job_id_domain')
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?")
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones', copy=False,
        readonly=False, states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]})
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', copy=False,
                                    readonly=False, states={'confirmed': [('readonly', True)],
                                                            'cancelled': [('readonly', True)]})
    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión', copy=False,
                                           readonly=False, states={'confirmed': [('readonly', True)],
                                                                   'cancelled': [('readonly', True)]})
    reason_description = fields.Text(string='Descripción del motivo', copy=False,
                                     readonly=False, states={'confirmed': [('readonly', True)],
                                                             'cancelled': [('readonly', True)]})
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma',
                              readonly=False, states={'confirmed': [('readonly', True)],
                                                      'cancelled': [('readonly', True)]})
    norm_type = fields.Char(string="Tipo norma", related="norm_id.tipoNorma", store=True, readonly=True)
    norm_number = fields.Integer(string='Número de norma', related="norm_id.numeroNorma",
                                 store=True, readonly=True)
    norm_year = fields.Integer(string='Año de norma', related="norm_id.anioNorma", store=True,
                               readonly=True)
    norm_article = fields.Integer(string='Artículo de norma', related="norm_id.articuloNorma",
                                  store=True, readonly=True)
    resolution_description = fields.Text(string='Descripción de la resolución',
                                         readonly=False, states={'confirmed': [('readonly', True)],
                                                                 'cancelled': [('readonly', True)]})
    resolution_date = fields.Date(string='Fecha de la resolución',
                                  readonly=False, states={'confirmed': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]})
    resolution_type = fields.Selection(
        [('M', 'Inciso'), ('P', 'Presidencia o Poder ejecutivo'), ('U', 'Unidad ejecutora')],
        string='Tipo de resolución',
        readonly=False, states={'confirmed': [('readonly', True)],
                                'cancelled': [('readonly', True)]})
    code_regime_start_commission_id = fields.Many2one('onsc.legajo.commission.regime',
                                                      string='Código del régimen de Inicio de Comisión', copy=False)
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('to_process', 'A procesar en destino'),
         ('returned', 'Devuelto a origen'),
         ('cancelled', 'Cancelado'),
         ('error_sgh', 'Error SGH'),
         ('confirmed', 'Confirmado')],
        string='Estado',
        tracking=True,
        default='draft')
    additional_information = fields.Text(string='Información adicional', copy=False,
                                         readonly=False, states={'confirmed': [('readonly', True)],
                                                                 'cancelled': [('readonly', True)]})
    attached_document_ids = fields.One2many('onsc.legajo.attached.document',
                                            'alta_cs_id', copy=False,
                                            string='Documentos adjuntos',
                                            readonly=False, states={'confirmed': [('readonly', True)],
                                                                    'cancelled': [('readonly', True)]})
    error_reported_integration_id = fields.Many2one('onsc.legajo.integration.error', copy=False,
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
    norm_id_domain = fields.Char(compute='_compute_norm_id_domain')

    # DATOS DEL WS10
    nroPuesto = fields.Char(string='Puesto', copy=False)
    nroPlaza = fields.Char(string='Plaza', copy=False, )
    secPlaza = fields.Char(string="Sec Plaza")
    is_error_synchronization = fields.Boolean(copy=False)
    error_message_synchronization = fields.Char(string="Mensaje de Error", copy=False)

    def _search_filter_destination(self, operator, value):
        employee_inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        if self.user_has_groups(
                'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs,onsc_legajo.group_legajo_consulta_altas_cs'):
            return [('state', 'not in', ['cancelled', 'confirmed'])]
        return ['|',
                '&', ('state', 'in', ['draft', 'to_process', 'error_sgh']),
                ('inciso_destination_id', '=', employee_inciso_id),
                '|',
                '&', ('state', 'in', ['draft', 'returned']),
                ('inciso_origin_id', '=', employee_inciso_id),
                '&', ('state', '=', 'error_sgh'),
                ('type_cs', 'in', ['ac2out', 'out2ac'])
                ]

    def _compute_filter_destination(self):
        for record in self:
            record.filter_destination = False

    @api.depends('state', 'type_cs', 'inciso_origin_id')
    def _compute_should_disable_form_edit(self):
        is_user_inciso = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs')
        is_user_ue = self.env.user.has_group('onsc_legajo.group_legajo_hr_ue_alta_cs')
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            # DESTINATION CONDITIONS
            is_editable_dest_inciso = record.inciso_destination_id == inciso_id and is_user_inciso
            is_editable_dest_ue = record.operating_unit_destination_id == operating_unit_id and is_user_ue
            is_editable_dest = is_editable_dest_inciso or is_editable_dest_ue
            # ORIGIN CONDITIONS
            is_editable_orig_inciso = record.inciso_origin_id == inciso_id and is_user_inciso
            is_editable_orig_ue = record.operating_unit_origin_id == operating_unit_id and is_user_ue
            is_editable_orig = is_editable_orig_inciso or is_editable_orig_ue
            if record.state in ['draft', 'to_process', 'returned', 'error_sgh'] and self.user_has_groups(
                    'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                record.should_disable_form_edit = False
            elif record.state not in ['draft', 'to_process', 'returned', 'error_sgh']:
                record.should_disable_form_edit = True
            elif record.state == 'to_process' and record.type_cs == 'ac2ac' and not is_editable_dest:
                record.should_disable_form_edit = True
            elif record.state == 'returned' and record.type_cs == 'ac2ac' and not is_editable_orig:
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
                rec.is_edit_contract = len(contracts) > 1
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
            else:
                rec.is_edit_contract = False
                rec.contract_id_domain = json.dumps([('id', '=', False)])

    @api.depends('operating_unit_origin_id', 'is_inciso_origin_ac')
    def _compute_partner_id_domain(self):
        user_partner_id = self.env.user.partner_id
        for record in self:
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
        contract = self.env.user.employee_id.job_id.contract_id
        for rec in self:
            # Si no es admin de altas de CS, el inciso origen es el del contrato del usuario: unico que es AC
            if self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                domain = []
            else:
                domain = ['|', ('id', '=', contract.inciso_id.id), ('is_central_administration', '=', False)]
            rec.inciso_origin_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id')
    def _compute_inciso_destination_id_domain(self):
        contract = self.env.user.employee_id.job_id.contract_id
        for rec in self:
            if rec.inciso_origin_id and rec.inciso_origin_id.is_central_administration:
                domain = []
            else:
                if not self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs'):
                    # si no eres admin CSC y el inciso origen es No es AC, el inciso destino es el del contrato del usuario: unico que es AC
                    domain = [('id', '=', contract.inciso_id.id)]
                else:
                    # si eres admin CSC y el inciso origen es No es AC, todos los incisos destino son AC
                    domain = [('is_central_administration', '=', True)]
            rec.inciso_destination_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id')
    def _compute_operating_unit_origin_id_domain(self):
        contract = self.env.user.employee_id.job_id.contract_id
        condition1 = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs') or self.env.user.has_group(
            'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
        condition2 = self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs')
        for rec in self:
            is_ac = rec.inciso_origin_id.is_central_administration
            if is_ac and not condition1 and condition2:
                domain = [('id', '=', contract.operating_unit_id.id)]
            elif rec.inciso_origin_id:
                domain = [('inciso_id', '=', rec.inciso_origin_id.id)]
            else:
                domain = [('id', 'in', [])]
            rec.operating_unit_origin_id_domain = json.dumps(domain)

    @api.depends('inciso_destination_id', 'type_cs')
    def _compute_operating_unit_destination_id_domain(self):
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        group1 = self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs')
        group2 = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs') or self.env.user.has_group(
            'onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
        for rec in self:
            if group1 and not group2 and rec.type_cs == 'out2ac':
                domain = [
                    ('id', '=', operating_unit_id),
                    ('id', '!=', rec.operating_unit_origin_id.id)
                ]
            else:
                domain = [
                    ('inciso_id', '=', rec.inciso_destination_id.id),
                    ('id', '!=', rec.operating_unit_origin_id.id)
                ]
            self.operating_unit_destination_id_domain = json.dumps(domain)

    @api.depends('inciso_destination_id')
    def _compute_norm_id_domain(self):
        for rec in self:
            if rec.inciso_destination_id.is_central_administration:
                _args = [('inciso_ids', 'in', [rec.inciso_destination_id.id])]
            else:
                _args = []
            rec.norm_id_domain = json.dumps(_args)

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

    @api.depends('type_cs', 'regime_origin_id')
    def _compute_is_regime_manager(self):
        Regime = self.env['onsc.legajo.regime'].sudo()
        for record in self:
            if record.type_cs == 'out2ac':
                record.is_regime_manager = Regime.search_count([('is_fac2ac', '=', True), ('is_manager', '=', True)])
            elif record.regime_origin_id:
                record.is_regime_manager = record.regime_origin_id.is_manager
            else:
                record.is_regime_manager = False

    @api.depends('contract_id')
    def _compute_program_project_origin_id(self):
        Office = self.env['onsc.legajo.office'].sudo()
        for rec in self:
            if rec.contract_id:
                rec.program_project_origin_id = Office.search([
                    ('inciso', '=', rec.contract_id.inciso_id.id),
                    ('unidadEjecutora', '=', rec.contract_id.operating_unit_id.id),
                    ('programa', '=', rec.contract_id.program), ('proyecto', '=', rec.contract_id.project)], limit=1).id
            else:
                rec.program_project_origin_id = False
            rec.is_responsable_uo = False

    # COMPUTES COMPORTAMIENTOS
    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_origin(self):
        for record in self:
            record.is_edit_origin = record.state == 'draft'

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_destination(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            administrator_security = self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
            inciso_security = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs')
            operating_unit_security = self.env.user.has_group('onsc_legajo.group_legajo_hr_ue_alta_cs')
            is_same_inciso = record.inciso_destination_id == record.inciso_origin_id
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
            elif is_same_inciso and operating_unit_security:
                record.is_edit_destination = False
            # El Usuario logueado tiene permiso por ue y la ue de destino es el mismo que el del usuario
            elif record.type_cs == 'ac2ac' and is_same_inciso:
                record.is_edit_destination = True
            # Siempre poder editar si no es ac2ac
            elif record.type_cs != 'ac2ac':
                record.is_edit_destination = True
            else:
                record.is_edit_destination = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state', 'operating_unit_destination_id',
                 'operating_unit_origin_id')
    def _compute_is_available_send_to_sgh(self):
        is_administrar_altas_cs = self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
        is_user_inciso = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs')
        is_user_ue = self.env.user.has_group('onsc_legajo.group_legajo_hr_ue_alta_cs')
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            # DESTINATION CONDITIONS
            is_editable_dest_inciso = record.inciso_destination_id == inciso_id and is_user_inciso
            is_editable_dest_ue = record.operating_unit_destination_id == operating_unit_id and is_user_ue
            is_editable_dest = is_editable_dest_inciso or is_editable_dest_ue
            # ORIGIN CONDITIONS
            is_editable_orig_inciso = record.inciso_origin_id == inciso_id and is_user_inciso
            is_editable_orig_ue = record.operating_unit_origin_id == operating_unit_id and is_user_ue
            is_editable_orig = is_editable_orig_inciso or is_editable_orig_ue

            is_same_inciso = record.inciso_origin_id == record.inciso_destination_id
            is_user_any_inciso = is_editable_orig_inciso or is_editable_dest_inciso

            if record.state in ['draft', 'to_process', 'returned', 'error_sgh'] and is_administrar_altas_cs:
                record.is_available_send_to_sgh = True
            elif record.type_cs == 'ac2ac' and is_editable_dest and record.state in ['to_process', 'error_sgh']:
                record.is_available_send_to_sgh = True
            elif record.type_cs == 'out2ac' and is_editable_dest and record.state in ['draft', 'error_sgh']:
                record.is_available_send_to_sgh = True
            elif record.type_cs == 'ac2out' and is_editable_orig and record.state in ['draft', 'error_sgh']:
                record.is_available_send_to_sgh = True
            elif is_same_inciso and is_user_any_inciso and record.state not in ['cancelled', 'confirmed']:
                record.is_available_send_to_sgh = True
            else:
                record.is_available_send_to_sgh = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state', 'operating_unit_destination_id',
                 'operating_unit_origin_id')
    def _compute_is_available_send_origin(self):
        is_administrar_altas_cs = self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
        is_user_inciso = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs')
        is_user_ue = self.env.user.has_group('onsc_legajo.group_legajo_hr_ue_alta_cs')
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            is_ac2ac = record.type_cs == 'ac2ac'
            is_editable_dest_inciso = record.inciso_destination_id == inciso_id and is_user_inciso
            is_editable_dest_ue = record.operating_unit_destination_id == operating_unit_id and is_user_ue

            is_same_inciso = record.inciso_origin_id == record.inciso_destination_id
            same_inciso_cond = (is_editable_dest_inciso and not is_same_inciso) or is_editable_dest_ue

            if record.state in ['to_process',
                                'error_sgh'] and record.is_edit_destination and is_ac2ac and same_inciso_cond:
                record.is_available_send_origin = True
            elif record.state in ['to_process', 'error_sgh'] and is_ac2ac and is_administrar_altas_cs:
                record.is_available_send_origin = True
            else:
                record.is_available_send_origin = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state',
                 'operating_unit_destination_id', 'operating_unit_origin_id')
    def _compute_is_available_send_destination(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        is_user_administrar_altas_cs = self.env.user.has_group('onsc_legajo.group_legajo_alta_cs_administrar_altas_cs')
        is_user_inciso_alta_cs = self.env.user.has_group('onsc_legajo.group_legajo_hr_inciso_alta_cs')
        is_user_ue_alta_cs = self.env.user.has_group('onsc_legajo.group_legajo_hr_ue_alta_cs')
        for record in self:
            is_destination_ac = record.inciso_destination_id.is_central_administration
            base_cond = record.state in ['draft', 'returned'] and is_destination_ac
            is_iam_inciso_orig = record.inciso_origin_id == inciso_id
            isnt_iam_inciso_dest = record.inciso_destination_id != inciso_id
            is_iam_ue_orig = record.operating_unit_origin_id == operating_unit_id
            if is_user_administrar_altas_cs:
                is_available_send_destination = False
            elif is_user_inciso_alta_cs and is_iam_inciso_orig and isnt_iam_inciso_dest and base_cond:
                is_available_send_destination = True
            elif is_user_ue_alta_cs and is_iam_ue_orig and base_cond:
                is_available_send_destination = True
            else:
                is_available_send_destination = False

            record.is_available_send_destination = is_available_send_destination

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_cs', 'state')
    def _compute_is_available_cancel(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            if record.state in ['confirmed', 'cancelled']:
                record.is_available_cancel = False
            elif record.state not in ['draft', 'cancelled'] and self.env.user.has_group(
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

    @api.depends('regime_origin_id')
    def _compute_security_job_id_domain(self):
        user_level = self.env.user.employee_id.job_id.sequence
        for rec in self:
            domain = [('sequence', '>=', user_level)]
            rec.security_job_id_domain = json.dumps(domain)

    @api.constrains("date_start_commission", "date_end_commission")
    def _check_dates(self):
        for record in self:
            if record.date_start_commission and record.date_start_commission > fields.Date.today():
                raise ValidationError(_("La fecha debe ser menor o igual al día de alta"))
            if record.date_end_commission and record.date_start_commission and record.date_end_commission < record.date_start_commission:
                raise ValidationError(_("La fecha hasta debe ser mayor o igual que la fecha desde"))

    @api.constrains("reason_description", "resolution_description")
    def _check_len_description(self):
        for record in self:
            if record.reason_description and len(record.reason_description) > 50:
                raise ValidationError(_("El campo Descripción del Motivo no puede tener más de 50 caracteres."))
            if record.resolution_description and len(record.resolution_description) > 100:
                raise ValidationError(_("El campo Descripción de la resolución no puede tener más de 100 caracteres."))
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
        self.is_responsable_uo = False

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
        self.date_start_commission = False
        self.date_end_commission = False
        self.department_id = False
        self.security_job_id = False
        self.legajo_state_id = False
        self.occupation_id = False
        self.regime_commission_id = False
        self.reason_description = False
        self.code_regime_start_commission_id = False
        self.additional_information = False

    @api.onchange('inciso_destination_id')
    def onchange_inciso_destination_id(self):
        self.norm_id = False
        self.operating_unit_destination_id = False

    @api.onchange('operating_unit_destination_id')
    def onchange_operating_unit_destination_id(self):
        self.department_id = False

    @api.onchange('operating_unit_origin_id', 'operating_unit_destination_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_destination_id and rec.operating_unit_origin_id and \
                    rec.operating_unit_origin_id == rec.operating_unit_destination_id:
                raise ValidationError(_('La unidad ejecutora de origen y destino no pueden ser iguales'))

    @api.onchange('regime_origin_id')
    def onchange_regime_origin_id(self):
        if self.regime_origin_id.is_manager is False:
            self.is_responsable_uo = False
        self.security_job_id = False

    # flake8: noqa: C901
    def check_send_sgh(self):
        for record in self:
            message = []
            for required_field in REQUIRED_FIELDS:
                if not eval('record.%s' % required_field):
                    message.append(record._fields[required_field].string)
            if record.inciso_destination_id.is_central_administration and not record.legajo_state_id:
                message.append(record._fields['legajo_state_id'].string)
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
            if not record.cv_sex:
                message.append(_("Sexo"))
            if record.regime_commission_id and not record.regime_commission_id.cgn_code:
                message.append(
                    _("Falta el Código de CGN en la configuración del Régimen de comisión seleccionado. Contactar al administrador del sistema."))
            if record.is_inciso_origin_ac and record.contract_id and not record.contract_id.legajo_state == 'active':
                message.append(_("El contrato debe estar activo"))
            if record.is_responsable_uo and not self.env['hr.job'].is_job_available_for_manager(
                    record.department_id, record.date_start_commission):
                message.append("No se puede asignar la seguridad de puesto elegida, "
                               "porque ya existe un responsable en la UO seleccionada.")
        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))
        return True

    def unlink(self):
        if self.filtered(lambda x: x.state != 'draft'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super().unlink()

    def action_send_destination(self):
        self.state = 'to_process'
        if not self.inciso_destination_id:
            raise ValidationError(_("Debe seleccionar inciso de destino"))
        if not self.operating_unit_destination_id:
            raise ValidationError(_("Debe seleccionar una unidad ejecutora de destino"))
        if self.is_inciso_origin_ac and self.contract_id and not self.contract_id.legajo_state == 'active':
            raise ValidationError(_("El contrato debe estar activo"))

    def action_send_origin(self):
        self.state = 'returned'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_send_sgh(self):
        self.check_send_sgh()
        self._message_log(body=_('Envia a SGH'))
        self.env['onsc.legajo.abstract.alta.cs.ws10'].with_context(
            log_info=True, altas_cs=self).suspend_security().syncronize(self)

    def action_aprobado_cgn(self):
        """
        aprobado cgn, construye toda la estructura legajo asociada al alta
        """
        if self.type_cs == 'out2ac':
            employee = self._get_legajo_employee()
            self.env['onsc.legajo']._get_legajo(employee)
        else:
            employee = self.employee_id
        new_contract = self._get_legajo_contract(employee)
        # self.contract_id.suspend_security().write({'cs_contract_id': new_contract.id})
        date_start = fields.Date.from_string(self.date_start_commission or fields.Date.today())
        self.contract_id.with_context(no_check_write=True).deactivate_legajo_contract(
            date_end=date_start - relativedelta(days=1),
            legajo_state='outgoing_commission',
            eff_date=fields.Date.today(),
            inciso_dest_id=self.inciso_destination_id.id,
            operating_unit_dest_id=self.operating_unit_destination_id.id,
        )
        if self.type_cs != 'ac2out':
            self._get_legajo_job(new_contract)
        self.write({
            'state': 'confirmed',
            'is_error_synchronization': False,
            'error_message_synchronization': ''
        })

    def get_inciso_operating_unit_by_user(self):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return inciso_id, operating_unit_id

    def _get_legajo_employee(self):
        cv_emissor_country_id = self.env.ref('base.uy')
        cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([
            ('code', '=', 'ci')], limit=1)
        return self.env['hr.employee']._get_legajo_employee(cv_emissor_country_id, cv_document_type_id, self.partner_id)

    def _get_legajo_contract(self, employee_id=False):
        Contract = self.env['hr.contract']
        origin_contract_id = self.contract_id
        employee = employee_id or self.employee_id
        vals = {
            'employee_id': employee.id,
            'name': employee.name,
            'date_start': self.date_start_commission or fields.Date.today(),
            'date_end_commission': self.date_end_commission,
            'inciso_id': self.inciso_destination_id.id,
            'operating_unit_id': self.operating_unit_destination_id.id,
            'income_mechanism_id': origin_contract_id.income_mechanism_id.id,
            'program': self.program_project_destination_id.programa,
            'project': self.program_project_destination_id.proyecto,
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
            'inciso_origin_id': self.inciso_origin_id.id,
            'operating_unit_origin_id': self.operating_unit_origin_id.id,
            'eff_date': fields.Date.today(),
            'legajo_state_id': self.legajo_state_id.id,
            'descriptor1_origin_id': origin_contract_id.descriptor1_id.id,
            'descriptor2_origin_id': origin_contract_id.descriptor2_id.id,
            'descriptor3_origin_id': origin_contract_id.descriptor3_id.id,
            'descriptor4_origin_id': origin_contract_id.descriptor4_id.id,
        }

        if self.type_cs == 'out2ac':
            _regime_id = self.env['onsc.legajo.regime'].sudo().search([('is_fac2ac', '=', True)], limit=1).id
        else:
            _regime_id = origin_contract_id.regime_id.id
        vals.update({'regime_id': _regime_id})
        contract = Contract.suspend_security().create(vals)

        for document_record in self.attached_document_ids:
            document_record.write({
                'contract_id': contract.id,
                'type': 'discharge'})

        contract.activate_legajo_contract(legajo_state='incoming_commission')
        return contract

    def _get_legajo_job(self, contract):
        return self.env['hr.job'].create_job(
            contract,
            self.department_id,
            self.date_start_commission,
            self.security_job_id,
            is_uo_manager=self.is_responsable_uo
        )
