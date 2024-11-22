# -*- coding: utf-8 -*-

from lxml import etree

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

STATES = [('to_validate', 'Para validar'),
          ('validated', 'Validado'),
          ('rejected', 'Rechazado')]


# Define Constraints of unicity and the logic to validate models
# _fields_2check_unicity: list of fields to check unicity
# _get_conditional_unicity_message: return message when unicity control is unsuccessful

class ONSCCVAbstractNameUpper(models.AbstractModel):
    _name = 'onsc.cv.abstract.name.upper'

    # Field name must be inherited by all new models. Its here for clear code
    name = fields.Char(string="Nombre")
    name_upper = fields.Char(string="Nombre(Mayúsculas)", compute='_compute_name_upper', store=True)

    @api.constrains('name_upper')
    def _check_name_upper(self):
        _name_string = self._fields.get('name', ) and self._fields.get('name', ).string or 'Nombre'
        for rec in self:
            if self.search_count([('name_upper', '=', rec.name_upper), ('id', '!=', rec.id)]):
                raise ValidationError(_("El %s debe ser único") % _name_string)

    @api.depends('name')
    def _compute_name_upper(self):
        for rec in self:
            rec.name_upper = rec.name.upper()


class ONSCCVAbstractConfig(models.AbstractModel):
    _name = 'onsc.cv.abstract.config'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'onsc.cv.abstract.name.upper']
    _description = 'Modelo abstracto de catálogos condicionales'
    _fields_2check_unicity = ['name', 'state']

    def _default_state(self):
        if self.user_has_groups('onsc_cv_digital.group_gestor_catalogos_cv') and self._context.get('is_config'):
            return 'validated'
        else:
            return 'to_validate'

    active = fields.Boolean(string='Activo', default=True, tracking=True)
    company_id = fields.Many2one('res.company',string="Empresa", required=True, default=lambda self: self.env.company)
    code = fields.Char(string=u'Código', size=5)
    state = fields.Selection(string="Estado",
                             selection=STATES,
                             tracking=True,
                             copy=True,
                             default=_default_state)
    reject_reason = fields.Text(string=u'Motivo de rechazo', tracking=True)
    create_uid = fields.Many2one('res.users',string="Creado por", index=True, tracking=True)

    @api.constrains(lambda self: ['%s' % x for x in self._fields_2check_unicity])
    def _check_conditional_unicity(self):
        """
        Constrains generico de evaluacion de unicidad de catalogos condicionales
        :return:
        """
        if len(self._fields_2check_unicity) == 0:
            return True
        for record in self.filtered(lambda x: x.state == 'validated'):
            record._check_parent_validation_state()
            args2validate = [('id', '!=', record.id)]
            for _field_2check_unicity in self._fields_2check_unicity:
                field_value = eval('record.%s' % _field_2check_unicity)
                if hasattr(field_value, 'id'):
                    field_value = field_value.id
                args2validate.append((_field_2check_unicity, '=', field_value))
            if self.search_count(args2validate):
                raise ValidationError(record._get_conditional_unicity_message())

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s" % (self.name))

    def _check_parent_validation_state(self):
        return True

    def get_description_model(self):
        return self._description

    def get_formview_id(self, access_uid=None):
        """ Sobreescrito para no permitir editar en los modelos relacionados
        Crea una vista form con campos readonly la primera vez y luego es llamada para los usuarios que no tienen
        permiso de escribir"""
        if access_uid:
            self_sudo = self.with_user(access_uid)
        else:
            self_sudo = self

        if self_sudo._check_can_write():
            return super(ONSCCVAbstractConfig, self).get_formview_id(access_uid=access_uid)
        # Hardcode the form view for public employee
        self = self.sudo()
        form_id = self.env['ir.ui.view'].search([('name', '=', '%s.form.readonly' % self._name)], limit=1)
        if not form_id:
            form_parent_id = self.env['ir.ui.view'].search([('model', '=', self._name), ('type', '=', 'form')], limit=1)
            if form_parent_id:
                arch = form_parent_id.arch
                doc = etree.XML(arch)
                for node in doc.xpath("//field"):
                    node.set("readonly", "1")
                form_id = self.env['ir.ui.view'].create(
                    {'name': '%s.form.readonly' % self._name,
                     "model": self._name,
                     "priority": 100,
                     'arch': etree.tostring(doc, encoding='unicode')
                     })

        return form_id.id

    # CRUD methods
    @api.model
    def create(self, values):
        result = super(ONSCCVAbstractConfig, self).create(values)
        if values.get('state') == 'validated':
            result._check_validation_status()
        return result

    def write(self, values):
        check_write_is_needed = len(values) > 1 or (len(values) == 1 and list(values.keys())[0] != 'active')
        if check_write_is_needed and self.filtered(lambda x: not x._check_can_write()):
            raise ValidationError(_("No puede modificar un registro en estado validado o rechazado."))
        result = super(ONSCCVAbstractConfig, self).write(values)
        if values.get('state') == 'validated':
            self._check_validation_status()
        return result

    def action_reject(self):
        ctx = self._context.copy()
        ctx.update({'default_model_name': self._name,
                    'default_res_id': self.id,
                    'default_is_multi': False})
        return {
            'name': _('Rechazo de %s' % self._description),
            'view_mode': 'form',
            'res_model': 'onsc.cv.reject.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def action_reject_multi(self):
        ctx = self._context.copy()
        ctx.update({'default_model_name': self._name,
                    'active_ids': self.ids,
                    'default_is_multi': True})

        if self.filtered(lambda x: x.state not in ['to_validate']):
            raise ValidationError(_("Solo se pueden rechazar registros en estado Para validar"))
        if ctx.get('tree_view_ref'):
            ctx.pop('tree_view_ref')
        if ctx.get('form_view_ref'):
            ctx.pop('form_view_ref')
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
        self._check_validation_status()
        self.write({'state': 'validated'})
        self.sudo()._send_validation_email()

    def _send_validation_email(self):
        """
        Envía un correo electrónico de validación
        :return:
        """
        validation_email_template_id = self.env.ref('onsc_cv_digital.email_template_validated')
        model_id = self.env['ir.model']._get_id(self._name)
        validation_email_template_id.model_id = model_id
        return validation_email_template_id.send_mail(self.id, force_send=True,
                                                      notif_layout='mail.mail_notification_light')

    def _send_reject_email(self):
        """
        Envía un correo electrónico de rechazo
        :return:
        """
        reject_email_template_id = self.env.ref('onsc_cv_digital.email_template_rejected')
        model_id = self.env['ir.model']._get_id(self._name)
        reject_email_template_id.model_id = model_id
        return reject_email_template_id.send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')

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
            args += ['|', ('state', '=', 'validated'), '&',
                     ('create_uid', '=', self.env.uid), ('state', '!=', 'rejected')]
        return super(ONSCCVAbstractConfig, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                         access_rights_uid=access_rights_uid)

    def _check_can_write(self):
        """Solo pueden modificar si el estado no es validado o recahazado"""
        return not self.filtered(lambda x: x.state in ['validated', 'rejected'])

    def _check_validation_status(self):
        return True
