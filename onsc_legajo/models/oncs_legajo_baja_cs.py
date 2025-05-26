# -*- coding:utf-8 -*-
import json

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

# campos requeridos para la sincronización

REQUIRED_FIELDS = {'end_date', 'reason_description', 'norm_id', 'norm_article', 'norm_type', 'norm_year',
                   'resolution_description', 'resolution_date', 'resolution_type', 'extinction_commission_id'}

STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
    ('confirmado', 'Confirmado'),
    ('communication_error', 'Error de comunicación'),
]


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
        apply_filter = not self.user_has_groups(
            'onsc_legajo.group_legajo_baja_cs_consulta_bajas') and not self.user_has_groups(
            'onsc_legajo.group_legajo_baja_cs_administrar_bajas')
        args = expression.AND([[('employee_id', '!=', self.env.user.employee_id.id)], args])
        if apply_filter and self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args2 = args
                args = expression.AND(
                    [[('inciso_id', '=', inciso_id.id)], args])
                args2 = expression.AND([[('inciso_id.is_central_administration', '=', False),
                                         ('inciso_origen_id', '=', inciso_id.id)], args2])
                args = expression.OR([args2, args])
        elif apply_filter and self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            args2 = args
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id)], args])
                args2 = expression.AND([[('inciso_id.is_central_administration', '=', False),
                                         ('inciso_origen_id', '=', inciso_id.id)], args2])
            if operating_unit_id:
                args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id), ], args])
                args2 = expression.AND([[('inciso_id.is_central_administration', '=', False),
                                         ('operating_unit_origen_id', '=', operating_unit_id.id)], args2])
            args = expression.OR([args2, args])
        return args

    def _get_domain_contract(self, args, employee_id):
        if self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[('inciso_id', '=', inciso_id.id),
                                        ('legajo_state', '=', 'incoming_commission')], args])

                args = expression.OR(
                    [['&', '&', '|',
                      ('inciso_origin_id', '=', inciso_id.id),
                      ('cs_contract_id.inciso_id', '=', inciso_id.id),
                      ('legajo_state', '=', 'incoming_commission'),
                      ('inciso_id.is_central_administration', '=', False)], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract_id.operating_unit_id

            args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id),
                                    ('legajo_state', '=', 'incoming_commission')], args])

            args = expression.OR(
                [['&', '&', '|',
                  ('operating_unit_origin_id', '=', operating_unit_id.id),
                  ('cs_contract_id.operating_unit_id', '=', operating_unit_id.id),
                  ('legajo_state', '=', 'incoming_commission'),
                  ('inciso_id.is_central_administration', '=', False)], args])
        else:
            args = expression.AND(
                [[('legajo_state', '=', 'incoming_commission')], args])
        args = expression.AND([[
            ('employee_id', '=', employee_id),
            ('employee_id', '!=', self.env.user.employee_id.id)], args])
        return args

    def _get_domain_employee(self, args):
        if self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            args = expression.AND([[('inciso_id', '=', inciso_id.id), ('legajo_state', '=', 'incoming_commission'),
                                    ('employee_id', '!=', self.env.user.employee_id.id)], args])
            # CS_CONTRACT_ID
            args = expression.OR([[('cs_contract_id.inciso_id', '=', inciso_id.id),
                                   ('legajo_state', '=', 'incoming_commission'),
                                   ('inciso_id.is_central_administration', '=', False),
                                   ('employee_id', '!=', self.env.user.employee_id.id)], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            operating_unit_id = contract_id.operating_unit_id
            args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id), ('legajo_state', '=', 'incoming_commission'),
                                    ('employee_id', '!=', self.env.user.employee_id.id)], args])

            # cs_contract_id
            args = expression.OR([[('cs_contract_id.operating_unit_id', '=', operating_unit_id.id),
                                   ('legajo_state', '=', 'incoming_commission'),
                                   ('inciso_id.is_central_administration', '=', False),
                                   ('employee_id', '!=', self.env.user.employee_id.id)], args])
        else:
            args = expression.AND(
                [[('employee_id', '!=', self.env.user.employee_id.id),
                  ('legajo_state', 'in', ('incoming_commission', 'outgoing_commission'))], args])
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
        return res

    employee_id = fields.Many2one("hr.employee", string="Funcionario", copy=False)
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain', copy=False)
    contract_id = fields.Many2one('hr.contract', u'Contrato comisión', copy=False)
    contract_origen_id = fields.Many2one('hr.contract', u'Contrato origen', related='contract_id.cs_contract_id',
                                         store=True, copy=False)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso comisión', related='contract_id.inciso_id',
                                store=True)
    inciso_origen_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso',
        compute='_compute_inciso_ue_origen_id',
        copy=False, store=True)
    operating_unit_origen_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora origen",
        compute='_compute_inciso_ue_origen_id',
        copy=False,
        store=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        related='contract_id.operating_unit_id', store=True)
    program = fields.Char(string='Programa ', related='contract_origen_id.program')
    project = fields.Char(string='Proyecto ', related='contract_origen_id.project')
    regime_origin_id = fields.Many2one('onsc.legajo.regime', string='Régimen', related='contract_origen_id.regime_id')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1',
                                     related='contract_origen_id.descriptor1_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2',
                                     related='contract_origen_id.descriptor2_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3',
                                     related='contract_origen_id.descriptor3_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4',
                                     related='contract_origen_id.descriptor4_id')
    end_date = fields.Date(
        string="Fecha hasta de la Comisión",
        required=True,
        copy=False)
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission",
                                               string="Motivo extinción de la comisión", copy=False)
    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'baja_cs_id',
                                                      string='Documentos adjuntos', copy=False)
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    show_contract = fields.Boolean('Show Contract', compute='_compute_contract_id_domain')
    state = fields.Selection(STATES, string='Estado', default='borrador', tracking=True, copy=False)
    gheId = fields.Char(string='Identificador de envió GHE')

    @api.depends('contract_id', 'contract_origen_id')
    def _compute_inciso_ue_origen_id(self):
        for rec in self:
            if rec.contract_id and rec.contract_origen_id:
                rec.inciso_origen_id = rec.contract_origen_id.inciso_id and rec.contract_origen_id.inciso_id.id
                rec.operating_unit_origen_id = rec.contract_origen_id.operating_unit_id and rec.contract_origen_id.operating_unit_id.id
            else:
                rec.inciso_origen_id = rec.contract_id.inciso_origin_id.id
                rec.operating_unit_origen_id = rec.contract_id.operating_unit_origin_id.id

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            if self.user_has_groups('onsc_legajo.group_legajo_baja_cs_consulta_bajas') \
                    and not self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_inciso') \
                    and not self.user_has_groups('onsc_legajo.group_legajo_baja_cs_recursos_humanos_ue') \
                    and not self.user_has_groups('onsc_legajo.group_legajo_baja_cs_administrar_bajas'):
                record.should_disable_form_edit = True
            else:
                record.should_disable_form_edit = record.state not in ['borrador', 'error_sgh']

    @api.depends('cv_emissor_country_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()

    @api.depends('employee_id')
    def _compute_contract_id_domain(self):
        for rec in self:
            if rec.employee_id:
                contracts = rec._get_employee_contracts()
                rec.show_contract = len(contracts) > 1
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
            else:
                rec.show_contract = False
                rec.contract_id_domain = json.dumps([('id', 'in', [])])

    @api.constrains("end_date")
    def _check_date(self):
        for record in self:
            if record.end_date > fields.Date.today():
                raise ValidationError(_("La Fecha hasta de  la Comisión debe ser menor o igual  al día de baja"))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            contracts = self._get_employee_contracts()
            if contracts:
                self.contract_id = contracts[0].id
            else:
                self.contract_id = False
        else:
            self.contract_id = False

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super(ONSCLegajoBajaCS, self).unlink()

    def action_call_ws11(self):
        self._check_required_fieds_ws11()
        self._message_log(body=_('Envia a SGH'))
        if self.state != 'communication_error':
            self.write({'gheId': self.env["ir.sequence"].next_by_code("onsc.legajo.ghe.id")})
        self.env['onsc.legajo.abstract.baja.vl.ws11'].suspend_security().syncronize(self)

    def action_update_contract(self):
        data = {
            'reason_deregistration': self.reason_description or False,
            'norm_code_deregistration_id': self.norm_id and self.norm_id.id or False,
            'type_norm_deregistration': self.norm_type or False,
            'norm_number_deregistration': self.norm_number or False,
            'norm_year_deregistration': self.norm_year or False,
            'norm_article_deregistration': self.norm_article or False,
            'resolution_description_deregistration': self.resolution_description or False,
            'resolution_date_deregistration': self.resolution_date or False,
            'resolution_type_deregistration': self.resolution_type or False,
            'additional_information_deregistration': self.additional_information,
            'extinction_commission_id': self.extinction_commission_id and self.extinction_commission_id.id or False
        }

        for attach in self.attached_document_discharge_ids:
            attach.write({
                'contract_id': self.contract_id.id,
                'type': 'deregistration'
            })
        self.contract_id.suspend_security().write(data)
        return True

    def action_actualizar_puesto(self):
        contrato_origen = self.contract_origen_id
        if self.inciso_id.is_central_administration and contrato_origen.inciso_id.is_central_administration:
            contrato_origen.suspend_security().activate_legajo_contract(
                eff_date=fields.Date.today(),
                clean_destination_info=True
            )
            self.contract_id.suspend_security().deactivate_legajo_contract(self.end_date, eff_date=fields.Date.today())
        elif not self.contract_id.inciso_id.is_central_administration and self.contract_id.legajo_state == 'incoming_commission':
            self.contract_id.suspend_security().deactivate_legajo_contract(self.end_date, eff_date=fields.Date.today())
            self.contract_id.cs_contract_id.suspend_security().activate_legajo_contract(
                eff_date=fields.Date.today(),
                clean_destination_info=True
            )
        elif self.contract_id.inciso_id.is_central_administration and self.contract_id.legajo_state == 'incoming_commission' \
                and not contrato_origen:
            self.contract_id.suspend_security().job_ids.filtered(lambda x: x.end_date is False).write(
                {'end_date': self.end_date})
            self.contract_id.suspend_security().deactivate_legajo_contract(self.end_date, eff_date=fields.Date.today())
        self.action_update_contract()
        self.write({'state': 'confirmado', 'is_error_synchronization': False, 'error_message_synchronization': '', })
        return True

    def button_open_contract(self):
        self.ensure_one()
        if self.contract_id:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_hr_contract_action')
            action.update({'res_id': self.contract_id.id})
            return action
        else:
            return True

    def _get_employee_contracts(self):
        Contract = self.env['hr.contract']
        args = self._get_domain_contract([], self.employee_id.id)
        return Contract.search(args)

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

            if record.contract_id and record.contract_id.legajo_state != 'incoming_commission':
                message.append(_("El contrato debe estar en comision entrante "))

            if record.contract_id and record.employee_id and record.employee_id.cv_nro_doc != record.contract_id.nro_doc:
                message.append(_(u"El funcionario de la baja de comisión deber ser el mismo del  contrato"))

            if not record.attached_document_discharge_ids:
                message.append(_("Debe haber al menos un documento adjunto"))

            if message:
                fields_str = '\n'.join(message)
                message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
                raise ValidationError(_(message))
        return True
