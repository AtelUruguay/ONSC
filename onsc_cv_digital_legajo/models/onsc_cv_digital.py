# -*- coding: utf-8 -*-


from odoo import fields, models, api, _


class ONSCCVDigital(models.Model):
    _name = 'onsc.cv.digital'
    _inherit = ['onsc.cv.digital', 'onsc.cv.legajo.abstract.common', 'onsc.legajo.abstract.legajo.security']

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_emergency_phone_id', 'emergency_service_telephone')]

    @api.model
    def domain_prefix_emergency_phone_id(self):
        country_id = self.env['res.country'].search([('code', '=', 'UY')])
        return [('country_id', 'in', country_id.ids)]

    employee_id = fields.Many2one("hr.employee", string="Empleado", compute='_compute_employee_id', store=True)
    is_docket = fields.Boolean(string="Tiene legajo")
    is_docket_active = fields.Boolean(string="Tiene legajo activo")
    # gender_date = fields.Date(string="Fecha de información género")
    gender_public_visualization_date = fields.Date(string="Fecha información visualización pública de género",
                                                   compute='_compute_gender_public_visualization_date', store=True)
    # afro_descendant_date = fields.Date(string="Fecha de información afrodescendencia")
    # status_civil_date = fields.Date(string="Fecha de información estado civil")
    address_info_date = fields.Date(string="Fecha de información domicilio",
                                    related='partner_id.address_info_date',
                                    readonly=False,
                                    store=True)
    # disability_date = fields.Date(string="Fecha de información discapacidad")
    # Datos del Legajo ----<Page>
    # institutional_email = fields.Char(string=u'Correo electrónico institucional', readonly=True)
    # digitized_document_file = fields.Binary(string=digitized_document_full_name)
    # digitized_document_filename = fields.Char('Nombre del documento Digitalizado')
    address_receipt_file = fields.Binary(related='partner_id.address_receipt_file', readonly=False)
    address_receipt_file_name = fields.Char(related='partner_id.address_receipt_file_name', readonly=False)

    # mergency_service_id = fields.Many2one("onsc.legajo.emergency", u"Servicio de emergencia móvil")
    # prefix_emergency_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
    #                                             domain=domain_prefix_emergency_phone_id,
    #                                             default=lambda self: self.env['res.country.phone'].search(
    #                                                 [('country_id.code', '=', 'UY')]))
    # emergency_service_telephone = fields.Char(related=mergency_service_id.phone,string=u'Teléfono del servicio de emergencia')
    # # TO-DO: Revisar este campo, No esta en catalogo
    # # health_provider_id = fields.Many2one("model", u"Prestador de Salud")
    # blood_type = fields.Selection(BLOOD_TYPE, string=u'Tipo de sangre')
    information_contact_ids = fields.One2many('onsc.cv.information.contact', 'cv_digital_id',
                                              string=u'Información de Contacto')

    # other_information_official = fields.Text(string="Otra información del funcionario/a")

    @api.depends('is_cv_gender_public')
    def _compute_gender_public_visualization_date(self):
        for record in self:
            record.gender_public_visualization_date = fields.Date.today()

    @api.depends('cv_emissor_country_id', 'cv_document_type_id', 'cv_nro_doc', 'is_docket')
    def _compute_employee_id(self):
        Employee = self.env['hr.employee'].sudo()
        for record in self:
            record.employee_id = Employee.search([
                ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                ('cv_document_type_id', '=', record.cv_document_type_id.id),
                ('cv_nro_doc', '=', record.cv_nro_doc),
            ], limit=1)

    @api.onchange('is_docket')
    def onchange_is_docket(self):
        if self.is_docket is False:
            self.gender_date = False
            self.afro_descendant_date = False
            self.status_civil_date = False
            self.address_info_date = False
            self.disability_date = False

    def _check_todisable_dynamic_fields(self):
        return super(ONSCCVDigital, self)._check_todisable_dynamic_fields() or self.is_docket

    #   VALIDACION DOCUMENTAL DE LEGAJO
    def button_documentary_tovalidate(self):
        if self._context.get('documentary_validation'):
            self._update_documentary(self._context.get('documentary_validation'), 'to_validate', '')

    def button_documentary_approve(self):
        if self._context.get('documentary_validation'):
            self._update_documentary(self._context.get('documentary_validation'), 'validated', '')

    def button_documentary_reject(self):
        ctx = self._context.copy()
        ctx.update({
            'default_model_name': self._name,
            'default_res_id': len(self.ids) == 1 and self.id or 0,
            'is_documentary_reject': True
        })
        return {
            'name': _('Rechazo de %s' % self._description),
            'view_mode': 'form',
            'res_model': 'onsc.cv.reject.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def _update_documentary(self, documentary_field, state, reject_reason):
        vals = {
            '%s_documentary_validation_state' % documentary_field: state,
            '%s_documentary_reject_reason' % documentary_field: reject_reason,
            '%s_documentary_validation_date' % documentary_field: fields.Date.today(),
            '%s_documentary_user_id' % documentary_field: self.env.user.id,
        }
        self.write(vals)

    def documentary_reject(self, reject_reason):
        self._update_documentary(self._context.get('documentary_validation'), 'rejected', reject_reason)

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_cv_digital_legajo.group_legajo_validador_doc_consulta')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_cv_digital_legajo.group_legajo_validador_doc_inciso')

    def group_legajo_validador_doc_ue(self):
        return self.user_has_groups('onsc_cv_digital_legajo.group_legajo_hr_ue')


class ONSCCVInformationContact(models.Model):
    _name = 'onsc.cv.information.contact'
    _description = 'Información de Contacto'
    _inherit = 'onsc.cv.abstract.phone.validated'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'contact_person_telephone')]

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV', required=True, index=True, ondelete='cascade')
    name_contact = fields.Char(string=u'Nombre de persona de contacto', required=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # link_people_contact_id = fields.Many2one("model", u"Vínculo con persona de contacto", required=True)
    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]), required=True)
    contact_person_telephone = fields.Char(string=u'Teléfono de persona de contacto', required=True)
    phone_full = fields.Char(compute='_compute_phone_full', string=u'Teléfono de persona de contacto')
    remark_contact_person = fields.Text(string=u'Observación para la persona de contacto', required=True)

    @api.depends('prefix_phone_id', 'contact_person_telephone')
    def _compute_phone_full(self):
        for rec in self:
            rec.phone_full = '+%s %s' % (rec.prefix_phone_id.prefix_code, rec.contact_person_telephone)
