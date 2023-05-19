# -*- coding:utf-8 -*-
import json
from lxml import etree
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
]


class ONSCEmploymentRelationship(models.Model):
    _name = 'onsc.legajo.employment.relationship'
    _description = 'Vínculo laboral'

    selected = fields.Boolean(string="Seleccionado", help="Active para seleccionar Vinculo")
    programa = fields.Char(string='Programa', copy=False)
    proyecto = fields.Char(string='Proyecto', copy=False)
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor 1', copy=False)
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor 2', copy=False)
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor 3', copy=False)
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor 4', copy=False)
    nroPuesto = fields.Char(string='Puesto', copy=False)
    nroPlaza = fields.Char(string='Plaza', copy=False)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)
    baja_vl_id = fields.Many2one("onsc.legajo.baja.vl", string="Baja de vínculo laboral", copy=False)
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', copy=False)
    state = fields.Selection(related='baja_vl_id.state', string='Estado', readonly=True)


class ONSCLegajoBajaVL(models.Model):
    _name = 'onsc.legajo.baja.vl'
    _inherit = ['onsc.legajo.actions.common.data', 'onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin']
    _description = 'Baja de vínculo laboral'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajoBajaVL, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                            submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_alta_vl = self.env.user.has_group('onsc_legajo.group_legajo_baja_vl_consulta_bajas_vl')
        is_user_administrar_altas_vl = self.env.user.has_group('onsc_legajo.group_legajo_baja_vl_administrar_bajas')
        if view_type in ['form', 'tree', 'kanban'] and is_user_alta_vl and not is_user_administrar_altas_vl:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
            for node_form in doc.xpath("//button[@name='action_call_ws1']"):
                node_form.getparent().remove(node_form)
        res['arch'] = etree.tostring(doc)
        return res

    end_date = fields.Date(string="Fecha de Baja", default=fields.Date.today(), required=True, copy=False)

    causes_discharge_id = fields.Many2one('onsc.legajo.causes.discharge', string='Causal de Egreso', copy=False)
    causes_discharge_line_ids = fields.One2many('onsc.legajo.causes.discharge.line',
                                                related='causes_discharge_id.causes_discharge_line_ids',
                                                string="Motivos de causal de egreso extendido")
    employment_relationship_ids = fields.One2many('onsc.legajo.employment.relationship','baja_vl_id',
                                                  string="Vínculo laboral",compute="_compute_employment_relationship_ids",store=True)
    attached_document_discharge_ids = fields.One2many('onsc.legajo.alta.vl.attached.document', 'baja_vl_id',
                                                      string='Documentos adjuntos')
    integration_error_id = fields.Many2one('onsc.legajo.integration.error', string=u'Error reportado integración',
                                           copy=False)
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    id_baja = fields.Char(string="Id Baja")
    is_require_extended = fields.Boolean("¿Requiere extendido?", compute="_compute_is_require_extended")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)
    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    partner_id = fields.Many2one("res.partner", string="Contacto")
    partner_id_domain = fields.Char(string="Dominio Cliente", compute='_compute_partner_id_domain')

    @api.depends('cv_emissor_country_id')
    def _compute_partner_id_domain(self):
        for rec in self:
            rec.partner_id_domain = self._get_domain_partner_ids()

    @api.depends('causes_discharge_id')
    def _compute_is_require_extended(self):
        for rec in self:
            if rec.causes_discharge_id:
                rec.is_require_extended = rec.causes_discharge_id.is_require_extended
            else:
                rec.is_require_extended = False

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoBajaVL, self).default_get(fields)
        res['cv_emissor_country_id'] = self.env.ref('base.uy').id
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                                     limit=1).id or False
        if self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_inciso') or self.user_has_groups(
                'onsc_legajo.group_legajo_baja_vl_recursos_humanos_ue'):
            res['inciso_id'] = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        if self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_ue'):
            res['operating_unit_id'] = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        return res

    def _get_domain_partner_ids(self):
        contract_id = self.env['hr.contract'].search(
            [('legajo_state', '=', 'active'), ('employee_id', '=', self.env.user.employee_id.id)])
        if contract_id:
            iniciso_id = contract_id.inciso_id.id
            operating_unit_id = contract_id.operating_unit_id.id
            partner_ids = self.env['hr.contract'].search([('legajo_state', '=', 'active'),
                                                          ('inciso_id', '=', iniciso_id),
                                                          ('operating_unit_id', '=', operating_unit_id),
                                                          ('employee_id', '!=',
                                                           self.env.user.employee_id.id)]).mapped(
                'employee_id.user_id.partner_id').filtered(lambda x: x.is_partner_cv)
            return json.dumps([('id', 'in', partner_ids.ids)])
        else:
            return json.dumps([('id', '=', False)])

    @api.constrains("end_date")
    def _check_date(self):
        for record in self:
            if record.end_date > fields.Date.today():
                raise ValidationError(_("La fecha baja debe ser menor o igual a la fecha de registro"))

    @api.constrains("attached_document_discharge_ids")
    def _check_attached_document_discharge(self):
        for record in self:
            if not record.attached_document_discharge_ids:
                raise ValidationError(_("Debe haber al menos un documento adjunto"))





    @api.depends( "partner_id")
    def _compute_employment_relationship_ids(self):
        for rec in self:
            employee_id = self.env['hr.employee'].sudo().search(
                [('cv_emissor_country_id', '=', rec.cv_emissor_country_id.id),
                 ('cv_document_type_id', '=', rec.cv_document_type_id.id),
                 ('cv_nro_doc', '=', rec.partner_id.cv_nro_doc)])

            contract_ids = self.env['hr.contract'].sudo().search([('employee_id', '=', employee_id.id)])
            vinculo_ids = [(5,)]

            for contract in contract_ids:
                data = {
                    'nroPuesto': contract.position,
                    'nroPlaza': contract.workplace,
                    'descriptor1_id': contract.descriptor1_id and contract.descriptor1_id.id or False,
                    'descriptor2_id': contract.descriptor2_id and contract.descriptor2_id.id or False,
                    'descriptor3_id': contract.descriptor3_id and contract.descriptor3_id.id or False,
                    'descriptor4_id': contract.descriptor4_id and contract.descriptor4_id.id or False,
                    'inciso_id': contract.inciso_id and contract.inciso_id.id or False,
                    'operating_unit_id': contract.operating_unit_id and contract.operating_unit_id.id or False,
                    'programa': contract.program,
                    'proyecto': contract.project,
                    'regime_id': contract.regime_id and contract.regime_id.id or False,
                }

                vinculo_ids.append((0, 0, data))
            rec.employment_relationship_ids = vinculo_ids

