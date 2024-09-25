# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning
from odoo.exceptions import ValidationError


class ONSCCatalogOccupation(models.Model):
    _name = 'onsc.catalog.occupation'
    _description = 'Ocupación'
    _inherit = ['onsc.catalog.abstract.base', 'model.history', 'mail.thread', 'mail.activity.mixin',
                'onsc.catalog.abstract.approval']
    _history_model = 'onsc.catalog.occupation.history'

    occupational_family_id = fields.Many2one("onsc.catalog.occupational.family", string="Familia",
                                             required=True, history=True, ondelete='restrict')
    management_process_id = fields.Many2one("onsc.catalog.management.process", string="Proceso",
                                            required=True, history=True, ondelete='restrict')
    purpose = fields.Char(string=u"Propósito")
    activities = fields.Char(string=u"Actividades")

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime('Fecha de última modificación', index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    @api.constrains('start_date', 'end_date', 'occupational_family_id.end_date', 'management_process_id.end_date',
                    'occupational_family_id.start_date', 'management_process_id.start_date')
    def _check_validity(self):
        _message = _("La vigencia de la ocupación debe estar contenida dentro de la vigencia del proceso y la familia")
        for record in self:
            sdate = record.start_date
            edate = record.end_date
            family_edate = record.occupational_family_id.end_date
            process_edate = record.management_process_id.end_date
            if sdate < record.occupational_family_id.start_date or (
                    family_edate and sdate > family_edate) or sdate < record.management_process_id.start_date or (
                    process_edate and sdate > process_edate):
                raise ValidationError(_message)
            if edate and ((family_edate and edate > family_edate) or (process_edate and edate > process_edate)):
                raise ValidationError(_message)

    def _action_open_view(self):
        vals = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': self._name,
            'name': 'Ocupaciones',
            'search_view_id': [self.env.ref('onsc_catalog.onsc_catalog_occupation_search').id, 'search'],
            'views': [
                [self.env.ref('onsc_catalog.onsc_catalog_occupation_tree').id, 'tree'],
                [self.env.ref('onsc_catalog.onsc_catalog_occupation_form').id, 'form'],
            ]
        }
        _context = dict(self._context, default_active=False)
        if not self.env.user.has_group('onsc_catalog.group_catalog_configurador_servicio_civil'):
            if self.env.user.has_group('onsc_catalog.group_catalog_aprobador_cgn'):
                vals['context'] = dict(_context, search_default_filter_inactive_cgn=1,
                                       create=False,
                                       delete=False,
                                       edit=False)
            else:
                vals['context'] = dict(_context,
                                       create=False,
                                       delete=False,
                                       edit=False)
        else:
            vals['context'] = _context
        return vals

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return catalog_warning(_(u"La fecha de inicio de vigencia no puede ser mayor "
                                     u"que la fecha de fin de vigencia"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return catalog_warning(_(u"La fecha de fin de vigencia no puede ser menor "
                                     u"que la fecha de inicio de vigencia"))

    def unlink(self):
        if self.filtered(lambda x: x.is_approve_cgn):
            raise ValidationError(_("No se puede eliminar una Ocupación luego de ser aprobada por CGN"))
        return super(ONSCCatalogOccupation, self).unlink()

    def toggle_active(self):
        self._check_toggle_active()
        return super(ONSCCatalogOccupation, self.with_context(
            no_check_write=True,
            no_check_active=True)).toggle_active()

    def _check_toggle_active(self):
        if False in self.mapped('is_approve_cgn'):
            raise ValidationError(
                _("No puede archivar o desarchivar una %s si no está Aprobada CGN!") % self._description)
        return True


class ONSCCatalogOccupationHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.catalog.occupation.history'
    _parent_model = 'onsc.catalog.occupation'
