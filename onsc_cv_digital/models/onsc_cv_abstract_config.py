# -*- coding: utf-8 -*-

from lxml import etree

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

STATES = [('to_validate', 'Para validar'),
          ('validated', 'Validado'),
          ('rejected', 'Rechazado')]


class ONSCCVAbstractConfig(models.Model):
    _name = 'onsc.cv.abstract.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Modelo abstracto de catálogos'

    active = fields.Boolean(string='Activo', default=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    code = fields.Char(string=u'Código', size=5, )
    state = fields.Selection(string="Estado",
                             selection=STATES,
                             tracking=True,
                             default=lambda self: self.user_has_groups(
                                 'onsc_cv_digital.group_gestor_catalogos_cv') and 'validated' or 'to_validate')
    reject_reason = fields.Char(string=u'Motivo de rechazo', tracking=True)
    create_uid = fields.Many2one('res.users', index=True, tracking=True)
    can_edit = fields.Boolean(compute='_calc_can_edit')

    @api.depends('state')
    def _calc_can_edit(self):
        for rec in self:
            rec.can_edit = rec._check_can_write()

    def get_description_model(self):
        return self._description

    # def check_access_rule_all(self, operations=None):
    #     res = super(ONSCCVAbstractConfig, self).check_access_rule_all(operations)
    #     if not self._check_can_write() and 'write' in res:
    #         res['write'] = False
    #     return res

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Sobreesctito para Agregar a los Catálogos condicionales un campo en la vista form
        can_edit, luego se modfica cada atributo para que pueda editar o no segun el valor de este campo
        """
        res = super(ONSCCVAbstractConfig, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            if len(doc.xpath("//field[@name='can_edit']")) == 0:
                # Si nunca se ha agregado el campo can_edit entonces se agrega en el formulario
                for node in doc.xpath("//field"):
                    node.set('attrs', "{'readonly': [('can_edit', '=', False)]}")
                if doc.tag == 'form':
                    doc.insert(0, etree.Element('field', attrib={
                        'name': 'can_edit',
                        'invisible': '1',
                    }))
                form_view = self.env['ir.ui.view'].sudo().search([
                    ('model', '=', self._name), ('type', '=', 'form')], limit=1)
                form_view.sudo().write({'arch': etree.tostring(doc)})
                # Llamamos al super nuevamente para que tome los cambios que hemos realizado
                return super(ONSCCVAbstractConfig, self).fields_view_get(view_id, view_type, toolbar, submenu)
        return res

    # CRUD methods
    def write(self, values):
        if not self._check_can_write():
            raise ValidationError(_("No puede mofificar un registro en estado validado."))
        return super(ONSCCVAbstractConfig, self).write(values)

    def action_reject(self):
        ctx = self._context.copy()
        ctx.update({'default_model_name': self._name,
                    'default_res_id': self.id})
        return {
            'name': _('Rechazo de %s' % self._description),
            'view_mode': 'form',
            'res_model': 'onsc.cv.reject.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def action_validate(self):
        for record in self:
            record._check_validate([])
        self.sudo()._send_validation_email()
        self.write({'state': 'validated'})

    def _send_validation_email(self):
        """
        Envía un correo electrónico de validación
        :return:
        """
        validation_email_template_id = self.env.ref('onsc_cv_digital.email_template_validated')
        model_id = self.env['ir.model']._get_id(self._name)
        validation_email_template_id.model_id = model_id
        self.with_context(force_send=True).message_post_with_template(
            validation_email_template_id.id, email_layout_xmlid='mail.mail_notification_light')

    def _send_reject_email(self):
        """
        Envía un correo electrónico de rechazo
        :return:
        """
        reject_email_template_id = self.env.ref('onsc_cv_digital.email_template_rejected')
        model_id = self.env['ir.model']._get_id(self._name)
        reject_email_template_id.model_id = model_id
        self.with_context(force_send=True).message_post_with_template(
            reject_email_template_id.id, email_layout_xmlid='mail.mail_notification_light')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        REGLA GENERAL PARA CATALOGOS CONFIGURABLES
        Mostrar solamente aquellos catalogos que esten validados o que fueron creados por el usuario si:
            -No estamos en el menu de gestion del catalogo
            -No es el superuser
            -No soy Validador de Catalogo. Este se incluye porque el validador deberia poder entrar a validarlo
            desde cualquier lugar
        """
        if not self._context.get('is_config') and self.env.uid != SUPERUSER_ID and not self.user_has_groups(
                'onsc_cv_digital.group_validador_catalogos_cv'):
            args += ['|', ('state', '=', 'validated'), ('create_uid', '=', self.env.uid)]
        return super(ONSCCVAbstractConfig, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                         access_rights_uid=access_rights_uid)

    def _check_validate(self, args2validate, message=""):
        """

        :param args2validate: Lista formato OdooWay para search_count
        :param message: Mensaje para mostrar al usuario en caso de no pasar la Validación
        :return: True si debe seguir con la validación, Mensaje de Validación(message) de lo contrario
        """
        if len(args2validate) == 0:
            return True
        args2validate.extend([('state', '=', 'validated'), ('id', '!=', self.id)])
        if self.search_count(args2validate):
            raise ValidationError(message)

    def _check_can_write(self):
        """Los usuarios CV solo pueden modificar si el estado no es validado"""
        return not (self.filtered(lambda x: x.state == 'validated') and self.user_has_groups(
            'onsc_cv_digital.group_user_cv'))
