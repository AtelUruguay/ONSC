# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Delete model onsc.cv.abstract.origin.institution because change name to onsc.cv.abstract.work
    cr.execute("delete from ir_model where model='onsc.cv.abstract.origin.institution'")
    # Delete constrains
    cr.execute("ALTER TABLE onsc_cv_location DROP CONSTRAINT IF EXISTS localidad_name_by_state_unique")
