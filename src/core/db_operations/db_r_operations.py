import pymysql
from datetime import datetime
from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='error', logfile_name='db.log')
db_logger = custom_logger.create_logger()


class DBOperations:
    def __init__(self, db_config: dict):
        self.db_host_name = db_config.get('db_host')
        self.db_port = db_config.get('db_port')
        self.db_name = db_config.get('db_name')
        self.db_user = db_config.get('db_user')
        self.db_pass = db_config.get('db_pass')

    def create_db_connection(self):
        try:
            db_connection = pymysql.connect(
                host=self.db_host_name,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass
            )
            db_logger.info(f"Opened database connection")
            return db_connection
        except Exception as err:
            db_logger.error(f"Problem while creating database connection: {err}")

    def check_connection(self):
        try:
            db_con = self.create_db_connection()
            with db_con:
                c = db_con.cursor()
                c.execute("SELECT VERSION()")
                data = c.fetchone()
            db_logger.info(f"Database Version Check successful")
            return {'status': True, 'data': data}
        except Exception as err:
            db_logger.error(f"Database connection error: {err}")
            return {'status': False, 'data': 'Something wrong with Database Connection'}

    def get_all_planetary_tax(self):
        try:
            db_con = self.create_db_connection()
            with db_con:
                c = db_con.cursor()
                c.execute(
                    "SELECT amount, date, reason FROM corptools_corporationwalletjournalentry "
                    "WHERE ref_type='planetary_import_tax' or ref_type='planetary_export_tax'"
                    " ORDER BY date"
                )
                data = c.fetchall()
                if not data:
                    db_logger.info(f"get_all_planetary_tax empty response")
                    return {
                        'status': False,
                        'data': 'There is no data for your request!\nCheck the entered data and try again'
                    }
            db_logger.info(f"get_all_planetary_tax req/resp successful")
            return {'status': True, 'data': data}
        except Exception as err:
            db_logger.error(f"get_all_planetary_tax Database connection error: {err}")
            return {'status': False, 'data': 'Something wrong with Database Connection'}

    def get_period_planetary_tax(self, period_start, period_end, system_name: str = None, character_name: str = None):
        try:
            formated_period_start = datetime.strptime(period_start, "%Y.%m.%d").date()
            formated_period_end = datetime.strptime(period_end, "%Y.%m.%d").date()
            try:
                db_con = self.create_db_connection()
                with db_con:
                    c = db_con.cursor()
                    if system_name and not character_name:
                        c.execute(
                            "SELECT corptools_corporationwalletjournalentry.amount, "
                            "corptools_corporationwalletjournalentry.date, "
                            "corptools_evename.name AS char_name  "
                            "FROM corptools_corporationwalletjournalentry "
                            "JOIN corptools_evename "
                            "ON corptools_corporationwalletjournalentry.first_party_name_id = corptools_evename.eve_id "
                            "WHERE (ref_type='planetary_import_tax' or ref_type='planetary_export_tax') "
                            "AND (DATE(date) BETWEEN %s and %s)"
                            "AND (corptools_corporationwalletjournalentry.reason LIKE %s) "
                            "ORDER BY corptools_corporationwalletjournalentry.date",
                            (formated_period_start, formated_period_end, f"%%{system_name}%%")
                        )
                        db_logger.info(f"get_period_planetary_tax (system_name and not character_name) query")
                    elif character_name and not system_name:
                        c.execute(
                            "SELECT corptools_corporationwalletjournalentry.amount,"
                            "corptools_corporationwalletjournalentry.date,"
                            "corptools_corporationwalletjournalentry.reason, corptools_evename.name AS char_name "
                            "FROM corptools_corporationwalletjournalentry JOIN corptools_evename "
                            "ON corptools_corporationwalletjournalentry.first_party_name_id = corptools_evename.eve_id "
                            "WHERE (corptools_corporationwalletjournalentry.ref_type='planetary_import_tax' "
                            "or corptools_corporationwalletjournalentry.ref_type='planetary_export_tax') "
                            "AND (DATE(corptools_corporationwalletjournalentry.date) BETWEEN %s and %s)"
                            "AND (corptools_evename.name = %s) ORDER BY corptools_corporationwalletjournalentry.date",
                            (formated_period_start, formated_period_end, character_name)
                        )
                        db_logger.info(f"get_period_planetary_tax (character_name and not system_name) query")
                    elif system_name and character_name:
                        c.execute(
                            "SELECT corptools_corporationwalletjournalentry.amount, "
                            "corptools_corporationwalletjournalentry.date, "
                            "corptools_corporationwalletjournalentry.reason, corptools_evename.name AS char_name  "
                            "FROM corptools_corporationwalletjournalentry JOIN corptools_evename "
                            "ON corptools_corporationwalletjournalentry.first_party_name_id = corptools_evename.eve_id "
                            "WHERE (corptools_corporationwalletjournalentry.ref_type='planetary_import_tax' "
                            "or corptools_corporationwalletjournalentry.ref_type='planetary_export_tax') "
                            "AND (DATE(corptools_corporationwalletjournalentry.date) BETWEEN %s and %s)"
                            "AND (corptools_corporationwalletjournalentry.reason LIKE %s) "
                            "AND (corptools_evename.name = %s) "
                            "ORDER BY corptools_corporationwalletjournalentry.date",
                            (formated_period_start, formated_period_end, f"%%{system_name}%%", character_name)
                        )
                        db_logger.info(f"get_period_planetary_tax (system_name and character_name) query")
                    else:
                        c.execute(
                            "SELECT amount, date, reason FROM corptools_corporationwalletjournalentry "
                            "WHERE (ref_type='planetary_import_tax' or ref_type='planetary_export_tax') AND "
                            "(DATE(date) BETWEEN %s and %s) "
                            "ORDER BY date",
                            (formated_period_start, formated_period_end)
                        )
                        db_logger.info(f"get_period_planetary_tax (else) query")
                    data = c.fetchall()
                    if not data:
                        db_logger.error(f"get_period_planetary_tax empty response")
                        return {
                            'status': False,
                            'data': 'There is no data for your request!\nCheck the entered data and try again'
                        }
                db_logger.info(f"get_period_planetary_tax req/resp successful")
                return {'status': True, 'data': data}
            except Exception as err:
                db_logger.error(f"get_period_planetary_tax Database connection error: {err}")
                return {'status': False, 'data': 'Something wrong with Database Connection'}
        except ValueError as convertError:
            db_logger.info(f"get_period_planetary_tax Wrong date format: {convertError}")
            return {'status': False, 'data': f'Wrong date format: {convertError}'}

