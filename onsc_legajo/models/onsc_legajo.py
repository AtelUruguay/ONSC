# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError


class ONSCLegajo(models.Model):
    _name = "onsc.legajo"
    _inherit = "onsc.legajo.abstract.legajo.security"
    _rec_name = "employee_id"
    _order = "employee_id"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree', 'kanban'] and not self.env.user.has_group(
                'onsc_legajo.group_legajo_configurador'):
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Funcionario",
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

    image_1920 = fields.Image(string='Foto', max_width=1920, max_height=1920,
                              related='employee_id.image_1920', store=True)
    avatar_128 = fields.Image(string='Avatar 128', max_width=128, max_height=128,
                              related='employee_id.avatar_128', store=True)

    public_admin_entry_date = fields.Date(string=u'Fecha de ingreso a la administración pública')
    public_admin_inactivity_years_qty = fields.Integer(string=u'Años de inactividad')

    contract_ids = fields.One2many('hr.contract', compute='_compute_contract_info')
    contracts_count = fields.Integer(string='Cantidad de contratos', compute='_compute_contract_info')

    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado del funcionario',
        related='employee_id.legajo_state',
        store=True
    )

    job_ids = fields.One2many(
        comodel_name='hr.job',
        inverse_name='legajo_id',
        string='Puestos')

    def _compute_contract_info(self):
        for record in self:
            available_contracts = record._get_user_available_contract(record.employee_id)
            record.contract_ids = available_contracts
            record.contracts_count = len(available_contracts)

    def button_open_contract(self):
        self.ensure_one()
        if self.contracts_count == 0:
            return True
        elif self.contracts_count == 1:
            action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_hr_contract_action')
            action.update({
                'res_id': self.contract_ids[0].id
            })
        else:
            action = self.env["ir.actions.actions"]._for_xml_id(
                'onsc_legajo.onsc_legajo_hr_contract_list_readonly_action')
            _context = self._context.copy()
            _context.update({
                'create': False,
                'edit': False,
                'is_legajo': True,
                'filter_contracts': True,
                'from_smart_button': True
            })
            action.update({
                'context': str(_context),
                'domain': [('id', 'in', self.contract_ids.ids)]
            })
        return action

    def button_open_employee(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('onsc_legajo.onsc_legajo_one_employee_action')
        action['res_id'] = self.employee_id.id
        return action

    def button_rve_history(self):
        try:
            self.ensure_one()
            rve_document = self.env['onsc.legajo.abstract.ws.rve'].suspend_security().syncronize(self)
            attachment_name = _("Historial RVE Funcionario %s.pdf") % self.full_name
            attachment = self.env["ir.attachment"].create({
                "name": attachment_name,
                "datas": bytes(rve_document, 'utf-8'),
                "type": "binary",
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": self.id,
            })
            url = "{}/web/content/ir.attachment/{}/datas/{}".format(
                self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
                attachment.id,
                attachment.name,
            )
            return {
                "type": "ir.actions.act_url",
                "target": "new",
                "url": url,
            }
        except Exception as e:
            raise ValidationError(_("Error al obtener la Historia laboral. Detalle: %s" % tools.ustr(e)))

    def button_rve_history_test(self):
        try:
            self.ensure_one()
            rve_document = self.env['onsc.legajo.abstract.ws.rve'].with_context(
                test=True).suspend_security().syncronize(self)
            attachment_name = _("Historial RVE Funcionario %s.pdf") % self.full_name
            attachment = self.env["ir.attachment"].create({
                "name": attachment_name,
                "datas": bytes(rve_document, 'utf-8'),
                "type": "binary",
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": self.id,
            })
            url = "{}/web/content/ir.attachment/{}/datas/{}?download=true".format(
                self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
                attachment.id,
                attachment.name,
            )
            return {
                "type": "ir.actions.act_url",
                "target": "new",
                "url": url,
            }
        except Exception as e:
            raise ValidationError(_("Error al obtener la Historia laboral. Detalle: %s" % tools.ustr(e)))

    def _action_milegajo(self):
        ctx = self.env.context.copy()
        ctx['mi_legajo'] = True
        ctx['is_legajo'] = True
        mi_legajo = self.sudo().with_context(mi_legajo=True, is_legajo=True).search(
            [('employee_id', '=', self.env.user.employee_id.id)], limit=1).id
        if mi_legajo:
            view_mode = 'form'
        else:
            view_mode = 'kanban'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': self._name,
            'name': 'Mi legajo',
            'context': ctx,
            "target": "main",
            "res_id": mi_legajo,
        }

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_ue')

    # INTELIGENCIA DE ENTIDAD
    def _get_legajo(self, employee, entry_date=False, inactivity_years=False):
        """
        Si existe un legajo para ese Empleado lo devuelve sino lo crea
        :param employee: Recordset a hr.employee
        :param entry_date: Fecha de ingreso a la administracion publica
        :param inactivity_years: Cantidad de anios de inactividad
        :return: nuevo recordet de onsc.legajo
        """
        Legajo = self.suspend_security()
        legajo = Legajo.search([('employee_id', '=', employee.id)], limit=1)
        if not legajo:
            legajo = Legajo.create({
                'employee_id': employee.id,
                'public_admin_entry_date': entry_date,
                'public_admin_inactivity_years_qty': inactivity_years
            })
        return legajo
