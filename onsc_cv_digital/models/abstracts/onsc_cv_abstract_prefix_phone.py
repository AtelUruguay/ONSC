from odoo import models, fields
from odoo.exceptions import MissingError


class ONSCCVAbstractPrefixPhone(models.AbstractModel):
    _name = 'onsc.cv.abstract.prefix.phone'
    _description = 'Calse abstracta para definir campos de prefijos telefónicos'
    _fields_prefix_phones = ['prefix_phone']

    prefix_phone = fields.Many2one('res.country', 'Prefijo',
                                   default=lambda self: self.env['res.country'].search([('code', '=', 'UY')]))

    def _read_format(self, fnames, load='_classic_read'):
        """Returns a list of dictionaries mapping field names to their values,
        with one dictionary per record that exists.

        The output format is similar to the one expected from the `read` method.

        The current method is different from `read` because it retrieves its
        values from the cache without doing a query when it is avoidable.
        """
        data = [(record, {'id': record._ids[0]}) for record in self]
        use_name_get = (load == '_classic_read')

        for name in fnames:
            convert = self._fields[name].convert_to_read
            for record, vals in data:
                # missing records have their vals empty
                if not vals:
                    continue
                try:
                    if name in self._fields_prefix_phones:
                        record = record.with_context(format_phone_code=True)
                    vals[name] = convert(record[name], record, use_name_get)
                except MissingError:
                    vals.clear()
        result = [vals for record, vals in data if vals]

        return result
