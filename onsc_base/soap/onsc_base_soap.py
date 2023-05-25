# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from spyne import ComplexModelBase, ComplexModel
from spyne import Unicode
from spyne.model.complex import Array

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


class BaseComplexType(ComplexModelBase):
    __namespace__ = NAMESPACE_BASE_V1


class ErrorHandler(ComplexModel):
    __type_name__ = 'error_handler'
    _type_info = [
        ('type', Unicode(min_occurs=1)),
        ('code', Unicode(min_occurs=1)),
        ('error', Unicode(min_occurs=1)),
        ('description', Unicode(min_occurs=1)),
    ]
    _type_info_alt = []


class WsResponse(BaseComplexType):
    __type_name__ = 'service_response'
    _type_info = {
        'result': Unicode(min_occurs=1),
        'description': Unicode(min_occurs=0),
        'errors': Array(ErrorHandler, min_occurs=0, type_name='ArrayOfErrorHandler')
    }
    _type_info_alt = []
