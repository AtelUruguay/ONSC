# -*- coding: utf-8 -*-
import json
from lxml import etree
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv import expression

class ONSCLegajoAltaCS(models.Model):
    _name = 'onsc.legajo.alta.cs'
    _inherit = ['onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin']
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

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        hide = ['document_identity_file', 'document_identity_filename', 'civical_credential_file',
                'civical_credential_filename', 'is_cv_race_public', 'cv_gender_record_filename',
                'cjppu_affiliate_number', 'professional_resume', 'user_linkedIn', 'is_driver_license', 'cv_gender2',
                'cv_gender_id', 'is_afro_descendants', 'is_occupational_health_card', 'occupational_health_card_date',
                'is_medical_aptitude_certificate_status', 'medical_aptitude_certificate_date', 'is_victim_violent',
                'is_public_information_victim_violent', 'allow_content_public', 'situation_disability',
                'people_disabilitie', 'certificate_date', 'to_date', 'see', 'hear', 'walk', 'speak', 'realize', 'lear',
                'interaction', 'need_other_support', 'afro_descendants_file', 'occupational_health_card_file',
                'occupational_health_card_filename', 'relationship_victim_violent_filename', 'is_cv_gender_public',
                'medical_aptitude_certificate_file', 'relationship_victim_violent_file', 'document_certificate_file',
                'document_certificate_filename', 'afro_descendants_filename']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    def _get_domain(self, args):
        args = expression.AND([[
            ('partner_id', '!=', self.env.user.partner_id.id)
        ], args])
        if self.user_has_groups('onsc_legajo.group_legajo_hr_inciso_alta_cs'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    '|', ('inciso_origin_id', '=', inciso_id.id),
                    ('inciso_destination_id', '=', inciso_id.id)
                ], args])
        if self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[
                    '|', ('inciso_origin_id', '=', inciso_id.id),
                    ('inciso_destination_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    '|', ('operating_unit_origin_id', '=', operating_unit_id.id),
                    ('operating_unit_destination_id', '=', operating_unit_id.id)
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

    employee_id = fields.Many2one('hr.employee', 'Empleados', compute="_compute_employee", store=True)
    partner_id = fields.Many2one('res.partner', string='CI', required=True)
    partner_id_domain = fields.Char(compute='_compute_partner_id_domain')

    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso Origen', required=True,
                                       default=lambda self: self._get_default_inciso_id(), copy=False)
    inciso_origin_id_domain = fields.Char(compute='_compute_inciso_origin_id_domain')
    is_inciso_origin_ac = fields.Boolean("El inciso de origen es AC?",
                                         related='inciso_origin_id.is_central_administration')
    operating_unit_origin_id = fields.Many2one("operating.unit", string="Unidad ejecutora Origen", required=True,
                                               default=lambda self: self._get_default_ue_id(), copy=False)
    operating_unit_origin_id_domain = fields.Char(compute='_compute_operating_unit_origin_id_domain')
    sequence_position_origin = fields.Char(string='Secuencia Plaza Origen')
    contract_id = fields.Many2one('hr.contract', 'Contrato', copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    program_project_origin_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto Origen',
                                                compute='_compute_program_project_origin_id', store=True)
    program_origin = fields.Char(string='Programa Origen', related='program_project_origin_id.programaDescripcion')
    project_origin = fields.Char(string='Proyecto Origen', related='program_project_origin_id.proyectoDescripcion')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen Origen', related='contract_id.regime_id')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1',
                                     related='contract_id.descriptor1_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2',
                                     related='contract_id.descriptor2_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3',
                                     related='contract_id.descriptor3_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4',
                                     related='contract_id.descriptor4_id')
    type_commission_selection = fields.Selection(
        [('cs', 'Comisión de Servicio'), ('pc', 'Pase en Comisión')],
        string='Tipo de comisión', compute='_compute_type_commission_selection')
    inciso_destination_id = fields.Many2one('onsc.catalog.inciso', string='Inciso Destino')
    inciso_destination_id_domain = fields.Char(compute='_compute_inciso_destination_id_domain')
    operating_unit_destination_id = fields.Many2one("operating.unit", string="Unidad ejecutora Destino")
    operating_unit_destination_id_domain = fields.Char(compute='_compute_operating_unit_destination_id_domain')

    program_project_destination_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto Destino',
                                                     domain="[('inciso', '=', inciso_destination_id),('unidadEjecutora', '=', operating_unit_destination_id)]")
    program_destination = fields.Char(string='Programa Destino',
                                      related='program_project_destination_id.programaDescripcion')
    project_destination = fields.Char(string='Proyecto Destino',
                                      related='program_project_destination_id.proyectoDescripcion')
    regime_destination = fields.Char(string='Régimen Destino', default='3001')
    date_start_commission = fields.Date(string='Fecha desde de la Comisión')
    department_id = fields.Many2one('hr.department', string='UO')
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión')
    description_reason = fields.Text(string='Descripción del motivo')
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma')
    norm_type = fields.Char(string="Tipo norma", related="norm_id.tipoNorma", store=True, readonly=True)
    norm_number = fields.Integer(string='Número de norma', related="norm_id.numeroNorma",
                                 store=True, readonly=True)
    norm_year = fields.Integer(string='Año de norma', related="norm_id.anioNorma", store=True,
                               readonly=True)
    norm_article = fields.Integer(string='Artículo de norma', related="norm_id.articuloNorma",
                                  store=True, readonly=True)
    tag_norm_not_found = fields.Char(string='Etiqueta con el mensaje en caso de no encontrar la norma')
    description_resolution = fields.Text(string='Descripción de la resolución')
    date_resolution = fields.Date(string='Fecha de la resolución')
    resolution_type = fields.Selection(
        [('m', 'Inciso'), ('p', 'Presidencia o Poder ejecutivo'), ('u', 'Unidad ejecutora')],
        string='Tipo de resolución')
    code_regime_start_commission_id = fields.Many2one('onsc.legajo.commission.regime',
                                                      string='Código del régimen de Inicio de Comisión')
    state = fields.Selection(
        [('draft', 'Borrador'), ('to_process', 'A procesar en destino'), ('returned', 'Devuelto a origen'),
         ('cancelled', 'Cancelado'), ('error_sgh', 'Error SGH'), ('confirmed', 'Confirmado')],
        string='Estado', default='draft')
    additional_information = fields.Text(string='Información adicional')
    attached_documen_ids = fields.One2many('onsc.legajo.attached.document',
                                           'alta_cs_id',
                                           string='Documentos adjuntos')
    error_reported_integration_id = fields.Many2one('onsc.legajo.integration.error',
                                                    string='Error reportado integración')

    type_move_selection = fields.Selection(
        [('', 'No determinado'), ('ac2ac', 'AC a AC'), ('ac2out', 'AC a fuera de AC'), ('out2ac', 'Fuera de AC a AC ')],
        string='Tipo de movimiento', compute='_compute_type_move_selection')

    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    # editar datos de destino
    is_edit_destination = fields.Boolean(string="Editar datos de destino", compute='_compute_is_edit_destination')
    is_edit_origin = fields.Boolean(string="Editar datos de origen", compute='_compute_is_edit_origin')
    is_edit_inciso_ou_destination = fields.Boolean(string="Editar inciso/ou destino",
                                                   compute='_compute_is_edit_inciso_ou_destination')

    @api.constrains("date_start_commission")
    def _check_date(self):
        for record in self:
            if record.date_start_commission and record.date_start_commission > fields.Date.today():
                raise ValidationError("La fecha debe ser menor o igual al día de alta")

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

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['draft', 'to_process', 'returned']

    @api.depends('operating_unit_origin_id', 'operating_unit_destination_id')
    def _compute_type_commission_selection(self):
        for record in self:
            if record.operating_unit_origin_id and record.operating_unit_destination_id:
                if record.operating_unit_origin_id.inciso_id == record.operating_unit_destination_id.inciso_id:
                    record.type_commission_selection = 'cs'
                else:
                    record.type_commission_selection = 'pc'

    @api.depends('partner_id')
    def _compute_employee(self):
        for record in self:
            Employee = self.env['hr.employee'].suspend_security()
            cv_emissor_country_id = self.env.ref('base.uy').id
            cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                                  limit=1).id or False
            record.employee_id = Employee.search([
                ('cv_emissor_country_id', '=', cv_emissor_country_id),
                ('cv_document_type_id', '=', cv_document_type_id),
                ('cv_nro_doc', '=', record.partner_id.cv_nro_doc),
            ], limit=1)

    @api.depends('employee_id')
    def _compute_contract_id_domain(self):
        Contract = self.env['hr.contract']
        for rec in self:
            if rec.employee_id:
                args = [("legajo_state", "=", 'active'), ('employee_id', '=', rec.employee_id.id),
                        ('operating_unit_id', '=', rec.operating_unit_origin_id.id)]
                contracts = Contract.search(args)
                if contracts:
                    rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
                else:
                    rec.contract_id_domain = json.dumps([('id', '=', False)])
            else:
                rec.contract_id_domain = json.dumps([('id', '=', False)])

    @api.depends('operating_unit_origin_id')
    def _compute_partner_id_domain(self):
        for record in self:
            if record.is_inciso_origin_ac:
                employee_ids = self.env['hr.contract'].sudo().search(
                    [('operating_unit_id', '=', record.operating_unit_origin_id.id),
                     ('legajo_state', '=', 'active'),
                     ('regime_id.presupuesto', '=', True)]).mapped(
                    'employee_id').ids
                record.partner_id_domain = json.dumps([('legajo_employee_ids', 'in', employee_ids)])
            else:
                record.partner_id_domain = json.dumps(
                    [('is_partner_cv', '=', True), ('is_cv_uruguay', '=', True)])

    @api.depends('inciso_origin_id')
    def _compute_inciso_origin_id_domain(self):
        for rec in self:
            contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
            inciso_id = contract.inciso_id.id if contract else False
            domain = ['|', ('id', '=', inciso_id), ('is_central_administration', '=', False)]
            rec.inciso_origin_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id')
    def _compute_inciso_destination_id_domain(self):
        # Inciso Destino: cualquier inciso salvo que el inciso origen esté fuera de AC que en ese caso debe ser el del usuario.
        # Observacion el inciso origen y el destino no puden ser los dos Fuera AC
        for rec in self:
            contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
            inciso_id = contract.inciso_id.id if contract else False
            if rec.inciso_origin_id and not rec.inciso_origin_id.is_central_administration:
                domain = [('id', '=', inciso_id)]
            else:
                domain = ['|', ('id', '=', inciso_id), ('is_central_administration', '=', False)]
            rec.inciso_destination_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id', 'inciso_destination_id')
    def _compute_type_move_selection(self):
        for record in self:
            if record.inciso_origin_id and record.inciso_destination_id:
                if record.inciso_origin_id.is_central_administration and record.inciso_destination_id.is_central_administration:
                    record.type_move_selection = 'ac2ac'
                elif record.inciso_origin_id.is_central_administration and not record.inciso_destination_id.is_central_administration:
                    record.type_move_selection = 'ac2out'
                elif not record.inciso_origin_id.is_central_administration and record.inciso_destination_id.is_central_administration:
                    record.type_move_selection = 'out2ac'
                else:
                    record.type_move_selection = ''
            else:
                record.type_move_selection = ''

    @api.depends('inciso_origin_id')
    def _compute_operating_unit_origin_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_origin_id:
                contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
                inciso_id = contract.inciso_id.id if contract else False
                domain = ['|', ('inciso_id', '=', rec.inciso_origin_id.id), ('id', '=', inciso_id)]
            self.operating_unit_origin_id_domain = json.dumps(domain)

    @api.depends('inciso_destination_id')
    def _compute_operating_unit_destination_id_domain(self):
        # UE Destino: si el inciso destino es el del usuario se filtra por la seguridad del usuario. Si la UE de destino es igual a la de origen “Error: no se puede realizar una comisión dentro de la misma UE.”
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_destination_id:
                contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
                inciso_id = contract.inciso_id.id if contract else False
                domain = ['|', ('inciso_id', '=', rec.inciso_destination_id.id), ('id', '=', inciso_id)]
            self.operating_unit_destination_id_domain = json.dumps(domain)

    @api.depends('contract_id')
    def _compute_program_project_origin_id(self):
        for rec in self:
            if rec.contract_id:
                rec.program_project_origin_id = self.env['onsc.legajo.office'].search(
                    [('inciso', '=', rec.contract_id.inciso_id.id),
                     ('unidadEjecutora', '=', rec.contract_id.operating_unit_id.id),
                     ('programa', '=', rec.contract_id.program), ('proyecto', '=', rec.contract_id.project)]).id
            else:
                rec.program_project_origin_id = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_move_selection', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_origin(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            if record.state == 'draft':
                record.is_edit_origin = True
            else:
                record.is_edit_origin = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_move_selection', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_destination(self):
        for record in self:
            inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
            if record.type_move_selection == 'ac2ac' and record.inciso_destination_id == inciso_id and record.operating_unit_destination_id == operating_unit_id:
                record.is_edit_destination = True
            elif record.type_move_selection != 'ac2ac':
                record.is_edit_destination = True
            else:
                record.is_edit_destination = False

    @api.depends('inciso_origin_id', 'inciso_destination_id', 'type_move_selection', 'operating_unit_origin_id',
                 'operating_unit_destination_id')
    def _compute_is_edit_inciso_ou_destination(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            if record.inciso_destination_id == inciso_id and record.operating_unit_destination_id == operating_unit_id and record.state not in [
                'draft', 'returned']:
                record.is_edit_inciso_ou_destination = False
            elif record.inciso_origin_id == inciso_id and record.state not in [
                'draft', 'returned']:
                record.is_edit_inciso_ou_destination = False
            else:
                record.is_edit_inciso_ou_destination = True

    def get_inciso_operating_unit_by_user(self):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return inciso_id, operating_unit_id

    @api.onchange('inciso_origin_id')
    def onchange_inciso_origin_id(self):
        if self.inciso_origin_id:
            self.operating_unit_origin_id = False
            self.partner_id = False
            self.inciso_destination_id = False
            self.operating_unit_destination_id = False
            self.contract_id = False

    @api.onchange('operating_unit_origin_id')
    def onchange_operating_unit_origin_id(self):
        if self.operating_unit_origin_id:
            self.partner_id = False
            self.inciso_destination_id = False
            self.operating_unit_destination_id = False
            self.contract_id = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.contract_id = False

    @api.onchange('inciso_destination_id')
    def onchange_inciso_destination_id(self):
        if self.inciso_destination_id:
            self.operating_unit_destination_id = False

    @api.onchange('operating_unit_origin_id', 'operating_unit_destination_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_destination_id and rec.operating_unit_origin_id and rec.operating_unit_origin_id == rec.operating_unit_destination_id:
                raise ValidationError('La unidad ejecutora de origen y destino no pueden ser iguales')

    def action_send_destination(self):
        self.state = 'to_process'

    def action_send_origin(self):
        self.state = 'returned'

    def action_cancel(self):
        self.state = 'cancelled'
