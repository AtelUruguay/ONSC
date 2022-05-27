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
        self.write({'state': 'validated'})

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
