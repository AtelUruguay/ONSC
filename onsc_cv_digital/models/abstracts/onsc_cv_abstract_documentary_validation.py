# -*- coding: utf-8 -*-
from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

DOCUMENTARY_VALIDATION_STATES = [('to_validate', 'Para validar'),
                                 ('validated', 'Validado'),
                                 ('rejected', 'Rechazado')]


class ONSCCVAbstractFileValidation(models.AbstractModel):
    _name = 'onsc.cv.abstract.documentary.validation'
    _inherit = 'onsc.cv.abstract.common'
    _description = 'Modelo abstracto de validación documental'

    documentary_validation_state = fields.Selection(string="Estado de validación documental",
                                                    selection=DOCUMENTARY_VALIDATION_STATES,
                                                    default='to_validate',
                                                    tracking=True)
    documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental', tracking=True)
    documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    documentary_user_id = fields.Many2one(comodel_name="res.users", string="Usuario validación documental",
                                          tracking=True)

    @property
    def field_documentary_validation_state(self):
        return etree.XML("""<field name="documentary_validation_state" invisible="0"/>""")

    @property
    def widget_call_documentary_button(self):
        return etree.XML(_("""
            <div>
                <field name="documentary_validation_state" invisible="1"/>
                <button name="button_documentary_approve"
                    groups="onsc_cv_digital.group_validador_documental_cv"
                    type="object" string="Validar" icon="fa-thumbs-o-up" class="btn btn-sm btn-outline-info"/>
                <button name="button_documentary_reject"
                    groups="onsc_cv_digital.group_validador_documental_cv"
                    type="object" string="Rechazar" icon="fa-thumbs-o-down" class="btn btn-sm btn-outline-danger"/>
                <div class="alert alert-danger" role="alert"
                    attrs="{'invisible': [('documentary_validation_state', '!=', 'rejected')]}">
                    <p class="mb-0">
                        <strong>
                            Ha sido rechazado. Motivo del rechazo: <field name="documentary_reject_reason" class="oe_inline"/>
                            <p/>
                            Fecha: <field name="documentary_validation_date" class="oe_inline"/> Usuario: <field name="documentary_user_id" class="oe_inline" options="{'no_open': True, 'no_quick_create': True, 'no_create': True}"/>
                        </strong>
                    </p>
                </div>
                <div class="alert alert-success" role="alert"
                    attrs="{'invisible': [('documentary_validation_state', '!=', 'validated')]}">
                    <p class="mb-0">
                        <strong>
                            El registro ha sido validado
                            <p/>
                            Fecha: <field name="documentary_validation_date" class="oe_inline"/> Usuario: <field name="documentary_user_id" class="oe_inline" options="{'no_open': True, 'no_quick_create': True, 'no_create': True}"/>
                        </strong>
                    </p>
                </div>
            </div>"""))

    @property
    def widget_documentary_button(self):
        return etree.XML(_("""
                <div>
                    <field name="documentary_validation_state" invisible="1"/>
                    <div class="alert alert-danger" role="alert"
                        attrs="{'invisible': [('documentary_validation_state', '!=', 'rejected')]}">
                        <p class="mb-0">
                            <strong>
                                Ha sido rechazado. Motivo del rechazo: <field name="documentary_reject_reason" class="oe_inline"/>
                                <p/>
                                Fecha: <field name="documentary_validation_date" class="oe_inline"/> Usuario: <field name="documentary_user_id" class="oe_inline" options="{'no_open': True, 'no_quick_create': True, 'no_create': True}"/>
                            </strong>
                        </p>
                    </div>
                </div>"""))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Add in form view divs with info status off documentary validation """
        res = super(ONSCCVAbstractFileValidation, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            field_ids = self.env["onsc.cv.documentary.validation.config"].search(
                [('model_id.model', '=', self._name)]).mapped('field_ids')
            if self._context.get('is_call_documentary_validation', False):
                for field in field_ids:
                    node = doc.xpath("//field[@name='" + field.name + "']")
                    for n in node:
                        n.set('doc-validation', 'label-text-danger')
                res['arch'] = etree.tostring(doc, encoding='unicode')
                widget = self.widget_call_documentary_button
            else:
                widget = self.widget_documentary_button
            if len(field_ids):
                for node in doc.xpath('//sheet'):
                    node.insert(0, widget)
                xarch, xfields = self.env['ir.ui.view'].postprocess_and_fields(doc, model=self._name)
                res['arch'] = xarch
                res['fields'] = xfields
        return res

    def write(self, vals):
        if not vals.get('documentary_validation_state', False):
            vals['documentary_validation_state'] = 'to_validate'
        return super(ONSCCVAbstractFileValidation, self).write(vals)

    def unlink(self):
        if self._check_todisable():
            return super(ONSCCVAbstractFileValidation, self).unlink()

    def button_documentary_approve(self):
        args = {
            'documentary_validation_state': 'validated',
            'documentary_reject_reason': '',
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        }
        self.write(args)
        self.search([('id', 'in', self.mapped('original_instance_identifier'))]).write(args)
        self._update_call_documentary_validation_status()

    def button_documentary_reject(self):
        ctx = self._context.copy()
        ctx.update({
            'default_model_name': self._name,
            'default_res_id': self.id,
            'is_documentary_reject': True
        })
        return {
            'name': _('Rechazo de %s' % self._description),
            'view_mode': 'form',
            'res_model': 'onsc.cv.reject.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def _update_call_documentary_validation_status(self):
        if self._fields.get('cv_digital_id'):
            calls = self.env['onsc.cv.digital.call'].search([('cv_digital_id', 'in', self.mapped('cv_digital_id').ids)])
            calls._compute_gral_info_documentary_validation_state()

    def _check_todisable(self):
        config = self.env['onsc.cv.documentary.validation.config']
        _name = self._name
        if not self._fields.get('cv_digital_id', False) or not config.search_count([('model_id.model', '=', _name)]):
            return True
        for record in self:
            if record.documentary_validation_state == 'validated' and record._check_todisable_dynamic_fields():
                raise ValidationError(
                    _(u"No es posible eliminar el registro porque está en estado de validación documental: 'Validado' "
                      u"y tiene o tuvo vínculo con el estado"))
        return True

    def _check_todisable_dynamic_fields(self):
        return self.cv_digital_id._is_rve_link()
