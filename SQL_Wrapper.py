#!<python3_path>/python3


"""
    ############################## USAGE ##############################
    This is a SQL query wrapper script which can be used to run SQL
    queries on MySQL DB. This validates the query provided by user from
    command line such that it doesn't modify existing DB structure.
    This also ensures the appropriate where clause on Primary Keys set
    for a table so that only a specific record is updated, if needed.
    In case DB is updated, then sends email to mentioned mailer list.
    Query supported list and Non supported Queries is mentioned below.
    Sample Usage from command line:
    <python3_path>/python3 sql_wrapper.py  show "tables;"
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
    print("Failed to import required modules: %s" %(e))


query = ""
send_email = False
query_status = True
argv_list = []
column_list = []
# Permitted list: query_list
query_list = ["SHOW", "DESCRIBE", "DESC", "SELECT", "INSERT", "UPDATE"]
# Non Permitted List: ["CREATE", "ALTER", "DELETE", "TRUNCATE", "DROP"]


def sendEmail(mail_text):

    """
    Sends an email to specified mailers list information.
    :param mail_text: Mail body
    :return: exit()
    """

    SMTP_MAIL_SERVER = 'abcde.domain.com'
    NOREPLY_ADDR = 'noreply@domain.com'
    MAIL_SUBJECT = 'db SQL Query - Email Notification Test'

    # Construct the message object
    MailMessage_Ob = MIMEText(mail_text)
    MailMessage_Ob['Subject'] = MAIL_SUBJECT
    MailMessage_Ob['From'] = NOREPLY_ADDR
    MailMessage_Ob['To'] = 'abhinav@domain.com'
    # Send the msg
    Smtp_Ob = smtplib.SMTP(SMTP_MAIL_SERVER)
    Smtp_Ob.send_message(MailMessage_Ob)
    exit()


def run_Query(query):

    """
    Executes the SQL query after making connection with db details
    :param query: SQL query to be run on DB
    :return: Query output
    """

    global column_list
    global query_status
    result = []
    data = ""
    config = ConfigParser()
    # Reading the database config file for database information
    config.read('/users/abhinav/.dbConfig.cfg')
    db_hostname = config.get('database_information', 'db_hostname')
    db_name = config.get('database_information', 'db_name')
    db_username = config.get('database_information', 'db_username')
    db_password = config.get('database_information', 'db_password')

    try:
        connection = mysql.connector.connect(host=db_hostname,
                                             database=db_name,
                                             user=db_username,
                                             password=db_password,
                                             allow_local_infile=False)
        if connection.is_connected():
            cursor = connection.cursor()
            print("\nRunning SQL query: %s \n" % (query))
            cursor.execute(query)
            result = cursor.fetchall()
            num_column = len(cursor.description)
            column_list = [i[0] for i in cursor.description]
    except Exception as e:
        print("\nFailed to run sql query: %s \n %s\n" % (query, e))
        query_status = False
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("\nMySQL connection is closed\n")
            return result

def wrapp_result(result):

    """
    Reformatting of query output
    :param result: Output of SQL query
    :return: String - Structured output
    """

    data = ""
    for c in column_list:
        data = data + " | " + str(c)
    data = data + " |\n\n"
    for r in result:
        for c in r:
            if type(c) == bytearray:
                c = bytes(bytes(c))
            data = data + " | " + str(c)
        data = data + " |\n\n"
    return data

def validate_Constraints(query, argv_list):

    """
    Validates UPDATE SQL queries by verifying existence of WHERE clause
    on set of primary keys so that only one record is affected/updated
    :param query: SQL query provided by command line argument
    :param argv_list: Command line argument list
    :return: 0 or 1 based on validation
    """

    global send_email
    list_pk = []
    q = query.upper()
    my_table_name = query.split()[1]
    if not q.__contains__("WHERE "):
        print("\nWHERE clause missing in query: %s\n" % (query))
        return 1
    else:
        # Below query is used to get list of primary key of a table named my_table_name
        sq = 'SELECT k.column_name FROM information_schema.table_constraints t ' \
             'JOIN information_schema.key_column_usage k USING(constraint_name,table_schema,table_name) ' \
             'WHERE t.constraint_type="PRIMARY KEY" AND t.table_schema="your_database_name" AND t.table_name="' + my_table_name + '";'
        list_pk = run_Query(sq)
        list_pk = [i[0] for i in list_pk]
        for pk in list_pk:
            if not pk in query:
                print("Primary key %s not in query: %s" % (pk, query))
                return 1
        send_email = True
        return 0


def validate_Query(query, argv_list):

    """
    Validates permitted SQL queries
    :param query: SQL query provided by command line argument
    :param argv_list: Command line argument list
    :return: 0 or 1 based on validation
    """

    c1 = argv_list[1].upper()=="UPDATE"
    if c1:
        return validate_Constraints(query, argv_list)
    else:
        return 0


if __name__ == '__main__':

    """
    Accepts SQL query as command line argument
    Validates and execute query to display on console
    and sends email on any successful UPDATE query
    """

    result = []
    try:
        argv_list = sys.argv
        query = ' '.join(argv_list[1:])
        if (not argv_list[1].upper() in query_list) or validate_Query(query, argv_list):
            print("\nPermission Denied\n")
            exit(1)
        result = run_Query(query)
        db_data = wrapp_result(result)
        print("\n" + db_data + "\n")
        print("Success!!!")
    except Exception as e:
        print("\nScript Failed to run: %s" % (e))
    finally:
        if send_email and query_status:
            user = getpass.getuser()
            mail_txt = "Database updated by USER: " + user + "\n"
            mail_txt += "Query Executed: " + query + "\n"
            mail_txt += "Query Output: " + str(result) + "\n"
            print("\nSending Email Notification\n")
            print("\n" + mail_txt + "\n")
            send_email(mail_txt)
