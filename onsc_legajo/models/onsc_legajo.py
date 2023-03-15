# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ONSCLegajo(models.Model):
    _name = "onsc.legajo"
    _rec_name = "employee_id"

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

    def get_available_recordsets(self, user=False):
        Job = self.env['hr.job']


    def button_open_contract(self):
        self.ensure_one()
        if self.contracts_count == 1:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_hr_contract_action')
            action['res_id'] = self.contract_ids[0].id
        else:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_hr_contract_action')
            action['domain'] = [('employee_id', '=', self.employee_id.id)]
        action['flags'] = {'initial_mode': 'view'}
        return action

    def button_open_employee(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_employee_action')
        action['res_id'] = self.employee_id.id
        return action
