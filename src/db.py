import os
import sqlite3
import datetime

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secure a connection with the database and stores it 
        into the instance variable 'conn'
        """
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_users_table()
        self.create_transxs_table()

    def create_users_table(self):
        """
        Using SQL, creates a users table
        """
        self.conn.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            balance REAL NOT NULL
        );
        """)

    def create_transxs_table(self):
        """
        Using SQL, create a subtask table
        """
        self.conn.execute("""CREATE TABLE IF NOT EXISTS transxs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            message TEXT NOT NULL,
            accepted BOOLEAN NULL,
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        );
        """)
    

#    def get_all_users(self):
 #       """
  #      Using SQL, returns all the users in a table
   #     """
    #    cursor = self.conn.execute("SELECT * FROM users")
     #   users = []
      #  for row in cursor:
       #     users.append({"id" : row[0], "name": row[1], "username": row[2]})
        #return users

    def get_all_users(self):
        """
        Using SQL, gets all tasks in the task table 
        """
        cursor = self.conn.execute("""
        SELECT * FROM users;
        """)
        users = []
        for row in cursor:
            users.append({
                "id" : row[0],
                "name" : row[1],
                "username" : row[2],
            })
        return users



    def get_user_by_id(self,id):
        """
        Gets a user by its id
        """
        cursor =  self.conn.execute("SELECT * FROM users WHERE id = ?;",(id,) )
        for row in cursor:
            return ({"id" : row[0], "name": row[1], "username": row[2], "balance": row[3], "transactions" : self.get_user_transxs(id)})
        return None

    def insert_user_table(self, name, username, balance):
        """
        Using SQL, this inserts a user into the users table
        """
        cursor = self.conn.execute("INSERT INTO users(name, username, balance) VALUES (?, ?, ?);", (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid

    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user from a table
        """
        self.conn.execute("DELETE FROM users WHERE id = ?;", (id,))
        self.conn.commit()

    def get_user_balance(self, id):
        """
        Using SQL, find the amount of money that a user has
        """
        cursor =  self.conn.execute("SELECT * FROM users WHERE id = ?;",(id,) )
        for row in cursor:
            return row[3]


    def update_user_by_id(self, balance, id):
        """
        Using SQL, update the balance of a specific user in users
        """
        self.conn.execute("""UPDATE users
        SET balance = ?
        WHERE id = ?;""", (balance, id))
        self.conn.commit()

    def insert_transx(self, timestamp, sender_id, receiver_id, amount, message, accepted):
        """
        Using SQL, adds a new subtask into the subtask table
        """
        cursor = self.conn.execute("""
            INSERT INTO transxs (timestamp, sender_id, receiver_id, amount, message, accepted) 
            VALUES (?, ?, ?, ?, ?, ?);""", (timestamp, sender_id, receiver_id, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid #returns id of last thing inserted and returns it

    def get_transx_by_id(self, id):
        """
        Using SQL, gets a transaction by its id
        """
        cursor = self.conn.execute("""
            SELECT * FROM transxs WHERE id=?;""", (id,),)
        for row in cursor: 
            return {
                "id" : id, 
                "timestamp" : row[1],
                "sender_id" : row[2],
                "receiver_id" : row[3],
                "amount" : row[4],
                "message" : row[5],
                "accepted" : row[6]
            }
        return None

    def update_transx(self, id, accepted):
        """
        Using SQL, update the transaction of a given transaction by its id
        """
        self.conn.execute("""UPDATE transxs
        SET accepted = ?
        WHERE id = ?;""", (accepted, id))
        self.conn.commit()


    def get_user_transxs(self, user_id):
        """
        Retrieve all transactions of a user based on their user ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM transxs 
        WHERE sender_id = ? OR receiver_id = ?
        """, (user_id, user_id))
        transactions = cursor.fetchall()
        trxs = []
        trx = {}
        for i in transactions:
            trx["id"] = i[0]
            trx["timestamp"] = i[1]
            trx["sender_id"] = i[2]
            trx["receiver_id"] = i[3]
            trx["amount"] = i[4]
            trx["message"] = i[5]
            trx["accepted"] = i[6]
            trxs.append(trx)
            trx = {}
        return trxs
    

    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user from a users
        """
        self.conn.execute("DELETE FROM users WHERE id = ?;", (id,))
        self.conn.commit()









# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
