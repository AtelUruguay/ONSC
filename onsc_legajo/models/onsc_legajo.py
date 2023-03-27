# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, models, fields
from odoo.osv import expression


class ONSCLegajo(models.Model):
    _name = "onsc.legajo"
    _rec_name = "employee_id"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree', 'kanban'] and not self.env.user.has_group(
                'onsc_legajo.group_legajo_configurador_legajo'):
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def _get_expression_domain(self, args):
        available_contracts = self._get_user_available_contract()
        args = expression.AND([[
            ('employee_id', 'in', available_contracts.mapped('employee_id').ids)
        ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        args = self._get_expression_domain(args)
        return super(ONSCLegajo, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        domain = self._get_expression_domain(domain)
        return super(ONSCLegajo, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                                  lazy=lazy)

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
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

    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920,
                              related='employee_id.image_1920', store=True)
    avatar_128 = fields.Image(string='Avatar 128', max_width=128, max_height=128,
                              related='employee_id.avatar_128', store=True)

    public_admin_entry_date = fields.Date(string=u'Fecha de ingreso a la administración pública')
    public_admin_inactivity_years_qty = fields.Integer(string=u'Años de inactividad')

    contract_ids = fields.One2many('hr.contract', related='employee_id.contract_ids')
    contracts_count = fields.Integer(string='Contract Count', related='employee_id.contracts_count')

    def _compute_contract_info(self):
        for record in self:
            available_contracts = record._get_user_available_contract()
            record.contract_ids = available_contracts
            record.contracts_count = len(available_contracts)

    # is_disassociated = fields.Boolean(string="Es egresado", compute='_compute_is_disassociated')
    #
    # @api.depends('contract_ids')
    # def _compute_is_disassociated(self):
    #     user_inciso = self.env.user.employee_id.job_id.contract_id.inciso_id
    #     for record in self:
    #         any_contract_active = record.contract_ids.filtered(lambda x:x.legajo_state != 'baja')
    #         if len(any_contract_active) == 0 and len(record.contract_ids) > 0 and record.contract_ids.sorted(key=lambda x: x.date_end, reverse=True)[0].inciso_id == user_inciso:
    #             record.is_disassociated = True

    def button_open_contract(self):
        self.ensure_one()
        if self.contracts_count == 0:
            return True
        elif self.contracts_count == 1:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_hr_contract_action')
            action['res_id'] = self.contract_ids[0].id
        else:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_hr_contract_action')
            action['domain'] = [('employee_id', '=', self.employee_id.id)]
        return action

    def button_open_employee(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_employee_action')
        action['res_id'] = self.employee_id.id
        return action

    def _action_milegajo(self):
        ctx = self.env.context.copy()
        ctx['mi_legajo'] = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'name': 'Mi legajo',
            'context': ctx,
            "target": "main",
            "res_id": self.sudo().search([('employee_id', '=', self.env.user.employee_id.id)], limit=1).id,
        }

    @api.model
    def _get_user_available_contract(self):
        available_contracts = self.env['hr.contract']
        if self._context.get('mi_legajo'):
            employees = self.env.user.employee_id
        else:
            employees = self.employee_id or self.env['hr.employee'].search([])
        if self._context.get('mi_legajo') or self.user_has_groups(
                'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador_legajo'):
            available_contracts = employees.mapped('contract_ids')
        elif self.user_has_groups(
                'onsc_legajo.group_legajo_hr_inciso'):
            contract = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract.inciso_id.id
            if inciso_id:
                available_contracts = employees.mapped('contract_ids').filtered(
                    lambda x: x.inciso_id.id == inciso_id and x.legajo_state in ['active', 'outgoing_commission',
                                                                                 'incoming_commission'])
        elif self.user_has_groups(
                'onsc_legajo.group_legajo_hr_ue'):
            contract = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract.operating_unit_id.id
            if operating_unit_id:
                available_contracts = employees.mapped('contract_ids').filtered(
                    lambda x: x.operating_unit_id.id == operating_unit_id and x.legajo_state in ['active',
                                                                                                 'outgoing_commission',
                                                                                                 'incoming_commission'])
        return available_contracts
