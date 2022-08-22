# Part of Odoo. See LICENSE file for full copyright and licensing details.
import sys
# import the error handling libraries for psycopg2
import logging
_logger = logging.getLogger(__name__)


# define a function that handles and parses psycopg2 exceptions
def print_psycopg2_exception(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()
    # get the line number when exception occured
    line_num = traceback.tb_lineno
    # print the connect() error
    _logger.info("\npsycopg2 ERROR: %s on line number: %s", err, line_num)
    _logger.info("psycopg2 traceback: %s -- type: %s", traceback, err_type)

    # psycopg2 extensions.Diagnostics object attribute
    _logger.info("\nextensions.Diagnostics: %s", err.diag)

    # print the pgcode and pgerror exceptions
    _logger.info("pgerror: %s", err.pgerror)
    _logger.info("pgcode: %s\n", err.pgcode)


def list_to_sql_tuple(convert_list):
    new_tuple = ""
    if len(convert_list) == 1:
        new_tuple += "(" + str(convert_list[0]) + ")"
    else:
        new_tuple = str(tuple(convert_list))
    return new_tuple


def get_average_db_query(question_ids, survey_ids, date_from,
                         date_to):
    sql = """select avg(quizz_mark) as Promedio, max(quizz_mark)
             as Maximo, count(*) as Cantidad from survey_user_input_line
             where question_id in {0} and survey_id in {1} and
             date_create >= '{2}' and date_create <= '{3}'""".\
        format(question_ids, survey_ids, date_from, date_to)
    return sql


def get_average_grouped_answers_db_query(question_ids, survey_ids,
                                         date_from, date_to):
    sql = """select value_suggested, count(*) as cantidad
             from survey_user_input_line
             where question_id in {0} and survey_id in {1} and
             date_create >= '{2}' and date_create <= '{3}'
             group by value_suggested""".\
        format(question_ids, survey_ids, date_from, date_to)
    return sql


def get_nsnc_answers(survey_ids, date_from, date_to):
    sql = """select count(*) as nsnc_answer from survey_user_input
             where survey_id in {0} and
             date_create >= '{1}' and date_create <= '{2}' and
             id in (select user_input_id from survey_user_input_line);""".\
        format(survey_ids, date_from, date_to)
    return sql


def search_read_db(table, select_fields, where_conditions):
    return """
    select {0}
    from {1}
    where {2}
    """.format(select_fields, table, where_conditions)


def get_table(model_name):
    return model_name.replace(".", "_")


def get_select_fields(fields):
    string_fields = ""
    primero = True
    for f in fields:
        if primero:
            string_fields += str(f)
            primero = False
        else:
            string_fields += " , " + str(f)
    return string_fields
