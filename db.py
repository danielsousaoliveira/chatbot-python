#
# File: db.py
# Author: Daniel Oliveira
#

### MySQL Database Initial Definition and Handling ###

from __future__ import annotations

## Import dependencies ##

import os
from typing import Any
from dotenv import load_dotenv
from mysql.connector import connect, Error

load_dotenv()

## Helper to open a database connection using environment variables ##

def get_connection(with_db: bool = True) -> Any:
    kwargs = dict(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
    )
    if with_db:
        kwargs['database'] = os.environ['MYSQL_DB']
    return connect(**kwargs)

## Create MySQL Database, if there is none with the same name ##

def createDB() -> None:
    try:
        with get_connection(with_db=False) as connection:
            create_db = "CREATE DATABASE IF NOT EXISTS `crexusers` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
            with connection.cursor() as cursor:
                cursor.execute(create_db)
    except Error as e:
        print(e)

## Create table inside the database, if there is none with the same name ##

def createTable() -> None:
    try:
        with get_connection() as connection:
            create_table ="""CREATE TABLE IF NOT EXISTS `accounts` (
	                      `id` int(11) NOT NULL AUTO_INCREMENT,
  	                      `username` varchar(50) NOT NULL,
                          `name` varchar(100) NOT NULL,
  	                      `password` varchar(255) NOT NULL,
  	                      `email` varchar(100) NOT NULL,
                          `balance` int(255) NOT NULL,
                          PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"""
            with connection.cursor() as cursor:
                cursor.execute(create_table)
                connection.commit()
    except Error as e:
        print(e)

## Print current database state ##

def printDB() -> None:
    connection = get_connection()
    show ="SELECT * FROM accounts"
    with connection.cursor() as cursor:
        cursor.execute(show)
        result = cursor.fetchall()
    for row in result:
        print(row)

## Create initial accounts with user data and insert them into the database ##

def insertInitialAccounts() -> None:
    connection = get_connection()
    ins = """INSERT IGNORE INTO `accounts` (`id`, `username`, `name`, `password`, `email`, `balance`)
          VALUES
          (1, 'daniel', 'Daniel Oliveira', 'pass1', 'danielsoliveira@ua.pt', 0)
          """
    with connection.cursor() as cursor:
        cursor.execute(ins)
        connection.commit()

## Remove one chosen user ##

def removeUser(user: str) -> None:
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM accounts WHERE username = %s", (user,))
        connection.commit()

## Delete existing database ##

def deleteDB() -> None:
    connection = get_connection()
    deldb = "DROP DATABASE crexusers"
    with connection.cursor() as cursor:
        cursor.execute(deldb)
        connection.commit()

## Update user BTC balance, buying more or selling what he currently have ##

def updateBalance(id: int, new: int, flag: bool) -> None:
    connection = get_connection()
    with connection.cursor() as cursor:
        if flag:
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (new, id))
        else:
            cursor.execute("UPDATE accounts SET balance = GREATEST(0, balance - %s) WHERE id = %s", (new, id))
        connection.commit()

## Update user password on the database ##

def updatePassword(id: int, new: str) -> None:
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("UPDATE accounts SET password = %s WHERE id = %s", (new, id))
        connection.commit()

## Update user email on the database ##

def updateEmail(id: int, new: str) -> None:
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("UPDATE accounts SET email = %s WHERE id = %s", (new, id))
        connection.commit()

## Initial function to create database, table and insert accounts ##

def initializeDB() -> None:
    createDB()
    createTable()
    insertInitialAccounts()

## Main function just to print current state of database ##

def main() -> None:
    #initializeDB() #run in the first initialization
    printDB()

## Run directly to check database ##
if __name__ == "__main__":
    main()
