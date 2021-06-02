#!/aabb/cc/dd/python3

"""
    ############################## ABOUT ##############################

    This is a SQL query wrapper script which can be used to run SQL
    queries on MySQL DB. This generates sql query based on the type
    mentioned by the user and validates the generated query formed
    using the command line options provided by user to the script.
    This ensures appropriate where clause on primary keys is set for
    a table so that only a specific record is updated, if needed.
    In case DB is updated, then sends email to mentioned mailer list.
    Query supported type and non supported queries is mentioned below.
    Note: Mandatory Options --> -type <value> and -table <table name>

    Sample Usage from command line:

    wrapp_sql.py
        -type* <UPDATE/INSERT>
        -table* BUILD_DATA
        -BUILD_ID <value, *mandatory for UPDATE query>
        -PLATFORM <value, *mandatory for UPDATE query>
        -COMPONENT <value, default NA>
        -column1 <new value>
        -column2 <new value>

    Requirement: a databaseConfig file with multiple config sections as:

    [database_credentials]
    db_name=<db_name>
    db_hostname=<db_hostname>
    db_username=<db_username>
    db_password=<db_password>

    [table_primary_keys]
    <TABLES> = <Comma separated Primary Keys>
    TABLE = PK1, PK2, PK3...

    [table_columns]
    <TABLES> = <Comma separated Column Names>
    TABLE = COLUMN1, COLUMN2...

    ###################################################################
"""


try:
    import getpass
    import sys
    import argparse
    import subprocess
    import shutil
    import json
    import traceback
    from datetime import datetime
    import smtplib
    from email.mime.text import MIMEText
    import warnings
    import re
    from configparser import ConfigParser
    import mysql.connector
    from mysql.connector import Error
    import requests
    import os
except Exception as e:
    print("Failed to import modules: %s" %(e))


# Default mode is ni - non interactive
options_dict = {'mode': 'ni'}
# pk_dict to be updated via database_pk.cfg file
pk_dict = {}
# Types of SQL queries to be supported by this script
query_types = ["UPDATE", "INSERT", "DESC", "DESCRIBE"]
MAIL_TO = 'abcde@xyz.com'
mode = ""
type = ""
table = ""
sql_query = ""
column_list = []
send_email = False
query_status = False
tools = os.environ.get('TOOLS') or "/a/b/c/d/"
# databaseConfig has information about database
databaseConfig = tools + '/db/.databaseConfig.cfg'


def usage():
    """
    This shows some sample usage of the script
    such as HELP, UPDATE, INSERT & DESC or DESCRIBE
    """

    usage_str = "\nSAMPLE SCRIPT USAGE EXAMPLES:\n\n"
    usage_str += "HELP USAGE:\n"
    usage_str += "wrapp_sql.py <-help or -h>\n\n"
    usage_str += "UPDATE QUERY EXAMPLE:\n"
    usage_str += "wrapp_sql.py -type UPDATE -table BUILD_DATA -SITE sjc -BUILD_ID 1622025995 -PLATFORM ALL\n"
    usage_str += "Generated query: UPDATE BUILD_DATA SET SITE='sjc' WHERE PLATFORM='ALL' AND COMPONENT='NA' AND BUILD_ID='1622025995';\n\n"
    usage_str += "DESC or DESCRIBE QUERY EXAMPLE:\n"
    usage_str += "wrapp_sql.py -mode ni -type DESC -table BUILD_DATA\n"
    usage_str += "Generated query: DESC BUILD_DATA ;\n\n"
    usage_str += "INSERT QUERY EXAMPLE:\n"
    usage_str += "wrapp_sql.py -type INSERT -table BUILD_IDS -BUILD_ID 0246813579\n"
    usage_str += "Generated query: INSERT INTO BUILD_IDS VALUES ('0246813579') ;\n\n"
    print (usage_str)
    exit(1)


def validate_and_init_core_options(argv_list):
    """
    This function validates the mandatory arguments to
    this script like -typr and -table and also does
    important initializations for script functionality.
    :param argv_list: command line arguments
    """

    global mode
    global type
    global table
    global options_dict
    i = 0
    while i < len(argv_list) - 1:
        options_dict[str(argv_list[i])[1:]] = str(argv_list[i + 1])
        i = i + 2
    if not options_dict.get('type'):
        print("********** Missing mandatory option -type **********")
        usage()
    if not options_dict.get('type').upper() in query_types:
        print("********** Permission Denied: for -type %s **********" % (options_dict.get('type')))
        usage()
    if not options_dict.get('table'):
        print("********** Missing mandatory option -table **********")
        usage()
    mode = options_dict['mode']
    type = options_dict['type'].upper()
    table = options_dict['table']


def get_db_data(config_section_name):
    """
    This function reads the file databaseConfig which contains
    database relevant data in separate config sections.
    :param config_section: config section in databaseConfig
    :return: list of data set from required config section
    """

    try:
        config = ConfigParser()
        # Reading database_pk.cfg for getting table primary keys set
        config.read(databaseConfig)
        table_data = config.get(config_section_name, table)
        data_list = table_data.split(', ')
        return data_list
    except Exception as e:
        print("Failed to fetch primary keys for table %s in file %s: %s" % (table, databaseConfig, e))
        exit(1)


def validate_update_query():
    """
    This function fetch the required primary keys
    for the given table and validates the UPDATE query by
    verifying if the set of primary key is provided
    by the user through command line options.
    :return: 1 for failure else returns 0
    """

    pk_list = get_db_data('table_primary_keys')
    for pk in pk_list:
        pk_dict[pk] = ''
    if (table == 'BUILD_DATA') and (not options_dict.get("COMPONENT")):
        options_dict["COMPONENT"] = "NA"
    for i in pk_dict:
        if not options_dict.get(i):
            print("********** Missing primary key %s for WHERE clause on table %s **********" %(i, table))
            print("********** Please provide all the primary keys as an option to this script. **********")
            return 1
        else:
            pk_dict[i] = options_dict.get(i)
    return 0


