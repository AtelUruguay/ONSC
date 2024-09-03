# -*- coding:utf-8 -*-
import json
import logging

from email_validator import EmailNotValidError, validate_email
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
]
# campos requeridos para la sincronización

REQUIRED_FIELDS = ['end_date', 'reason_description', 'norm_id', 'resolution_description', 'resolution_date',
                   'resolution_type', 'causes_discharge_id', 'contract_id']


class ONSCLegajoBajaVL(models.Model):
    _name = 'onsc.legajo.baja.vl'
    _inherit = [
        'onsc.legajo.actions.common.data',
        'onsc.partner.common.data',
        'mail.thread',
        'mail.activity.mixin',
        'onsc.legajo.abstract.opbase.security'
    ]
    _description = 'Baja de vínculo laboral'
    _rec_name = 'full_name'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajoBajaVL, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                            submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_baja_vl = self.env.user.has_group('onsc_legajo.group_legajo_baja_vl_consulta_bajas_vl')
        is_user_administrar_baja_vl = self.env.user.has_group('onsc_legajo.group_legajo_baja_vl_administrar_bajas')
        if view_type in ['form', 'tree', 'kanban'] and is_user_baja_vl and not is_user_administrar_baja_vl:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
            for node_form in doc.xpath("//button[@name='action_call_ws9']"):
                node_form.getparent().remove(node_form)
        res['arch'] = etree.tostring(doc)
        return res

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_ue')

    def _get_domain(self, args):
        return super(ONSCLegajoBajaVL, self)._get_domain(args, use_employee=True)

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoBajaVL, self).default_get(fields)
        res['cv_emissor_country_id'] = self.env.ref('base.uy').id
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                                     limit=1).id or False
        return res

    def read(self, fields=None, load="_classic_read"):
        Employee = self.env['hr.employee'].sudo()
        result = super(ONSCLegajoBajaVL, self).read(fields, load)
        for item in result:
            if item.get('employee_id'):
                employee_id = item['employee_id'][0]
                item['employee_id'] = (item['employee_id'][0], Employee.browse(employee_id)._custom_display_name())
        return result

    employee_id = fields.Many2one("hr.employee", string="Funcionario")
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain')
    contract_id = fields.Many2one('hr.contract', 'Contrato', copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    end_date = fields.Date(string="Fecha de Baja", required=True, copy=False)

    causes_discharge_id = fields.Many2one('onsc.legajo.causes.discharge', string='Causal de Egreso', copy=False)
    causes_discharge_extended_id = fields.Many2one("onsc.legajo.causes.discharge.line",
                                                   string="Causal de egreso extendido",
                                                   domain="[('causes_discharge_id', '=', causes_discharge_id)]",
                                                   history=True)

    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'baja_vl_id',
                                                      string='Documentos adjuntos')
    id_baja = fields.Char(string="Id Baja")

    is_require_extended = fields.Boolean("¿Requiere extendido?", compute="_compute_is_require_extended")
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    is_ready_send_sgh = fields.Boolean(string="Listo para enviar", compute='_compute_is_ready_to_send')
    full_name = fields.Char('Nombre', compute='_compute_full_name')
    is_read_only_description = fields.Boolean(
        "Solo lectura los campos descripcion y norma",
        compute='_compute_is_read_only_description',
        store=True
    )

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['borrador', 'error_sgh']

    @api.depends('cv_emissor_country_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()

    @api.depends('employee_id')
    def _compute_contract_id_domain(self):
        Contract = self.env['hr.contract']
        for rec in self:
            if rec.employee_id:
                args = [("legajo_state", "=", 'active'), ('employee_id', '=', rec.employee_id.id)]
                args = self._get_domain(args)
                contracts = Contract.search(args)
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
            else:
                rec.contract_id_domain = json.dumps([('id', '=', False)])

    @api.depends('contract_id')
    def _compute_is_ready_to_send(self):
        for record in self:
            record.is_ready_send_sgh = bool(record.contract_id)

    @api.depends('causes_discharge_id')
    def _compute_is_require_extended(self):
        for rec in self:
            if rec.causes_discharge_id:
                rec.is_require_extended = rec.causes_discharge_id.is_require_extended
            else:
                rec.is_require_extended = False

    @api.depends('employee_id')
    def _compute_full_name(self):
        for record in self:
            record.full_name = record.employee_id.cv_nro_doc + ' - ' + calc_full_name(
                record.employee_id.cv_first_name, record.employee_id.cv_second_name,
                record.employee_id.cv_last_name_1,
                record.employee_id.cv_last_name_2) + ' - ' + record.end_date.strftime('%Y%m%d')

    @api.depends('causes_discharge_id','causes_discharge_extended_id','state')
    def _compute_is_read_only_description(self):
        for record in self:
            if record.state not in ['borrador','error_sgh']:
                record.is_read_only_description = True
            elif not record.causes_discharge_id.is_require_extended and (
                record.causes_discharge_id.reason_description or record.causes_discharge_id.resolution_description or record.causes_discharge_id.norm_id):
                record.is_read_only_description = True
            elif record.causes_discharge_extended_id.reason_description or record.causes_discharge_extended_id.resolution_description or record.causes_discharge_extended_id.norm_id:
                record.is_read_only_description = True
            else:
                record.is_read_only_description = False


    @api.constrains("end_date")
    def _check_date(self):
        for record in self:
            if record.end_date > fields.Date.today():
                raise ValidationError(_("La fecha baja debe ser menor o igual a la fecha de registro"))

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.operating_unit_id = self.contract_id.operating_unit_id.id
        self.inciso_id = self.contract_id.inciso_id.id

    @api.onchange('causes_discharge_id')
    def onchange_causes_discharge(self):
        if not self.causes_discharge_id.is_require_extended and (
                self.causes_discharge_id.reason_description or self.causes_discharge_id.resolution_description or self.causes_discharge_id.norm_id):
            self.reason_description = self.causes_discharge_id.reason_description
            self.resolution_description = self.causes_discharge_id.resolution_description
            self.norm_id = self.causes_discharge_id.norm_id
            # self.is_read_only_description = True
        else:
            # self.is_read_only_description = False
            self.reason_description = False
            self.resolution_description = False
            self.norm_id = False
            self.causes_discharge_extended_id = False

    @api.onchange('causes_discharge_extended_id')
    def onchange_causes_discharge_extended_id(self):
        if self.causes_discharge_extended_id.reason_description or self.causes_discharge_extended_id.resolution_description or self.causes_discharge_extended_id.norm_id:
            self.reason_description = self.causes_discharge_extended_id.reason_description
            self.resolution_description = self.causes_discharge_extended_id.resolution_description
            self.norm_id = self.causes_discharge_extended_id.norm_id
            # self.is_read_only_description = True
        else:
            self.reason_description = False
            self.resolution_description = False
            self.norm_id = False
            # self.is_read_only_description = False

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super(ONSCLegajoBajaVL, self).unlink()

    def action_call_ws9(self):
        self._check_required_fieds_ws9()
        self._message_log(body=_('Envia a SGH'))
        self.env['onsc.legajo.abstract.baja.vl.ws9'].suspend_security().syncronize(self)

    def action_aprobado_cgn(self):
        data = {
            'id_deregistration_discharge': self.id_baja,
            'reason_deregistration': self.reason_description or False,
            'norm_code_deregistration_id': self.norm_id and self.norm_id.id or False,
            'type_norm_deregistration': self.norm_type or False,
            'norm_number_deregistration': self.norm_number or False,
            'norm_year_deregistration': self.norm_year or False,
            'norm_article_deregistration': self.norm_article or False,
            'resolution_description_deregistration': self.resolution_description or False,
            'resolution_date_deregistration': self.resolution_date or False,
            'resolution_type_deregistration': self.resolution_type or False,
            'causes_discharge_id': self.causes_discharge_id and self.causes_discharge_id.id or False,
            'additional_information_deregistration': self.additional_information,
            'legajo_state': 'baja',
            'causes_discharge_extended': self.causes_discharge_extended_id and self.causes_discharge_extended_id.id or False
        }

        for attach in self.attached_document_discharge_ids:
            attach.write({
                'contract_id': self.contract_id.id,
                'type': 'deregistration'
            })
        self.contract_id.suspend_security().write(data)
        self.with_context(no_check_write=True).contract_id.suspend_security().deactivate_legajo_contract(
            date_end=self.end_date
        )
        self.suspend_security().write({'state': 'aprobado_cgn'})
        self._send_aprobado_notification()
        return True

    def action_rechazado_cgn(self):
        self.write({'state': 'rechazado_cgn'})
        self._send_rechazado_notification()
        return True

    def _send_aprobado_notification(self):
        validation_email_template_id = self.env.ref('onsc_legajo.email_template_bajavl_aprobada')
        validation_email_template_id.send_mail(self.id, force_send=True)

    def _send_rechazado_notification(self):
        validation_email_template_id = self.env.ref('onsc_legajo.email_template_bajavl_rechazada')
        validation_email_template_id.send_mail(self.id, force_send=True)

    def button_open_contract(self):
        self.ensure_one()
        if self.contract_id:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_hr_contract_action')
            action.update({'res_id': self.contract_id.id})
            return action
        else:
            return True

    def _get_domain_employee_ids(self):
        args = [("legajo_state", "=", 'active')]
        args = self._get_domain(args)

        employees = self.env['hr.contract'].search(args).mapped('employee_id')
        if employees:
            return json.dumps([('id', 'in', employees.ids)])
        else:
            return json.dumps([('id', '=', False)])

    def _check_required_fieds_ws9(self):
        for record in self:
            message = []
            for required_field in REQUIRED_FIELDS:
                if not eval('record.%s' % required_field):
                    message.append(record._fields[required_field].string)
            if not record.employee_id.cv_nro_doc:
                message.append(_("Debe tener numero de documento"))

            if record.contract_id.legajo_state != 'active':
                message.append(_("El contrato debe estar activo "))

            if not record.attached_document_discharge_ids:
                message.append(_("Debe haber al menos un documento adjunto"))

        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))
        return True

    def get_followers_mails(self):
        followers_emails = []
        for follower in self.message_follower_ids:
            try:
                partner_email = follower.partner_id.email
                validate_email(partner_email)
                followers_emails.append(partner_email)
            except EmailNotValidError:
                # Si el email no es válido, se captura la excepción
                _logger.info(_("Mail de Contacto no válido: %s") % follower.partner_id.email)
        return ','.join(followers_emails)

    def get_bajavl_name(self):
        return self.employee_id.display_name
