# -*- coding:utf-8 -*-
import json

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

# campos requeridos para la sincronización

REQUIRED_FIELDS = {'end_date', 'reason_description', 'norm_number', 'norm_article', 'norm_type', 'norm_year',
                   'resolution_description', 'resolution_date', 'resolution_type', 'extinction_commission_id'}


class ONSCLegajoBajaCS(models.Model):
    _name = 'onsc.legajo.baja.cs'
    _inherit = ['onsc.legajo.actions.common.data', 'onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin']
    _description = 'Baja de Comisión  Servicio'
    _rec_name = 'employee_id'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajoBajaCS, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                            submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_baja_cs = self.env.user.has_group('onsc_legajo.group_legajo_baja_cs_consulta_bajas_cs')
        is_user_administrar_baja_cs = self.env.user.has_group('onsc_legajo.group_legajo_baja_cs_administrar_bajas')
        if view_type in ['form', 'tree', 'kanban'] and is_user_baja_cs and not is_user_administrar_baja_cs:
            for node_form in doc.xpath("//%s" % view_type):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
            for node_form in doc.xpath("//button[@name='action_call_ws11']"):
                node_form.getparent().remove(node_form)
        res['arch'] = etree.tostring(doc)
        return res

    def _get_domain(self, args):
        args = expression.AND([[('employee_id', '!=', self.env.user.employee_id.id)], args])
        if self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id)], args])
            elif self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue'):
                contract_id = self.env.user.employee_id.job_id.contract_id
                inciso_id = contract_id.inciso_id
                operating_unit_id = contract_id.operating_unit_id
                if inciso_id:
                    args = expression.AND([[('inciso_id', '=', inciso_id.id)], args])
                if operating_unit_id:
                    args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id)], args])
        return args

    def _get_domain_contract(self, args, employee_id):
        args = expression.AND([[('employee_id', '!=', self.env.user.employee_id.id)], args])
        if self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id), ('legajo_state', '=', 'incoming_commission'),
                                        ('employee_id', '=', employee_id),
                                        ('employee_id', '!=', self.env.user.employee_id.id)], args])

                args = expression.OR([[('inciso_id', '=', inciso_id.id), ('legajo_state', '=', 'outgoing_commission'),
                                       ('cs_contract_id.inciso_id.is_central_administration', '=', False),
                                       ('employee_id', '=', employee_id),
                                       ('employee_id', '!=', self.env.user.employee_id.id)], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id)], args])
            if operating_unit_id:
                args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id)], args])
            if employee_id:
                args = expression.AND(
                    [[('employee_id', '=', employee_id), ('employee_id', '!=', self.env.user.employee_id.id)], args])
            args2 = args
            args = expression.AND([[('legajo_state', '=', 'incoming_commission')], args])
            args2 = expression.AND([[('legajo_state', '=', 'outgoing_commission'),
                                     ('cs_contract_id.inciso_id.is_central_administration', '=', False)], args2])
            args = expression.OR([args2, args])
        else:
            args = expression.AND(
                [[('employee_id', '=', employee_id), ('employee_id', '!=', self.env.user.employee_id.id)], args])
        return args

    def _get_domain_employee(self, args):
        if self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id), ('legajo_state', '=', 'incoming_commission'),
                                        ('employee_id', '!=', self.env.user.employee_id.id)], args])

                args = expression.OR([[('inciso_id', '=', inciso_id.id), ('legajo_state', '=', 'outgoing_commission'),
                                       ('cs_contract_id.inciso_id.is_central_administration', '=', False),
                                       ('employee_id', '!=', self.env.user.employee_id.id)], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id)], args])
            if operating_unit_id:
                args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id)], args])

            args = expression.AND([[('employee_id', '!=', self.env.user.employee_id.id)], args])
            args2 = args
            args = expression.AND([[('legajo_state', '=', 'incoming_commission')], args])
            args2 = expression.AND([[('legajo_state', '=', 'outgoing_commission'),
                                     ('cs_contract_id.inciso_id.is_central_administration', '=', False)], args2])
            args = expression.OR([args2, args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCLegajoBajaCS, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def read(self, fields=None, load="_classic_read"):
        Employee = self.env['hr.employee'].sudo()
        result = super(ONSCLegajoBajaCS, self).read(fields, load)
        for item in result:
            if item.get('employee_id'):
                employee_id = item['employee_id'][0]
                item['employee_id'] = (item['employee_id'][0], Employee.browse(employee_id)._custom_display_name())
        return result

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoBajaCS, self).default_get(fields)
        res['cv_emissor_country_id'] = self.env.ref('base.uy').id
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                                     limit=1).id or False
        res['show_contract'] = False
        return res

    employee_id = fields.Many2one("hr.employee", string="Funcionario", copy=False)
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain', copy=False)
    contract_id = fields.Many2one('hr.contract', 'Contrato', copy=False)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', related='contract_id.inciso_id')
    inciso_origen_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', related='contract_id.inciso_origin_id')
    operating_unit_origen_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                               related='contract_id.operating_unit_origin_id')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        related='contract_id.operating_unit_id')
    program = fields.Char(string='Programa ', related='contract_id.program')
    project = fields.Char(string='Proyecto ', related='contract_id.project')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen', related='contract_id.regime_id')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1',
                                     related='contract_id.descriptor1_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2',
                                     related='contract_id.descriptor2_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3',
                                     related='contract_id.descriptor3_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4',
                                     related='contract_id.descriptor4_id')
    end_date = fields.Date(string="Fecha hasta de  la Comisión", default=lambda *a: fields.Date.today(), required=True,
                           copy=False)
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission",
                                               string="Motivo extinción de la comisión", copy=False)
    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'baja_cs_id',
                                                      string='Documentos adjuntos', copy=False)
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain', store=True)
    show_contract = fields.Boolean('Show Contract')

    @api.constrains("end_date")
    def _check_date(self):
        for record in self:
            if record.end_date > fields.Date.today():
                raise ValidationError(_("La Fecha hasta de  la Comisión debe ser menor o igual  al día de baja"))

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
                rec.show_contract = False
                args = []
                args = self._get_domain_contract(args, rec.employee_id.id)
                contract = Contract.search(args)
                if contract:
                    if len(contract) > 1:
                        rec.show_contract = True
                    rec.contract_id_domain = json.dumps([('id', 'in', contract.ids)])
                    rec.contract_id = contract[0].id
                else:
                    rec.contract_id_domain = json.dumps([('id', '=', False)])
            else:
                rec.contract_id_domain = json.dumps([('id', '=', False)])

    def action_call_ws11(self):
        self._check_required_fieds_ws11()
        self.env['onsc.legajo.abstract.baja.vl.ws11'].suspend_security().syncronize(self)

    def _get_domain_employee_ids(self):
        args = []
        args = self._get_domain_employee(args)
        employees = self.env['hr.contract'].search(args).mapped('employee_id')
        if employees:
            return json.dumps([('id', 'in', employees.ids)])
        else:
            return json.dumps([('id', '=', False)])

    def _check_required_fieds_ws11(self):
        message = []
        for record in self:
            for required_field in REQUIRED_FIELDS:
                if not eval('record.%s' % required_field):
                    message.append(record._fields[required_field].string)

            if not record.employee_id.cv_nro_doc:
                message.append(_("Debe tener numero de documento"))

            if not record.contract_id or not record.contract_id.sec_position:
                message.append(_("El contrato debe tener Sec. Plaza definido"))

            if not record.extinction_commission_id or not record.extinction_commission_id.code:
                message.append(_("El contrato debe tener Sec. Plaza definido"))

            if not record.attached_document_discharge_ids:
                message.append(_("Debe haber al menos un documento adjunto"))

            if message:
                fields_str = '\n'.join(message)
                message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
                raise ValidationError(_(message))
        return True

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super(ONSCLegajoBajaCS, self).unlink()

    def action_actualizar_puesto(self):
        ContratoOrigen = self.env['hr.contract'].sudo().search([("cs_contract_id", "=", self.contract_id.id)])
        if self.inciso_id.is_central_administration and ContratoOrigen.inciso_id.is_central_administration:
            ContratoOrigen.suspend_security().activate_legajo_contract()
            ContratoOrigen.suspend_security().write({'cs_contract_id': False, })
            self.contract_id.suspend_security().job_ids.filtered(lambda x: x.end_date is False).write(
                {'end_date': self.end_date})
        elif not self.inciso_id.is_central_administration and ContratoOrigen.inciso_id.is_central_administration:
            ContratoOrigen.suspend_security().activate_legajo_contract()
            ContratoOrigen.suspend_security().write({'cs_contract_id': False, })
        elif self.contract_id.inciso_id.is_central_administration and not \
                ContratoOrigen.inciso_id.is_central_administration:
            self.contract_id.suspend_security().job_ids.filtered(lambda x: x.end_date is False).write(
                {'end_date': self.end_date})

        self.contract_id.suspend_security().deactivate_legajo_contract(self.end_date)
        self.write({'state': 'confirmado', 'is_error_synchronization': False, 'error_message_synchronization': ''})
        return True
