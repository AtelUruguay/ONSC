# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Delete model onsc.cv.abstract.origin.institution because change name to onsc.cv.abstract.work
    cr.execute("delete from ir_model where model='onsc.cv.abstract.origin.institution'")
    # Delete model onsc.cv.abstract.origin.institution.task because change name to onsc.cv.abstract.work.task
    cr.execute("delete from ir_model where model='onsc.cv.origin.institution.task'")
