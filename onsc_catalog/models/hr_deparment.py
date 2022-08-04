# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning


class Department(models.Model):
    _name = "hr.department"
    _inherit = ['hr.department', 'model.history']
    _history_model = 'hr.department.history'

    code = fields.Integer('Identificador')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', history=True)
    company_id = fields.Many2one('res.company',
                                 related='inciso_id.company_id',
                                 store=True, history=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", history=True)
    parent_id = fields.Many2one('hr.department', string='Parent Department', index=True,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                history=True)
    name = fields.Char('Department Name', required=True, history=True)
    short_name = fields.Char(string="Nombre corto", history=True)
    function_nature = fields.Selection(string=u"Naturaleza de la función",
                                       selection=[
                                           ('adviser', 'Asesora'),
                                           ('operative', 'Ejecutora'),
                                           ('comite', 'Comité'),
                                           ('commission_project', 'Comisión/Proyecto'),
                                           ('program', 'Programa'),
                                       ], history=True)
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel jerárquico", history=True)
    function_nature_form = fields.Selection(selection=[
        ('form1', 'Formulario 1'),
        ('form2', 'Formulario 2'),
    ], compute='_compute_function_nature_form', store=True)
    mission = fields.Char(string="Misión", history=True)
    reponsability_ids = fields.One2many("hr.department.responsability",
                                        inverse_name="department_id",
                                        string="Lista de responsabilidades", history=True)
    key_functional_habilities = fields.Char(string="Competencias funcionales claves", history=True)
    process_contributor = fields.Char(string="Procesos a los que contribuye", history=True)
    regulatory = fields.Char(string="Marco normativo", history=True)
    start_date = fields.Date(string='Inicio de vigencia', history=True)
    end_date = fields.Date(string='Fin de vigencia', history=True)
    category = fields.Selection(string=u"Categoría", selection=[
        ('planning', 'PLANIFICACION ESTRATEGICA'),
        ('financial_management', 'GESTION FINANCIERA'),
        ('technology', u'TECNOLOGIA y REDISEÑO DE PROCESOS'),
        ('human_management', 'GESTION HUMANA'),
    ], history=True)
    is_approve_onsc = fields.Boolean(string="Aprobado ONSC")
    approve_onsc_date = fields.Date(string=u"Fecha aprobación ONSC")
    is_approve_cgn = fields.Boolean(string="Aprobado CGN")
    approve_cgn_date = fields.Date(string=u"Fecha aprobación CGN")

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

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        if self.operating_unit_id.id is False or self.parent_id.operating_unit_id != self.operating_unit_id:
            self.parent_id = False

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

    def action_aprobar_cgn(self):
        self.write({'is_approve_cgn': True, 'approve_cgn_date': fields.Date.today(), 'active': True})

    def action_aprobar_onsc(self):
        self.write({'is_approve_onsc': True, 'approve_onsc_date': fields.Date.today()})


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
