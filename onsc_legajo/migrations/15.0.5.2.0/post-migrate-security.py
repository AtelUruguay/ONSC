# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        offices = env['onsc.legajo.office'].search([('proyectoDescripcion', '!=', False), ('proyecto', '=', False)])
        offices.write({'proyecto': '0'})
    except Exception as e:
        pass
