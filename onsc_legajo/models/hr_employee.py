# -*- coding: utf-8 -*-
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import models, fields, api


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.partner.common.data', 'model.history']
    _history_model = 'hr.employee.history'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree', 'kanban'] and not self.env.user.has_group(
                'onsc_legajo.group_legajo_configurador_empleado'):
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    partner_id = fields.Many2one('res.partner', string='Contacto', compute='_compute_partner_id', store=True)

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)

    photo_updated_date = fields.Date(string="Fecha de foto de la/del funcionaria/o")

    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]))
    personal_phone = fields.Char(string="Teléfono particular")
    prefix_mobile_phone_id = fields.Many2one('res.country.phone', 'Prefijo del móvil',
                                             default=lambda self: self.env['res.country.phone'].search(
                                                 [('country_id.code', '=', 'UY')]))
    mobile_phone = fields.Char(string="Teléfono celular")
    email = fields.Char(string="Email")

    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Archivos adjuntos")
    attachment_count = fields.Integer(compute='_compute_attachment_ids', string="Cantidad de archivos adjuntos")

    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado',
        compute='_compute_legajo_state',
        store=True,
        history=True)

    def name_get(self):
        res = []
        for record in self:
            name = record.full_name or record.name
            if self._context.get('show_cv_nro_doc', False) and record.cv_nro_doc:
                name = record.cv_nro_doc + " - " + record.full_name or record.name
            res.append((record.id, name))
        return res
    def _custom_display_name(self):
        return self.cv_nro_doc + " - " + self.full_name or self.name

    @api.depends('cv_emissor_country_id','cv_document_type_id','cv_nro_doc')
    def _compute_partner_id(self):
        Partner = self.env['res.partner'].sudo()
        for record in self:
            record.partner_id = Partner.search([
                ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                ('cv_document_type_id', '=', record.cv_document_type_id.id),
                ('cv_nro_doc', '=', record.cv_nro_doc),
            ], limit=1)


    @api.depends('cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2')
    def _compute_full_name(self):
        for record in self:
            full_name = calc_full_name(record.cv_first_name, record.cv_second_name,
                                       record.cv_last_name_1, record.cv_last_name_2)
            if full_name:
                record.full_name = full_name
            else:
                record.full_name = record.name

    def _compute_attachment_ids(self):
        for rec in self:
            attachment_ids = self.env['ir.attachment'].sudo().search(
                [('res_id', '=', rec.id), ('res_model', '=', 'hr.employee')])
            rec.attachment_ids = attachment_ids
            rec.attachment_count = len(attachment_ids)

    @api.depends('contract_ids', 'contract_ids.legajo_state')
    def _compute_legajo_state(self):
        for rec in self:
            if rec.contract_ids.filtered(lambda x: x.legajo_state != 'baja'):
                rec.legajo_state = 'active'
            else:
                rec.legajo_state = 'egresed'

    @api.model
    def create(self, values):
        full_name = calc_full_name(values.get('cv_first_name'), values.get('cv_second_name'),
                                   values.get('cv_last_name_1'), values.get('cv_last_name_2'))
        if full_name:
            values['name'] = full_name
        elif self.env.context.get('is_legajo'):
            values['name'] = 'dummy'

        if self.env.context.get('is_legajo'):
            return super(HrEmployee, self.suspend_security()).create(values)
        else:
            return super(HrEmployee, self).create(values)

    def _set_binary_history(self, values):
        for rec in self:
            today = fields.Date.today()
            Attachment = self.env['ir.attachment']
            if values.get('document_identity_file') and rec.document_identity_file:
                Attachment.create(
                    {'name': rec.document_identity_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.document_identity_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['document_identity_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('civical_credential_file') and rec.civical_credential_file:
                Attachment.create(
                    {'name': rec.civical_credential_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.civical_credential_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['civical_credential_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('cv_gender_record_file') and rec.cv_gender_record_file:
                Attachment.create(
                    {'name': rec.cv_gender_record_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.cv_gender_record_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['cv_gender_record_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('afro_descendants_file') and rec.afro_descendants_file:
                Attachment.create(
                    {'name': rec.afro_descendants_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.afro_descendants_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['afro_descendants_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('relationship_victim_violent_file') and rec.relationship_victim_violent_file:
                Attachment.create(
                    {'name': rec.relationship_victim_violent_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.relationship_victim_violent_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['relationship_victim_violent_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('address_receipt_file') and rec.address_receipt_file:
                Attachment.create(
                    {'name': rec.address_receipt_file_name.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.address_receipt_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['address_receipt_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('document_certificate_file') and rec.document_certificate_file:
                Attachment.create(
                    {'name': rec.document_certificate_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.document_certificate_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['document_certificate_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

            if values.get('digitized_document_file') and rec.digitized_document_file:
                Attachment.create(
                    {'name': rec.digitized_document_filename.replace(".pdf", '') + " " + str(today) + ".pdf",
                     'datas': rec.digitized_document_file, 'res_model': 'hr.employee',
                     'name_field': self._fields['digitized_document_file'].string,
                     'res_id': rec.id, 'type': 'binary'})

    def write(self, values):
        history_fields = self.get_history_fields()
        if not values.get('eff_date') and set(list(values)).intersection(set(history_fields)):
            values.update({
                'eff_date': fields.Date.today()
            })
        self._set_binary_history(values)
        if self.env.context.get('is_legajo'):
            res = super(HrEmployee, self.suspend_security()).write(values)
        else:
            res = super(HrEmployee, self).write(values)
        for rec in self.filtered(lambda x: x.name != x.full_name and x.full_name):
            rec.name = rec.full_name
        return res

    def unlink(self):
        if self.env.context.get('is_legajo'):
            return super(HrEmployee, self.suspend_security()).unlink()
        else:
            return super(HrEmployee, self).unlink()

    @api.model
    def get_history_record_action(self, history_id, res_id):
        return super(HrEmployee, self.with_context(model_view_form_id=self.env.ref(
            'onsc_legajo.onsc_legajo_hr_employee_form').id)).get_history_record_action(history_id, res_id)

    def action_view_attachment(self):
        self.ensure_one()
        vals = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', 'hr.employee'), ('res_id', '=', self.id)],
            'name': 'Histórico de archivos',
            'views': [
                [self.env.ref('onsc_legajo.view_attachment_history_tree').id, 'tree'],
                [self.env.ref('onsc_legajo.view_attachment_history_form').id, 'form'],
            ]
        }
        return vals

    # INTELIGENCIA DE ENTIDAD
    def _get_legajo_employee(self, emissor_country, document_type, partner_id):
        """
        SI EXISTE EL EMPLEADO LO DEVUELVE SINO LO CREA
        :param emissor_country: Recordset a res.country
        :param document_type: Recordset a onsc.cv.document.type
        :param partner_id: Recordset a res.partner
        :return: Recordset de hr.employee
        """
        employee = self.suspend_security().search([
            ('cv_emissor_country_id', '=', emissor_country.id),
            ('cv_document_type_id', '=', document_type.id),
            ('cv_nro_doc', '=', partner_id.cv_nro_doc),
        ], limit=1)
        if not employee:
            employee = self.suspend_security().create({
                'name': calc_full_name(partner_id.cv_first_name,
                                       partner_id.cv_second_name,
                                       partner_id.cv_last_name_1,
                                       partner_id.cv_last_name_2),
                'cv_emissor_country_id': emissor_country.id,
                'cv_document_type_id': document_type.id,
                'cv_nro_doc': partner_id.cv_nro_doc,
            })
        return employee

    def obtener_subordinados(self):

        """
        :return: todos los subordinados del empleado, tanto los que lo son directamente de la misma UO, como aquellos
        que lo son por transitivdad de UOs dependientes.
        """
        return self.search([('id', 'child_of', self.id), ('id', '!=', self.id)])


class HrEmployeeHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.employee.history'
    _parent_model = 'hr.employee'

    @api.model
    def create(self, values):
        record = super(HrEmployeeHistory, self).create(values)
        return record
