# -*- coding: utf-8 -*-

import json

from odoo import api, fields, models, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning
from odoo.exceptions import ValidationError


class Department(models.Model):
    _name = "hr.department"
    _inherit = ['hr.department', 'model.history']
    _history_model = 'hr.department.history'

    code = fields.Char('Identificador',
                       default=lambda self: self.env['ir.sequence'].next_by_code('onsc.catalog.inciso.identifier'),
                       copy=False)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', tracking=True, history=True)
    company_id = fields.Many2one('res.company',
                                 related='inciso_id.company_id',
                                 store=True, history=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", tracking=True, history=True)
    parent_id = fields.Many2one('hr.department', string='Parent Department', index=True,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                tracking=True,
                                history=True)
    parent_id_domain = fields.Char(compute='_compute_parent_id_domain')
    name = fields.Char('Department Name', required=True, tracking=True, history=True)
    short_name = fields.Char(string="Nombre corto", tracking=True, history=True)
    function_nature = fields.Selection(string=u"Naturaleza de la función",
                                       selection=[
                                           ('adviser', 'Asesora'),
                                           ('operative', 'Ejecutora'),
                                           ('comite', 'Comité'),
                                           ('commission_project', 'Comisión/Proyecto'),
                                           ('program', 'Programa'),
                                       ], tracking=True, history=True)
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel jerárquico", tracking=True,
                                            history=True)
    hierarchical_level_order = fields.Integer(string="Orden", related='hierarchical_level_id.order', store=True)
    hierarchical_level_id_domain = fields.Char(compute='_compute_hierarchical_level_id_domain')
    function_nature_form = fields.Selection(selection=[
        ('form1', 'Formulario 1'),
        ('form2', 'Formulario 2'),
    ], compute='_compute_function_nature_form', store=True)
    mission = fields.Char(string="Misión", history=True, tracking=True)
    reponsability_ids = fields.One2many("hr.department.responsability",
                                        inverse_name="department_id",
                                        string="Lista de responsabilidades", history=True)
    key_functional_habilities = fields.Char(string="Competencias funcionales claves", tracking=True, history=True)
    process_contributor = fields.Char(string="Procesos a los que contribuye", tracking=True, history=True)
    regulatory = fields.Char(string="Marco normativo", tracking=True, history=True)
    start_date = fields.Date(string='Inicio de vigencia', tracking=True, history=True)
    end_date = fields.Date(string='Fin de vigencia', tracking=True, history=True)
    category = fields.Selection(string=u"Categoría", selection=[
        ('planning', 'PLANIFICACION ESTRATEGICA'),
        ('financial_management', 'GESTION FINANCIERA'),
        ('technology', u'TECNOLOGIA y REDISEÑO DE PROCESOS'),
        ('human_management', 'GESTION HUMANA'),
    ], tracking=True, history=True)
    is_approve_onsc = fields.Boolean(string="Aprobado ONSC", copy=False, tracking=True)
    approve_onsc_date = fields.Date(string=u"Fecha aprobación ONSC", copy=False, )
    is_approve_cgn = fields.Boolean(string="Aprobado CGN", copy=False, tracking=True, )
    approve_cgn_date = fields.Date(string=u"Fecha aprobación CGN", copy=False)

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime('Fecha de última modificación', index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    @api.depends('function_nature')
    def _compute_function_nature_form(self):
        for record in self:
            if record.function_nature in ['operative', 'adviser']:
                record.function_nature_form = 'form1'
            else:
                record.function_nature_form = 'form2'

    @api.depends('inciso_id', 'function_nature')
    def _compute_hierarchical_level_id_domain(self):
        HierarchicalLevel = self.env['onsc.catalog.hierarchical.level']
        for record in self:
            domain = [('is_central_administration', '=', record.inciso_id.is_central_administration)]
            if record.function_nature == 'adviser':
                domain.append(('order', 'in', [1, 2]))
            elif record.function_nature in ['program', 'commission_project', 'comite']:
                domain.append(('order', 'in', [1]))
            record.hierarchical_level_id_domain = json.dumps([('id', 'in', HierarchicalLevel.search(domain).ids)])

    @api.depends('function_nature', 'hierarchical_level_id', 'operating_unit_id', 'hierarchical_level_order')
    def _compute_parent_id_domain(self):
        UO = self.env['hr.department']
        for record in self:
            domain = [('id', 'not in', self.ids), ('operating_unit_id', '=', record.operating_unit_id.id)]
            if record.function_nature == 'operative':
                domain.extend([
                    ('hierarchical_level_order', '<', record.hierarchical_level_order),
                    ('hierarchical_level_order', '>', 0)])
            elif record.function_nature == 'adviser':
                domain.extend([
                    ('hierarchical_level_order', '=', 1),
                    ('hierarchical_level_id.is_central_administration', '=', True), ])
            else:
                domain.extend([
                    ('hierarchical_level_order', '=', 1),
                    ('function_nature', '=', 'operative'),
                    ('hierarchical_level_id.is_central_administration', '=', True), ])
            uo_ids = UO.search(domain).ids
            record.parent_id_domain = json.dumps([('id', 'in', uo_ids)])

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return catalog_warning(_(u"La fecha de inicio de vigencia no puede ser mayor "
                                     u"que la fecha de fin de vigencia"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return catalog_warning(_(u"La fecha de fin de vigencia no puede ser menor "
                                     u"que la fecha de inicio de vigencia"))

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        self.operating_unit_id = False
        if self.inciso_id.id is False or self.inciso_id.is_central_administration != self.hierarchical_level_id.is_central_administration:
            self.hierarchical_level_id = False

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        if self.operating_unit_id.id is False or self.parent_id.operating_unit_id != self.operating_unit_id:
            self.parent_id = False

    @api.onchange('function_nature')
    def onchange_function_nature(self):
        self.hierarchical_level_id = False

    @api.onchange('is_approve_onsc')
    def onchange_is_approve_onsc(self):
        if self.is_approve_onsc:
            self.approve_onsc_date = fields.Date.today()
        else:
            self.approve_onsc_date = False

    @api.onchange('is_approve_cgn')
    def onchange_is_approve_cgn(self):
        if self.is_approve_cgn:
            self.approve_cgn_date = fields.Date.today()
        else:
            self.approve_cgn_date = False

    @api.onchange('function_nature_form')
    def onchange_function_nature_form(self):
        if self.function_nature_form == 'form2':
            self.short_name = False
            self.category = False
            self.mission = False
            self.process_contributor = False
            self.reponsability_ids = [(5,)]

    def write(self, vals):
        self._check_user_can_write()
        return super(Department, self).write(vals)

    def toggle_active(self):
        self._check_toggle_active()
        return super(Department, self.with_context(no_check_write=True)).toggle_active()

    def _check_user_can_write(self):
        if self.env.context.get('no_check_write', False) is False and self.user_has_groups(
                "onsc_catalog.group_catalog_aprobador_cgn") and self.user_has_groups(
            "onsc_catalog.group_catalog_configurador_servicio_civil") is False:
            raise ValidationError(_("No puede editar información de la Unidad organizativa. "
                                    "La única operación permitida es Aprobar CGN"))
        if self.env.context.get('no_check_write', False) is False and self.user_has_groups(
                "onsc_catalog.group_catalog_configurador_servicio_civil"):
            for record in self:
                condition1 = (record.is_approve_cgn is True and record.is_approve_onsc is False)
                condition2 = (record.is_approve_cgn is False and record.is_approve_onsc is True)
                if condition1 or condition2:
                    raise ValidationError(_("Solo puede editar si la aprobación CGN y ONSC "
                                            "están ambas marcadas o desmarcadas"))

    def _check_toggle_active(self):
        if False in self.mapped('is_approve_cgn'):
            raise ValidationError(_("No puede archivar o desarchivar una Unidad organizativa si no está Aprobada CGN!"))
        for record in self.filtered(lambda x: x.active is True):
            if self.search_count([('id', '!=', record.id), ('id', 'child_of', record.id), ('active', '=', True)]):
                raise ValidationError(_(u"No puede desactivar una Unidad organizativa si tiene dependencias activas!"))
        return True

    def action_aprobar_cgn(self):
        return self.suspend_security().with_context(no_check_write=True).write({
            'is_approve_cgn': True,
            'approve_cgn_date': fields.Date.today(),
            'active': True
        })

    def action_aprobar_onsc(self):
        return self.with_context(no_check_write=True).write({
            'is_approve_onsc': True,
            'approve_onsc_date': fields.Date.today()
        })


class DepartmentResponsability(models.Model):
    _name = "hr.department.responsability"
    _description = u"Lista de responsabilidades"

    department_id = fields.Many2one("hr.department", string="deparment_id")
    process = fields.Char(string="Proceso", required=True)
    product = fields.Char(string="Producto", required=True)
    target = fields.Char(string="Destinatarios", required=True)


class DepartmentHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.department.history'
    _parent_model = 'hr.department'
