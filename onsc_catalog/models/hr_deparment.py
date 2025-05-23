# -*- coding: utf-8 -*-

import json

from odoo import api, fields, models, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning
from odoo.exceptions import ValidationError


class Department(models.Model):
    _name = "hr.department"
    _inherit = ['hr.department', 'model.history', 'onsc.catalog.abstract.approval']
    _history_model = 'hr.department.history'

    code = fields.Char('Identificador',
                       default=lambda self: self.env['ir.sequence'].next_by_code('onsc.catalog.uo.identifier'),
                       copy=False)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso',
                                ondelete='restrict',
                                tracking=True, history=True)
    company_id = fields.Many2one('res.company',
                                 related='inciso_id.company_id',
                                 store=True, history=True, ondelete='restrict')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        ondelete='restrict',
                                        tracking=True, history=True)
    parent_id = fields.Many2one('hr.department', string='Parent Department', index=True,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                tracking=True,
                                history=True, ondelete='restrict')
    parent_id_domain = fields.Char(compute='_compute_parent_id_domain')
    name = fields.Char('Department Name', required=True, tracking=True, history=True)
    short_name = fields.Char(string="Nombre corto", tracking=True, history=True)
    function_nature = fields.Selection(string=u"Naturaleza de la función",
                                       selection=[
                                           ('adviser', 'Asesora'),
                                           ('operative', 'Ejecutora'),
                                           ('comite', 'Comité/Comisión'),
                                           ('program', 'Programa/Proyecto'),
                                       ], tracking=True, history=True)
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel jerárquico",
                                            tracking=True,
                                            ondelete='restrict',
                                            history=True)
    hierarchical_level_order = fields.Integer(string="Orden", related='hierarchical_level_id.order', store=True)
    hierarchical_level_id_domain = fields.Char(compute='_compute_hierarchical_level_id_domain')
    function_nature_form = fields.Selection(string="Tipo de formulario (atendiendo la naturaleza)",
                                            selection=[('form1', 'Formulario 1'),
                                                       ('form2', 'Formulario 2'), ],
                                            compute='_compute_function_nature_form',
                                            store=True)
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

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime('Fecha de última modificación', index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    complete_name = fields.Char('Complete Name',
                                compute='_compute_complete_name',
                                recursive=True,
                                store=True,
                                history=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for department in self:
            if department.parent_id:
                department.complete_name = '%s / %s' % (department.parent_id.complete_name, department.name)
            else:
                department.complete_name = department.name

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
            if record.function_nature in ['program', 'comite']:
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
        self.parent_id = False

    @api.onchange('hierarchical_level_id')
    def onchange_hierarchical_level_id(self):
        self.parent_id = False

    @api.onchange('function_nature_form')
    def onchange_function_nature_form(self):
        if self.function_nature_form == 'form2':
            self.short_name = False
            self.category = False
            self.mission = False
            self.process_contributor = False
            self.reponsability_ids = [(5,)]

    def unlink(self):
        if self.filtered(lambda x: x.is_approve_cgn):
            raise ValidationError(_("No se puede eliminar una UO luego de ser aprobada por CGN"))
        return super(Department, self).unlink()

    def toggle_active(self):
        self._check_toggle_active()
        return super(Department, self.with_context(no_check_write=True)).toggle_active()

    def _check_toggle_active(self):
        for record in self.filtered(lambda x: x.active is True):
            if self.search_count([('id', '!=', record.id), ('id', 'child_of', record.id), ('active', '=', True)]):
                raise ValidationError(_(u"No puede desactivar una Unidad organizativa si tiene dependencias activas!"))
        return super(Department, self)._check_toggle_active()

    def _action_open_view(self):
        vals = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': self._name,
            'name': 'Unidades organizativas',
            'search_view_id': [self.env.ref('onsc_catalog.onsc_catalog_department_search').id, 'search'],
            'views': [
                [self.env.ref('onsc_catalog.onsc_catalog_department_tree').id, 'tree'],
                [self.env.ref('onsc_catalog.onsc_catalog_department_form').id, 'form'],
            ]
        }
        _context = dict(self._context, default_active=False)
        if not self.env.user.has_group('onsc_catalog.group_catalog_configurador_servicio_civil'):
            if self.env.user.has_group('onsc_catalog.group_catalog_aprobador_cgn'):
                vals['context'] = dict(_context, search_default_filter_inactive_cgn=1,
                                       create=False,
                                       delete=False,
                                       edit=False)
            else:
                vals['context'] = dict(_context,
                                       create=False,
                                       delete=False,
                                       edit=False)
        else:
            vals['context'] = _context
        return vals

    @api.model
    def get_history_record_action(self, history_id, res_id):
        return super(Department, self.with_context(model_view_form_id=self.env.ref(
            'onsc_catalog.onsc_catalog_department_form').id)).get_history_record_action(history_id, res_id)

    def get_first_department_withmanager_in_tree(self, ignore_first_step=False):
        """
        ignore_first: Boolean. Ignorar el mismo departamento para forzar la busqueda al menos un escalon hacia arriba.
                                Util para casos donde no puede ser El mismo
        :return: UO con responsable o primer UO con responsable en el arbol hacia arriba
        """
        def recursive_search(department):
            if department.manager_id:
                return department
            if department.parent_id:
                return recursive_search(department.parent_id)
            return self.env['hr.department']

        if self.manager_id and not ignore_first_step:
            return self
        else:
            return recursive_search(self.parent_id)

    def get_all_managers_in_department_tree(self):
        """
        :return: Lista de todos los departamentos con responsables en el árbol hacia arriba
        """

        def recursive_search(department):
            managers = []
            if department.manager_id:
                managers.append(department.manager_id.id)
            if department.parent_id:
                managers.extend(recursive_search(department.parent_id))
            return managers
        managers_list = []

        if self.manager_id:
            managers_list.append(self.manager_id.id)
        managers_list.extend(recursive_search(self.parent_id))
        return managers_list


class DepartmentResponsability(models.Model):
    _name = "hr.department.responsability"
    _description = u"Lista de responsabilidades"

    department_id = fields.Many2one("hr.department", string="deparment_id", ondelete='restrict')
    process = fields.Char(string="Proceso", required=True)
    product = fields.Char(string="Producto", required=True)
    target = fields.Char(string="Destinatarios", required=True)


class DepartmentHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.department.history'
    _parent_model = 'hr.department'
