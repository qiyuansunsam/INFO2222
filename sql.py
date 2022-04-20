import sqlite3
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
import crypt
import random


# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()
        self.id = 1

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    # -----------------------------------------------------------------------------

    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='password'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.commit()

        # Add our admin user

        self.execute("""CREATE TABLE IF NOT EXISTS chatlink(
            CID INTEGER PRIMARY KEY AUTOINCREMENT,
            UIDSEND INT references Users(Id),
            UIDRECIEVE INT references Users(Id));""")
        self.commit()

        self.execute("""CREATE TABLE IF NOT EXISTS chatlog(
            CID INT references chatlink(CID),
            message TEXT,
            timestmp TIMESTAMP);""")
        self.commit()

        self.execute("""CREATE TABLE IF NOT EXISTS salts(
            Id INTEGER UNIQUE references Users(Id),
            salt TEXT);""")
        self.commit()

        self.execute("""CREATE TABLE IF NOT EXISTS exchange(
            UIDSEND INT references Users(Id),
            UIDRECIEVE INT references Users(Id),
            key TEXT,
            timestmp TIMESTAMP);""")
        self.commit()
        # Add key table
        self.execute("""CREATE TABLE IF NOT EXISTS pubkeys(
                    Id INTEGER UNIQUE references Users(Id),
                    pubkey TEXT);""")
        self.commit()
        
        # Add our admin user
        self.add_user('admin', admin_password, admin=1)
        self.add_user('t1', admin_password, admin=0)
        self.add_user('t2', admin_password, admin=0)
        self.add_user('t3', admin_password, admin=0)

    # -----------------------------------------------------------------------------
    # User handling
    # -----------------------------------------------------------------------------

    #Testing issue - check that firsttuple[0] is correct
    def pull(self,SID,RID):
        sql_query = """
            SELECT key,timestmp 
            FROM exchange
            WHERE (UIDSEND like {SID} and UIDRECIEVE like {RID}) OR (UIDSEND like {RID} and UIDRECIEVE like {SID})
            ORDER BY timestmp DESC
        """
        sql_query = sql_query.format(SID=SID,RID=RID)
        self.execute(sql_query)
        firsttuple = self.cur.fetchone()
        if firsttuple:
            
            return firsttuple[0]
        else:
            return ""

    def pull_public_key(self, Id):
        sql_query = """
                    SELECT pubkey 
                    FROM pubkeys
                    WHERE Id like '{Id}'
                """
        sql_query = sql_query.format(Id=Id)
        self.execute(sql_query)
        t = self.cur.fetchone()[0]
        print("public key: "+t)
        return t

    def write_key(self,SID,RID,key):
        sql_statement = """
                INSERT into exchange
                VALUES({SID},{RID},'{key}',CURRENT_TIMESTAMP)
            """
        sql_statement = sql_statement.format(SID=SID,RID=RID,key=key)
        self.execute(sql_statement)
        self.commit()




    #SQL here might not be 100% correct - also 
    #Need to check that in exchange table, row where RID,SID,key is the ROw that the SSK is sent in if not just need to swap SID and RID
    def wipekeys(self,SID,RID):
        sql_statement = """
                UPDATE exchange
                SET key = 'wipe'
                WHERE
                UIDSEND like {RID} and UIDRECIEVE like {SID}
            """
        sql_statement = sql_statement.format(RID=RID,SID=SID)
        self.execute(sql_statement)
        self.commit()

    # Add a user to the database
    def add_user(self, username, password, admin=0):
        print(username)
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars=[]
        for i in range(16):
            chars.append(random.choice(ALPHABET))
        salt = "".join(chars)
        password = password+salt
        hashobj = SHA256.new(data=password.encode())
        hashedpass = hashobj.hexdigest()
        sql_cmd = """
                INSERT INTO Users(username,password,admin)
                VALUES('{username}', '{password}', {admin})
            """

        sql_cmd = sql_cmd.format(username=username, password=hashedpass, admin=admin) 
        self.execute(sql_cmd)
        self.commit()

        sql_query = """
            SELECT Id 
            FROM Users
            WHERE username like '{username}'
        """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        result = self.cur.fetchall()
        Id = result[0][0]
        
   

        sql_cmd = """
            INSERT INTO salts(Id,salt)
            VALUES('{Id}','{salt}')
            """

        sql_cmd=sql_cmd.format(Id=Id,salt=salt)
        self.execute(sql_cmd)
        self.commit()

        return Id

    
    def addkey(self, Id, pubkey):
        sql_statement = """
            INSERT INTO pubkeys(id,pubkey)
            VALUES('{Id}','{pubkey}')
            """
        sql_statement = sql_statement.format(Id=Id, pubkey=pubkey)
        print(sql_statement)
        self.execute(sql_statement)
        return True

    def check_user(self, username):
        sql_query = """
                    SELECT Id 
                    FROM Users
                    WHERE username like '{username}'
                """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        temp = self.cur.fetchone()
        print("sssssss")
        print(temp)
        print("sssssss")
        if temp is not None:
            return True
    # -----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
            SELECT Id,password
            FROM Users
            WHERE username like '{username}'
        """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        result = self.cur.fetchone()
        if result:
            Id = result[0]
            passwordstored = result[1]
            print(Id)
            print(passwordstored)

            sql_query = """
                    SELECT salt
                    FROM salts
                    WHERE Id = '{Id}'
                """
            sql_query = sql_query.format(Id=Id)
            test = self.execute(sql_query)

            salt = self.cur.fetchone()

            # If our query returns
            if salt:
                sql_query = """
                    SELECT 1
                    FROM Users
                    Where password like '{hash}' and username like '{username}'
                """
                concat = password+salt[0]
                hashobj = SHA256.new(data=concat.encode())
                hashs = hashobj.hexdigest()
                sql_query = sql_query.format(hash=hashs,username=username)
                self.execute(sql_query)
                if self.cur.fetchone():
                    #Get friends list function that returns array of friends
                    #pass in array of friends where [2,3] is 
                    self.fetch_friends_list(Id)
                    return True
                else:
                    return False
            else:
                return False

        else:
            return False

    
    # TESTING ISSUE - check_chatlink returns the right variable (could be returning a tuple or something)
    # Need to remove fl since it is unused
    #
    def fetch_friends_list(self, UID):
        sql_queary = """SELECT * FROM Users"""
        self.cur.execute(sql_queary)
        p = "<p>Friends:</p>"
        result = self.cur.fetchall()
        for row in result:
            check = self.check_chatlink(UID,row[0])
            if check is not None:
                p += "<a onclick=setUID(" + str(row[0]) + "," + str(UID) + ") href='/chatroom'> " + row[1] + "</a><br>"
            elif row[0] != UID:
                p += "<a onclick=setUID(" + str(row[0]) + "," + str(UID) + ") href='/addfriend'> add friend: " + row[1] + "</a><br>"
        p += """<script>
        function setUID(RID, SID){
            document.cookie = "RID="+RID
            document.cookie = "SID="+SID
        }
        </script>"""

        f = open("templates/temp.html", "w")
        f.write(p)
        f.close()

    #Extra stuff.

    #Creates two chatlink entries, one for UIDSEND,UIDRECIEVE, and one for UIDRECIEVE,UIDSEND
    # - only called if one of the two entries does not exist already in a table
    # Since this creates both entries, we can assume that if one exists, the other does as well
    
    def create_chatlink(self,UIDSEND,UIDRECIEVE):
        sql_cmd = """
                INSERT into chatlink(UIDSEND,UIDRECIEVE)
                VALUES({UIDSEND},{UIDRECIEVE})
            """
        sql_cmd = sql_cmd.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        self.execute(sql_cmd)
        self.commit()
        sql_cmd = """
                INSERT into chatlink(UIDSEND,UIDRECIEVE)
                VALUES({UIDRECIEVE},{UIDSEND})
            """
        sql_cmd = sql_cmd.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        self.execute(sql_cmd)
        self.commit()
        return True

    #Checks to see if a chatlink between sender and reciever exists in table, if it does not exist, create a new one
    #TESTING issue - might not return correctly
    def check_chatlink(self,UIDSEND,UIDRECIEVE):
        sql_query = """
                SELECT CID 
                FROM chatlink
                WHERE UIDSEND = {UIDSEND} AND UIDRECIEVE = {UIDRECIEVE}
            """

        sql_query = sql_query.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        self.execute(sql_query)
        chatID = self.cur.fetchone()
        print(chatID)
        print(UIDSEND,UIDRECIEVE)
        # If our query returns
        if chatID:
            return chatID[0]
        else:
            return None

    #Self explanatory
    def add_chatlog(self,CID,message):
        sql_cmd = """
                INSERT into chatlog
                VALUES({CID},'{message}',CURRENT_TIMESTAMP)
            """
        sql_cmd = sql_cmd.format(CID=CID,message=message)
        print(sql_cmd)
        self.execute(sql_cmd)
        self.commit()
        return True



    #SQL query takes in UID send and RECIEVE, joins the messages retrieved, then orders by time sent for chronological order
    #returns a tuple at the moment
    #TESTING issue - Might not return correctly
    def get_chatlog(self,UIDSEND,UIDRECIEVE):
        chatid1 = self.check_chatlink(UIDSEND,UIDRECIEVE)
        chatid2 = self.check_chatlink(UIDRECIEVE,UIDSEND)
        print("CIDS "+str(chatid1),str(chatid2))
        sql_cmd = """
                Select message,timestmp from chatlog
                Where chatlog.CID = (SELECT chatlink.CID from chatlink where UIDSEND = {UIDSEND} and UIDRECIEVE = {UIDRECIEVE})
                UNION
                Select message,timestmp from chatlog
                Where chatlog.CID = (SELECT chatlink.CID from chatlink where UIDSEND = {UIDRECIEVE} and UIDRECIEVE = {UIDSEND})
                ORDER BY timestmp
            """
        sql_cmd = sql_cmd.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        print(sql_cmd)
        self.execute(sql_cmd)
        j = self.cur.fetchall()
        messagelist = ''
        for line in j:
            messagelist += ","+line[0]
        print("getting chatlog")
        print(messagelist)
        return messagelist