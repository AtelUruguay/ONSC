# -*- coding: utf-8 -*-

def _get_validation_status(record, validation_catalog_string):
    if len(record) > 1:
        return False
    _state = 'validated'
    for catalog in validation_catalog_string:
        catalog_state = eval('record.%s.state' % (catalog))
        if catalog_state == 'rejected':
            return 'rejected'
        if catalog_state == 'to_validate' and _state == 'validated':
            _state = 'to_validate'
    return _state
