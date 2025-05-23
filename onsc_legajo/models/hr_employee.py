# -*- coding: utf-8 -*-
import json

from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import models, fields, api

MODIFIED_FIELDS_TO_NOTIFY_SGH = [
    'cv_nro_doc',
    'full_name',
    'cv_full_name',
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_first_name',
    'cv_second_name',
    'marital_status_id',
    'cv_birthdate',
    'cv_sex',
    'country_of_birth_id',
    'crendencial_serie',
    'credential_number',
    'personal_phone',
    'mobile_phone',
    'email',
    'cv_address_state_id',
    'cv_address_location_id',
    'cv_address_street',
    'cv_address_street_id',
    'cv_address_nro_door',
    'cv_address_street2_id',
    'cv_address_street3_id',
    'cv_address_is_cv_bis',
    'cv_address_apto',
    'cv_address_place',
    'uy_citizenship',
    'cv_address_zip',
    'cv_address_block',
    'cv_address_sandlot',
    'occupational_health_card_date'
]


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.partner.common.data', 'model.history']
    _history_model = 'hr.employee.history'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(HrEmployee, self).fields_get(allfields, attributes)
        basic_search = 'onsc_legajo.onsc_legajo_hr_employee_basic_search'
        if len(self._context) and \
                self._context.get('search_view_ref', '') == basic_search and \
                not self._context.get('no_restrict_fields', False):
            for field in self._fields:
                if field in res:
                    res[field]['searchable'] = False
        return res

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
        # OCULTANDO BINARIOS DE FORMULARIO DE HISTORICOS EN FUNCIONARIO
        if view_type == 'form' and self._context.get('model_history', False):
            for potential_file_field in doc.xpath("//field"):
                if '_file' in potential_file_field.get('name') and potential_file_field.get('filename'):
                    potential_file_field.set('invisible', '1')
                    modifiers = json.loads(potential_file_field.get("modifiers") or "{}")
                    modifiers['invisible'] = True
                    potential_file_field.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        new_args = []
        for args_item in args:
            if (isinstance(args_item, tuple) or isinstance(args_item, list)) and args_item[0] == 'name' and len(
                    args_item) == 3:
                new_args.append('|')
                new_args.append(args_item)
                new_args.append(('cv_nro_doc', args_item[1], args_item[2]))
            else:
                new_args.append(args_item)
        return super(HrEmployee, self)._search(new_args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)

    partner_id = fields.Many2one('res.partner', string='Contacto', compute='_compute_partner_id', store=True)

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    photo_updated_date = fields.Date(string="Fecha de foto de la/del funcionaria/o")
    country_of_birth_id = fields.Many2one(
        "res.country",
        string="País de nacimiento")
    uy_citizenship = fields.Selection(
        string="Ciudadanía uruguaya",
        selection=[
            ('legal', 'Legal'), ('natural', 'Natural'),
            ('extranjero', 'Extranjero')],
        history=True)
    prefix_phone_id = fields.Many2one(
        'res.country.phone', 'Prefijo',
        default=lambda self: self.env['res.country.phone'].search([('country_id.code', '=', 'UY')]))
    personal_phone = fields.Char(string="Teléfono particular")
    prefix_mobile_phone_id = fields.Many2one(
        'res.country.phone', 'Prefijo del móvil',
        default=lambda self: self.env['res.country.phone'].search([('country_id.code', '=', 'UY')])
    )
    mobile_phone = fields.Char(string="Teléfono celular")
    email = fields.Char(string="Email")
    cv_sex_updated_date = fields.Date(u'Fecha de información sexo', history=True)

    professional_resume = fields.Text(string="Resumen profesional", history=True)
    user_linkedIn = fields.Char(string="Usuario en LinkedIn", history=True)

    # Domicilio
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)',
        groups="hr.group_hr_user,onsc_legajo.group_legajo_configurador_empleado,onsc_base.group_base_onsc",
        tracking=True,
        history=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    cv_address_state_id = fields.Many2one('res.country.state', string='Departamento', history=True)
    cv_address_nro_door = fields.Char(u'Número', history=True)
    cv_address_apto = fields.Char(u'Apto', history=True)
    cv_address_street = fields.Char(u'Calle', history=True)
    cv_address_zip = fields.Char(u'Código postal', history=True)
    cv_address_is_cv_bis = fields.Boolean(u'BIS', history=True)
    cv_address_amplification = fields.Text(u"Aclaraciones")
    cv_address_place = fields.Text(string="Paraje", size=200, history=True)
    cv_address_block = fields.Char(string="Manzana", size=5, history=True)
    cv_address_sandlot = fields.Char(string="Solar", size=5, history=True)
    address_receipt_file = fields.Binary('Documento digitalizado "Constancia de domicilio"')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')
    address_info_date = fields.Date(string="Fecha de información domicilio",
                                    readonly=False,
                                    store=True)

    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Archivos adjuntos")
    attachment_count = fields.Integer(compute='_compute_attachment_ids', string="Cantidad de archivos adjuntos")

    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado',
        compute='_compute_legajo_state',
        store=True,
        history=True)
    notify_sgh = fields.Boolean("Notificar SGH")

    def name_get(self):
        # return super(HrEmployeePrivate, self).name_get()
        res = []
        for record in self:
            name = record.full_name or record.name
            if self._context.get('show_cv_nro_doc', False) and record.cv_nro_doc:
                name = record.cv_nro_doc + " - " + record.full_name or record.name
            res.append((record.id, name))
        return res

    def _custom_display_name(self):
        return self.cv_nro_doc + " - " + self.full_name or self.name

    @api.depends('cv_emissor_country_id', 'cv_document_type_id', 'cv_nro_doc')
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
        if self.env.context.get('is_legajo'):
            return super(HrEmployee, self.suspend_security()).create(values)
        else:
            return super(HrEmployee, self).create(values)

    def write(self, values):
        if not self._context.get('consolidate_history_version'):
            self = self.with_context(consolidate_history_version=str(fields.Datetime.now()))
        history_fields = self.get_history_fields()
        no_post_history = self._context.get('no_post_history', False)
        if not values.get('eff_date') and set(list(values)).intersection(set(history_fields)) and not no_post_history:
            values.update({
                'eff_date': fields.Date.today()
            })
        self._set_binary_history(values)
        self._notify_sgh(values)
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

    def action_view_attachment(self):
        self.ensure_one()
        return {
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

    def _notify_sgh(self, values):
        BaseUtils = self.env['onsc.base.utils'].sudo()
        employees_notified_ids = []
        for record in self.filtered(lambda x: x.legajo_state == 'active'):
            values_filtered = BaseUtils.get_really_values_changed(record, values)
            for modified_field in MODIFIED_FIELDS_TO_NOTIFY_SGH:
                if modified_field in values_filtered and record.id not in employees_notified_ids:
                    employees_notified_ids.append(record.id)
                    record.notify_sgh = True

    @api.model
    def get_history_record_action(self, history_id, res_id):
        return super(HrEmployee, self.with_context(model_view_form_id=self.env.ref(
            'onsc_legajo.onsc_legajo_hr_employee_form').id)).get_history_record_action(history_id, res_id)

    def _get_really_values_changed(self, values):
        """
        FILTRA DE TODOS LOS VALORES QUE SE MANDAN A CAMBIAR EN UN EMPLEADO CUALES REALMENTE TIENEN DIFERENCIA
        :param values: Dict of values, ejemplo: los que vienen en un write
        :return: Dict of values: los que realmente cambiaron
        """
        values_filtered = {}
        _fields_get = self.with_context(no_restrict_fields=True).fields_get()
        for key, value in values.items():
            field_type = _fields_get.get(key).get('type')
            if field_type in ('integer', 'binary', 'date', 'datetime'):
                eval_str = "self.%s"
            elif field_type == 'many2one':
                eval_str = "self.%s.id"
            elif field_type in ['many2many', 'one2many']:
                eval_str = "self.%s.ids"
            else:
                eval_str = "self.%s"
            if eval(eval_str % (key)) != value:
                values_filtered.update({key: value})
        return values_filtered

    # INTELIGENCIA DE ENTIDAD
    def _get_legajo_employee(self, emissor_country, document_type, partner_id, notify_sgh=False):
        """
        SI EXISTE EL EMPLEADO LO DEVUELVE SINO LO CREA
        :param emissor_country: Recordset a res.country
        :param document_type: Recordset a onsc.cv.document.type
        :param partner_id: Recordset a res.partner
        :param notify_sgh: Boolean
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
                'notify_sgh': notify_sgh,
            })
        elif self._context.get('force_notify_sgh') and employee.legajo_state == 'egresed':
            employee.notify_sgh = True
        return employee


class HrEmployeeHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.employee.history'
    _parent_model = 'hr.employee'

    @api.model
    def create(self, values):
        record = super(HrEmployeeHistory, self).create(values)
        return record