def generate_update_query():
    """
    This functions generates the update query
    by concatenating query type as UPDATE, table name, SET
    clause ahd the where clause.
    :return: UPDATE query
    """

    set = "SET " + generate_set_col_val_pair()
    where = generate_where_clause()
    return type + " " + table + " " + set + " " + where + " ;"


def generate_insert_query():
    """
    This function generates the INSERT query by
    concatenating query type as INSERT and INTO table name
    with generates values set.
    :return: INSERT query
    """

    values = get_insert_values()
    return type + " INTO " + table + " VALUES (" + values + ") ;"


def get_insert_values():

    col_list = get_db_data('table_columns')
    values = ""
    for col in col_list:
        if col in options_dict.keys():
            values += "'" + options_dict.get(col) + "', "
        else:
            print("********** Missing value of column %s for insert query on %s **********" %(col, table))
            usage()
    return values[:-2]


def generate_where_clause():
    """
    This function generates WHERE clause using the
    dictionary pk_dict which has the set of pair of
    primary key of a table and its corresponding value.
    :return: WHERE clause
    """

    where_clause = "WHERE "
    i = 1
    for i in pk_dict:
        where_clause += str(i) + "='" + str(pk_dict.get(i)) + "' AND "
    return where_clause[:-5]


def generate_set_col_val_pair():
    """
    This function generates the SET clause for UPDATE query.
    :return: SET clause for UPDATE query
    """

    set_str = ""
    core_str = "mode type table"
    if type == "UPDATE":
        for i in pk_dict:
            core_str += " " + i
    for i in options_dict:
        if not (i in core_str):
            if type == "UPDATE":
                set_str += i + "="
            set_str += "'" + options_dict.get(i) + "', "
    return set_str[:-2]


def run_Query(query):
    """
    This function connects to the database using the config file
    and executes the query passed to this function as argument &
    finally returns the fetched row or UPDATE/INSERT query output.
    :param query: SQL query to execute
    :return: UPDATE/INSERT query output or the fetched row
    """

    try:
        global column_list
        global query_status
        result = []
        config = ConfigParser()
        # Reading the database config file for database information
        config.read(databaseConfig)
        db_hostname = config.get('database_credentials', 'db_hostname')
        db_name = config.get('database_credentials', 'db_name')
        db_username = config.get('database_credentials', 'db_username')
        db_password = config.get('database_credentials', 'db_password')
        connection = mysql.connector.connect(host=db_hostname,
                                             database=db_name,
                                             user=db_username,
                                             password=db_password,
                                             allow_local_infile=False)
        if connection.is_connected():
            cursor = connection.cursor()
            print("\nRunning SQL query: %s \n" % (query))
            cursor.execute(query)
            if type == "UPDATE" or type == "INSERT":
                connection.commit()
                result.append(str(cursor.rowcount)+" record(s) affected")
            else:
                result = cursor.fetchall()
                column_list = [i[0] for i in cursor.description]
            query_status = True
    except Exception as e:
        print("Exception caught in function run_Query: %s" % (e))
        query_status = False
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("\nMySQL connection is closed\n")
            return result


def sendEmail(mail_text):
    """
    This functions accepts mail body as a function argument
    and sends an email to the MAIL_TO with the specified SUBJECT
    :param mail_text: Mail body text
    """

    try:
        SMTP_MAIL_SERVER = 'pqr.xyz.com'
        MAIL_FROM = 'noreply@xyz.com'
        MAIL_SUBJECT = "DATABASE 'db' UPDATED"
        # Construct the message object
        MailMessage_Ob = MIMEText(mail_text)
        MailMessage_Ob['Subject'] = MAIL_SUBJECT
        MailMessage_Ob['From'] = MAIL_FROM
        MailMessage_Ob['To'] = MAIL_TO
        # Send email
        Smtp_Ob = smtplib.SMTP(SMTP_MAIL_SERVER)
        Smtp_Ob.send_message(MailMessage_Ob)
        exit()
    except Exception as e:
        print("Failed sending email to %s: %s" % (MAIL_TO, e))


if __name__ == '__main__':

    try:
        if not os.path.exists(databaseConfig):
            print("\nFile not found: %s" %(databaseConfig))
            exit(1)
        result = []
        if len(sys.argv) < 2:
            print('********** No option provided to the script. **********')
            usage()
        if sys.argv[1] == '-h' or sys.argv[1] == '-help':
            usage()
        validate_and_init_core_options(sys.argv)
        if type == 'UPDATE':
            if validate_update_query():
                print ("********** Update query validation failed. **********\n")
                exit(1)
            else:
                sql_query = generate_update_query()
                send_email = True
        elif type == 'INSERT':
            sql_query = generate_insert_query()
            send_email = True
        elif type == 'DESC' or type == 'DESCRIBE':
            sql_query = type + " " + table + " ;"
        result = run_Query(sql_query)
        if query_status:
            print(result)
    except Exception as e:
        print("\nScript failed to run: %s" % (e))
    finally:
        if send_email and query_status:
            user = getpass.getuser()
            mail_txt = "Database updated by user: " + user + "\n"
            mail_txt += "Query executed: " + sql_query + "\n"
            mail_txt += "Query output: " + str(result) + "\n"
            print("\nSending email notification to %s\n" %(MAIL_TO))
            print("\n" + mail_txt + "\n")
            sendEmail(mail_txt)
