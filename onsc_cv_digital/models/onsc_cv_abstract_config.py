# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID

STATES = [('to_validate', 'Para validar'),
          ('validated', 'Validado'),
          ('rejected', 'Rechazado')]


class ONSCCVAbstractConfig(models.Model):
    _name = 'onsc.cv.abstract.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Modelo abstracto de catálogos'

    active = fields.Boolean(string='Activo', default=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    code = fields.Char(string=u'Código', size=5)
    state = fields.Selection(string="Estado",
                             selection=STATES,
                             tracking=True,
                             default='validated')
    reject_reason = fields.Char(string=u'Motivo de rechazo', tracking=True)
    create_uid = fields.Many2one('res.users', index=True, tracking=True)

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
        self.sudo()._send_validation_email()
        self.write({'state': 'validated'})

    def _send_validation_email(self):
        """
        Primero busca si la plantilla de correo existe, sino la crea
        Envía un mail notificando el validación de un catálogo
        :return:
        """
        main_validation_email_template_id = self.env.ref('onsc_cv_digital.email_template_validated')
        model_id = self.env['ir.model']._get_id(self._name)

        onsc_mail_template_model_id = self.env['onsc.cv.mail.template.model'].search(
            [('model_id', '=', model_id)], limit=1)

        if not onsc_mail_template_model_id:
            onsc_mail_template_model_id = self.env['onsc.cv.mail.template.model'].create(
                {'model_id': model_id})
        validation_email_template_id = onsc_mail_template_model_id.validation_mail_template_id

        if not validation_email_template_id:
            validation_email_template_id = main_validation_email_template_id.copy(
                {'model_id': model_id,
                 'name': _('Plantilla para %s') % self._description,
                 'subject': _('Notificación de validación de %s') % self._description
                 },
            )
            onsc_mail_template_model_id.validation_mail_template_id = validation_email_template_id

        self.with_context(force_send=True).message_post_with_template(
            validation_email_template_id.id, email_layout_xmlid='mail.mail_notification_light')

    def _send_reject_email(self):
        """
        Primero busca si la plantilla de correo existe, sino la crea
        Envía un mail notificando el rechazo de un catálogo
        :return:
        """
        main_reject_email_template_id = self.env.ref('onsc_cv_digital.email_template_rejected')
        model_id = self.env['ir.model']._get_id(self._name)

        onsc_mail_template_model_id = self.env['onsc.cv.mail.template.model'].search(
            [('model_id', '=', model_id)], limit=1)

        if not onsc_mail_template_model_id:
            onsc_mail_template_model_id = self.env['onsc.cv.mail.template.model'].create(
                {'model_id': model_id})
        reject_mail_template_id = onsc_mail_template_model_id.reject_mail_template_id

        if not reject_mail_template_id:
            reject_mail_template_id = main_reject_email_template_id.copy(
                {'model_id': model_id,
                 'name': _('Plantilla para %s') % self._description,
                 'subject': _('Notificación de rechazo de %s') % self._description
                 },
            )
            onsc_mail_template_model_id.reject_mail_template_id = reject_mail_template_id

        self.with_context(force_send=True).message_post_with_template(
            reject_mail_template_id.id, email_layout_xmlid='mail.mail_notification_light')

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


class MailTemplateModel(models.Model):
    _name = 'onsc.cv.mail.template.model'
    _description = 'Plantilla de correo por modelo'

    model_id = fields.Many2one('ir.model', 'Modelo')
    validation_mail_template_id = fields.Many2one('mail.template', 'Plantilla de correo de validación')
    reject_mail_template_id = fields.Many2one('mail.template', 'Plantilla de correo de rechazo')
