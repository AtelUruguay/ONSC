# -*- coding: utf-8 -*-
from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

DOCUMENTARY_VALIDATION_STATES = [('to_validate', 'Para validar'),
                                 ('validated', 'Validado'),
                                 ('rejected', 'Rechazado')]


class ONSCCVAbstractFileValidation(models.AbstractModel):
    _name = 'onsc.cv.abstract.documentary.validation'
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
    def widget_documentary_button(self):
        return etree.XML(_("""
            <div>
                <button name="button_documentary_approve" type="object" string="Aprobar" icon="fa-thumbs-o-up" class="oe_highlight"/>
                <button name="button_documentary_reject" type="object" string="Rechazar" icon="fa-thumbs-o-down"/>
                <div class="alert alert-danger" role="alert"
                    attrs="{'invisible': [('documentary_validation_state', '!=', 'rejected')]}">
                    <p class="mb-0">
                        <strong>Ha sido rechazado</strong>
                        <p/>
                        <strong>
                            Motivo del rechazo: <field name="documentary_reject_reason" class="oe_inline"/>
                        </strong>
                        <p/>
                        <strong>
                            Fecha: <field name="documentary_validation_date" class="oe_inline"/>
                        </strong>
                        <p/>
                        <strong>
                            Usuario: <field name="documentary_user_id" class="oe_inline" options="{'no_open': True, 'no_quick_create': True, 'no_create': True}"/>
                        </strong>
                    </p>
                </div>
                <div class="alert alert-success" role="alert"
                    attrs="{'invisible': [('documentary_validation_state', '!=', 'validated')]}">
                    <p class="mb-0">
                        <strong>
                            El llamado ha sido validado
                        </strong>
                    </p>
                </div>
            </div>"""))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Add in form view divs with info status off documentary validation """
        res = super(ONSCCVAbstractFileValidation, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form' and self._context.get('is_cv_call', False):
            doc = etree.XML(res['arch'])
            field_ids = self.env["onsc.cv.documentary.validation.config"].search(
                [('model_id.model', '=', self._name)]).mapped('field_ids')
            for field in field_ids:
                node = doc.xpath("//field[@name='" + field.name + "']")
                for n in node:
                    n.set('doc-validation', 'label-text-danger')
            res['arch'] = etree.tostring(doc, encoding='unicode')
            for node in doc.xpath('//sheet'):
                node.insert(0, self.widget_documentary_button)
                if not len(doc.xpath('//field[@name="documentary_validation_state"]')):
                    node.insert(0, self.field_documentary_validation_state)
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
        self.write({
            'documentary_validation_state': 'validated',
            'documentary_reject_reason': '',
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        })

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
