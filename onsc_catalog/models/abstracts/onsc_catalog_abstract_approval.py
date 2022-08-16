# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCatalogAbstractApproval(models.AbstractModel):
    _name = 'onsc.catalog.abstract.approval'
    _description = 'Modelo abstracto de aprobación de catálogo'

    is_approve_onsc = fields.Boolean(string="Aprobado ONSC", copy=False, tracking=True)
    approve_onsc_date = fields.Date(string=u"Fecha aprobación ONSC", copy=False, )
    is_approve_cgn = fields.Boolean(string="Aprobado CGN", copy=False, tracking=True, )
    approve_cgn_date = fields.Date(string=u"Fecha aprobación CGN", copy=False)

    @api.onchange('is_approve_onsc')
    def onchange_is_approve_onsc(self):
        if self.is_approve_onsc:
            self.approve_onsc_date = fields.Date.today()
        else:
            self.approve_onsc_date = False

    @api.onchange('is_approve_cgn')
    def onchange_is_approve_cgn(self):
        if self.is_approve_cgn:
            self.approve_cgn_date = fields.Date.today()
        else:
            self.approve_cgn_date = False

    def write(self, vals):
        self._check_user_can_write()
        return super(ONSCCatalogAbstractApproval, self).write(vals)

    def action_aprobar_cgn(self):
        return self.suspend_security().with_context(no_check_write=True).write({
            'is_approve_cgn': True,
            'approve_cgn_date': fields.Date.today(),
            'active': True
        })

    def action_aprobar_onsc(self):
        return self.with_context(no_check_write=True).write({
            'is_approve_onsc': True,
            'approve_onsc_date': fields.Date.today()
        })

    def _check_toggle_active(self):
        if False in self.mapped('is_approve_cgn'):
            raise ValidationError(
                _("No puede archivar o desarchivar una %s si no está Aprobada CGN!") % self._description)
        return True

    def _check_user_can_write(self):
        is_cgn = self.user_has_groups("onsc_catalog.group_catalog_aprobador_cgn")
        is_not_configurador = self.user_has_groups("onsc_catalog.group_catalog_configurador_servicio_civil") is False
        if self.env.context.get('no_check_write', False) is False and is_cgn and is_not_configurador:
            raise ValidationError(_("No puede editar información de la Unidad organizativa. "
                                    "La única operación permitida es Aprobar CGN"))
        if self.env.context.get('no_check_write', False) is False and self.user_has_groups(
                "onsc_catalog.group_catalog_configurador_servicio_civil"):
            for record in self:
                condition1 = (record.is_approve_cgn is True and record.is_approve_onsc is False)
                condition2 = (record.is_approve_cgn is False and record.is_approve_onsc is True)
                if condition1 or condition2:
                    raise ValidationError(_("Solo puede editar si la aprobación ONSC y CGN "
                                            "están ambas marcadas o desmarcadas"))
