# -*- coding: utf-8 -*-

from odoo import models, _
from ..onsc_cv_useful_tools import get_onchange_warning_response as cv_warning
from ..onsc_cv_useful_tools import is_valid_phone


# When inherit this class the child must have almost two fields:
# Any phone field: str Phone number (without country prefix code)
# And the corresponding prefix_phone: recordset of res.country.phone
# Its mandatory to declare prefix_by_phones property

# The result is the dynamic generation of onchange functions to validate phone and prefix fields

class ONSCCVAbstractPhoneValidated(models.AbstractModel):
    _name = 'onsc.cv.abstract.phone.validated'
    _description = 'Modelo abstracto para validar teléfonos'

    @property
    def prefix_by_phones(self):
        """
        Overwrite to define list of tuple of prefix and phones fields ex:
        [('prefix_phone_home_id','phone_home'), ('prefix_phone_work_id', 'phone_work')]
        :return: list
        """
        return []

    def onchange_validate_phone(self, prefix_phone_id, phone):
        prefix_phone_id = getattr(self, prefix_phone_id)
        phone_value = getattr(self, phone)
        phone_formatted, format_with_error, invalid_phone = is_valid_phone(phone_value, prefix_phone_id.country_id)
        setattr(self, phone, phone_formatted)
        if format_with_error:
            setattr(self, phone, False)
            return cv_warning(_("El teléfono ingresado no es válido"))
        if invalid_phone:
            setattr(self, phone, False)
            return cv_warning(
                _("El teléfono ingresado no es válido para %s" % prefix_phone_id.country_id.name))

    def _register_hook(self):
        """Add onchange method by each element on prefix_by_phones"""

        def make_method(prefix_phone_id, phone_str):
            return lambda self: self.onchange_validate_phone(prefix_phone_id, phone_str)

        for prefix, phone in self.prefix_by_phones:
            method = make_method(prefix, phone)
            self._onchange_methods[prefix].append(method)
            self._onchange_methods[phone].append(method)
