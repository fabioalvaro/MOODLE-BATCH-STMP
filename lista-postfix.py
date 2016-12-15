#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import time
import sys
import pprint
import MySQLdb
import ConfigParser

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


# variables
conta_ses = 0
conta_ghost = 0
conta_postfix = 0
conta_vazio = 0

host = '10.10.10.10'
user = 'me'
password = '89745'

#se True update the connection to reflect the
muda_a_base = False



Config = ConfigParser.ConfigParser()
Config.read("settings.ini")
Config.sections()

host = ConfigSectionMap("MYSQLROOT")['host']
user = ConfigSectionMap("MYSQLROOT")['user']
password = ConfigSectionMap("MYSQLROOT")['password']

SERVER_AWS = ConfigSectionMap("SERVERS")['server_aws']



# change the connection and set to PostFix Server Pre-adjusted

def setPostFix(database):
    global Config
    #CHANCE HERE THE IP OF YOUR MAIN POSTFIX SERVER
    IP_POSTFIX = ConfigSectionMap("SERVERS")['server_postfix']

    resp = "\n"
    erro = True
    # variaveis
    global host
    global user
    global password

    db = MySQLdb.connect(host=host,  # your host, usually localhost
                         user=user,  # your username
                         passwd=password,  # your password
                         db=database,
                         port=3333)  # name of the data base

    db.autocommit(True)

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    # Use all the SQL you like
    
    sql = '''
    update mdl_config
    set value=""
    where name like "smtpuser";
    update mdl_config
    set value=""
    where name like "smtppass";'''

    try:
        cur.execute("""update mdl_config set value=%s where name like %s""", (IP_POSTFIX, 'smtphosts'))
        cur.execute("""update mdl_config set value=%s where name like %s""", ('', 'smtpuser')) #CHANGE HERE THE USER AND PASS
        cur.execute("""update mdl_config set value=%s where name like %s""", ('', 'smtppass')) #CHANGE HERE THE USER AND PASS
      
        resp = resp + "DATABASE..." + database + " Updated!\n"
        #resp = resp + "=========================================================\n"

        db.close()
        erro = False
    except Exception:
        pass



    if erro==True:
        resp = resp + "DATABASE..." + database + "\n"
        resp = resp + "=========================================================\n"
        resp = resp +"Erro to update!"

    return resp

# retrieve the database from server to database selected

def getSMTPCONF(database):

    global Config
    global conta_ses
    global conta_ghost
    global conta_vazio
    global conta_postfix

    SERVER_AWS = ConfigSectionMap("SERVERS")['server_aws']



    SERVER_ONPREMISSES = ConfigSectionMap("SERVERS")['server_onpremisses']
    SERVER_POSTFIX = ConfigSectionMap("SERVERS")['server_postfix']

    resp = "\n"
    erro = True
    # variaveis
    global host
    global user
    global password


    import MySQLdb

  
    db_atual = database

    db = MySQLdb.connect(host=host,  # your host, usually localhost
                         user=user,  # your username
                         passwd=password,  # your password
                         db=db_atual,
                         port=3333)  # name the Mysql port of setup

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    # Use all the SQL you like
    sql = '''select * from mdl_config
    where name like "smtphosts" OR
    name like "smtpuser" OR
    name like "smtppass" '''

    try:
        cur.execute(sql)
        resp = resp + "DATABASE..." + db_atual + "\n"
        resp = resp + "=========================================================\n"
        for row in cur.fetchall():
            resp = resp + str(row[1])+ " " + str(row[2])+"\n"

            if row[1] == "smtphosts":
                if row[2] == SERVER_AWS: #Server AWS
                    conta_ses = conta_ses + 1
                if row[2] == SERVER_ONPREMISSES: #Server On-Premises
                    conta_ghost = conta_ghost + 1
                if row[2] == SERVER_POSTFIX: #server PostFix
                    conta_postfix = conta_postfix + 1
                if row[2] == "":
                    conta_vazio = conta_vazio + 1


                        # pprint.pprint(row)
        db.close()
        erro = False
    except Exception:
        pass

    #update SMTP SERVER SETTING
    #conditions: Not A error, the parameters must be set to True
    global muda_a_base

    if erro == False:
        if muda_a_base == True:
            print setPostFix(db_atual)


    if erro==True:
        resp = resp + "DATABASE..." + db_atual + "\n"
        resp = resp + "=========================================================\n"
        resp = resp +"Erro!"

    return resp

#Clean the screen
os.system("clear")

ans=True
while ans:
    print("""
    MOODLE BATCH STMP CONFIGURATION 1.0 by Linux Campinas
    http://linuxcampinas.blogspot.com.br/
    ==================================================================
    1.List SMTP Configuration
    2.Update to Default POSTFIX Server
    4.Exit/Quit
    """)
    ans=raw_input("What would you like to do? ")
    if ans=="1":
      print("\nList SMTP Configuration")
      muda_a_base = False
      ans = None
    elif ans=="2":
      print("\n Update to Default POSTFIX Server")
      muda_a_base = True
      ans = None
    elif ans=="4":
      print("\n None")
      ans = None
    else:
       print("\n Not Valid Choice Try again")


print "Continuando...."



#limpa a tela
os.system("clear")





#How to use:

# put here the database name for each line e.g:
# and uncomment the lines below

#print getSMTPCONF("mydb_name1")
#print getSMTPCONF("mydb_name2")
#print getSMTPCONF("mydb_name3")

print "\n Databases set to SES: " + str(conta_ses)+""
print "\n Databases set to Ghost: " + str(conta_ghost)+""
print "\n Databases set to PostFix: " + str(conta_postfix)+""
print "\n Databases set to Empty: " + str(conta_vazio)+""


print "End of Process"
exit()
