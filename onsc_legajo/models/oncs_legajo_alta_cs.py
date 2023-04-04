# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoAltaCS(models.Model):
    _name = 'onsc.legajo.alta.cs'
    _inherit = ['onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin',
                'onsc.legajo.abstract.legajo.security']
    _description = 'Alta de Comisión Saliente'
    _rec_name = 'full_name'

    employee_id = fields.Many2one('hr.employee', 'Empleados')
    partner_id = fields.Many2one('res.partner', string='CI', required=True, )
    partner_id_domain = fields.Char(compute='_compute_partner_id_domain')
    full_name = fields.Char('Nombre', related='partner_id.cv_full_name', store=True)

    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso Origen', required=True,
                                       default=lambda self: self._get_default_inciso_id(), copy=False)
    inciso_origin_id_domain = fields.Char(compute='_compute_inciso_id_domain')
    is_inciso_origin_ac = fields.Boolean("El inciso de origen es AC?",
                                         related='inciso_origin_id.is_central_administration')
    operating_unit_origin_id = fields.Many2one("operating.unit", string="Unidad ejecutora Origen", required=True,
                                               default=lambda self: self._get_default_ue_id(), copy=False)
    operating_unit_origin_id_domain = fields.Char(compute='_compute_operating_unit_origin_id_domain')
    line_ids = fields.One2many('onsc.legajo.alta.cs.contract.line', 'alta_cs_id', string='Líneas de Alta de Comisión')
    sequence_position_origin = fields.Char(string='Secuencia Plaza Origen')
    contract_id = fields.Many2one('hr.contract', 'Contrato', compute='_compute_contract_id', store=True)
    program_origin = fields.Char(string='Programa Origen')
    project_origin = fields.Char(string='Proyecto Origen')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen Origen')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1', related='contract_id.descriptor1_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2', related='contract_id.descriptor2_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3', related='contract_id.descriptor3_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4', related='contract_id.descriptor4_id')
    type_commission_selection = fields.Selection(
        [('cs', 'Comisión de Servicio'), ('pc', 'Pase en Comisión')],
        string='Tipo de comisión', compute='_compute_type_commission_selection')
    inciso_destination_id = fields.Many2one('onsc.catalog.inciso', string='Inciso Destino', required=True)
    inciso_destination_id_domain = fields.Char(compute='_compute_inciso_destination_id_domain')
    operating_unit_destination_id = fields.Many2one("operating.unit", string="Unidad ejecutora Destino", required=True)
    operating_unit_destination_id_domain = fields.Char(compute='_compute_operating_unit_destination_id_domain')

    office_id = fields.Many2one("onsc.legajo.office", string="Oficina")
    office_id_domain = fields.Char(compute='_compute_office_id_domain')
    program_destination = fields.Char(string='Programa Destino', related='office_id.programaDescripcion')
    project_destination = fields.Char(string='Proyecto Destino', related='office_id.proyectoDescripcion')
    regime_destination = fields.Char(string='Régimen Destino', default='3001')
    date_start_commission = fields.Date(string='Fecha desde de la Comisión', required=True)
    department_id = fields.Many2one('hr.department', string='UO')
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión')
    description_reason = fields.Text(string='Descripción del motivo')
    norm_code_id = fields.Many2one('onsc.legajo.norm', string='Código de norma')
    norm_number = fields.Integer(string='Número de norma',
                                 related='norm_code_id.numeroNorma')
    norm_year = fields.Integer(string='Año de norma alta', related='norm_code_id.anioNorma')
    norm_article = fields.Integer(string='Artículo de norma',
                                  related='norm_code_id.articuloNorma')
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
        [('ac2ac', 'AC a AC'), ('ac2out', 'AC a fuera de AC'), ('out2ac', 'Fuera de AC a AC  ')],
        string='Tipo de movimiento', compute='_compute_type_move_selection')

    @api.constrains("line_ids")
    def _check_line_ids(self):
        # Chequear que solo una linea este con el campo is_selected = True
        if len(self.line_ids.filtered(lambda x: x.is_selected)) > 1:
            raise ValidationError("Solo puede seleccionar una línea en el origen")

    @api.constrains("attached_documen_ids")
    def _check_attached_documen_ids(self):
        for record in self:
            if not record.attached_documen_ids:
                raise ValidationError("Debe haber al menos un documento adjunto")

    @api.constrains("date_start_commission")
    def _check_date(self):
        for record in self:
            if record.date_start_commission > fields.Date.today():
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

    @api.depends('operating_unit_origin_id', 'operating_unit_destination_id')
    def _compute_type_commission_selection(self):
        for record in self:
            if record.operating_unit_origin_id and record.operating_unit_destination_id:
                if record.operating_unit_origin_id.inciso_id == record.operating_unit_destination_id.inciso_id:
                    record.type_commission_selection = 'cs'
                else:
                    record.type_commission_selection = 'pc'

    @api.depends('operating_unit_destination_id', 'inciso_destination_id')
    def _compute_office_id_domain(self):
        for record in self:
            if record.operating_unit_destination_id and record.inciso_destination_id:
                record.office_id_domain = json.dumps(
                    [('inciso', '=', record.inciso_destination_id.name),
                     ('unidadEjecutora', '=', record.operating_unit_destination_id.name)])
            else:
                record.office_id_domain = json.dumps([])

    @api.depends('operating_unit_origin_id')
    def _compute_partner_id_domain(self):
        for record in self:
            if record.is_inciso_origin_ac:
                employee_ids = self.env['hr.contract'].search(
                    [('operating_unit_id', '=', record.operating_unit_origin_id.id),
                     ('legajo_state', '=', 'active'),
                     ('regime_id.presupuesto', '=', True)]).mapped(
                    'employee_id').ids
                record.partner_id_domain = json.dumps([('legajo_employee_ids', 'in', employee_ids)])
            else:
                record.partner_id_domain = json.dumps(
                    [('cv_document_type_id.code', '=', 'ci'), ('is_partner_cv', '=', True)])

    def _compute_inciso_id_domain(self):
        for rec in self:
            contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
            inciso_id = contract.inciso_id.id if contract else False
            domain = ['|', ('id', '=', inciso_id), ('is_central_administration', '=', False)]
            rec.inciso_id_domain = json.dumps(domain)

    @api.depends('inciso_origin_id')
    def _compute_inciso_destination_id_domain(self):
        # Inciso Destino: cualquier inciso salvo que el inciso origen esté fuera de AC que en ese caso debe ser el del usuario.
        for rec in self:
            contract = self.env.user.employee_id.job_id.contract_id if self.env.user.employee_id and self.env.user.employee_id.job_id else False
            inciso_id = contract.inciso_id.id if contract else False
            if rec.inciso_origin_id and not rec.inciso_origin_id.is_central_administration:
                domain = [('id', '=', inciso_id)]
            else:
                domain = [('is_central_administration', '=', False)]
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
                record.type_move_selection = False

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

    @api.depends('line_ids')
    def _compute_contract_id(self):
        # obtener el contrato de la linea con el campo is_selected = True
        for rec in self:
            selected = rec.line_ids.filtered(lambda x: x.is_selected)
            if selected:
                rec.contract_id = selected.contract_id
            else:
                rec.contract_id = False

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador_legajo',
            'group_legajo_consulta_altas_cs')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_inciso_alta_cs')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_ue_alta_cs')

    def get_domain(self, args):
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
        args = self.get_domain(args)
        return super(ONSCLegajoAltaCS, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        domain = self.get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.onchange('partner_id')
    def onchange_employee_id(self):
        if self.partner_id:
            self.employee_id = self.partner_id.legajo_employee_ids[0].id
            data = [(5, 0, 0)]
            available_contracts = self._get_available_contracts(self.employee_id, self.operating_unit_origin_id.id,
                                                                'operating_unit_id')
            if available_contracts:
                for contract in available_contracts:
                    data.append((0, 0, {'contract_id': contract.id, }))
                self.line_ids = data
            else:
                self.line_ids = data
        else:
            self.line_ids = [(5, 0, 0)]

    @api.onchange('regime_id')
    def onchange_regimen(self):
        for rec in self:
            rec.descriptor1_id = False
            rec.descriptor2_id = False
            rec.descriptor3_id = False
            rec.descriptor4_id = False

    @api.onchange('inciso_origin_id')
    def onchange_inciso_origin_id(self):
        if self.inciso_origin_id:
            self.operating_unit_origin_id = False
            self.program_origin = False
            self.project_origin = False
            self.partner_id = False

    # validar q las operating unit de origen y destino no sean iguales
    @api.onchange('operating_unit_origin_id', 'operating_unit_destination_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_origin_id == rec.operating_unit_destination_id:
                raise ValidationError('La unidad ejecutora de origen y destino no pueden ser iguales')


class OnscLegajoAltaCsCcontractLine(models.Model):
    _name = 'onsc.legajo.alta.cs.contract.line'
    _description = 'Alta Comisión línea de contrato'

    alta_cs_id = fields.Many2one('onsc.legajo.alta.cs', string='Alta CS', ondelete='cascade', index=True)
    contract_id = fields.Many2one('hr.contract', string='Contracto')
    position = fields.Char(string='Puesto', related='contract_id.position')
    workplace = fields.Char(string='Plaza', related='contract_id.workplace')
    workplace_state = fields.Char(string='Estado de la plaza', related='contract_id.workplace_state')
    is_selected = fields.Boolean(string='Seleccionado')
