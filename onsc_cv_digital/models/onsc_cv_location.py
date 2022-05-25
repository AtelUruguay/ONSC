# -*- coding: utf-8 -*-

from odoo import fields, models, api

from odoo import SUPERUSER_ID


class ONSCCVLocation(models.Model):
    _name = 'onsc.cv.location'
    _description = 'Ciudad/Localidad'
    _order = 'state_id, name'

    name = fields.Char(string='Nombre de Localidad', size=40, required=True, index=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True)
    state_id = fields.Many2one('res.country.state', string='Departamento', ondelete='restrict', required=True,
                               domain="[('country_id','=',country_id)]")
    code = fields.Char(string=u'Código', size=5)
    active = fields.Boolean(string='Activo', default=True)
    other_code = fields.Integer(string=u'Otro código')

    state = fields.Selection(string="Estado",
                             selection=[('to_validate', 'Para validar'),
                                        ('validated', 'Validado'),
                                        ('rejected', 'Rechazado')],
                             default='validated')
    reject_reason = fields.Char(string=u'Motivo de rechazo')
    create_uid = fields.Many2one('res.users', index=True)

    _sql_constraints = [
        ('localidad_name_by_state_unique', 'unique(name, state_id)',
         'Ya existe una Localidad con ese nombre en el mismo Departamento'), ]

    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.state_id = False

    @api.model
    def create(self, values):
        values['name'] = values.get('name', '').upper()
        return super(ONSCCVLocation, self).create(values)

    def write(self, values):
        if values.get('name', False):
            values['name'] = values.get('name', '').upper()
        return super(ONSCCVLocation, self).write(values)

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
        if not self._context.get('is_config') and self.env.uid != SUPERUSER_ID and not self.env.user_has_groups(
                'onsc_cv_digital.group_validador_catalogos_cv'):
            args += ['|', ('state', '=', 'validated'), ('create_uid', '=', self.env.uid)]
        return super(ONSCCVLocation, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                   access_rights_uid=access_rights_uid)

    def action_validate(self):
        self.write({'state': 'validated'})

    def action_reject(self):
        return self.env["ir.actions.actions"]._for_xml_id("onsc_cv_digital.onsc_cv_location_reject_wizard_action")
