import sqlite3
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

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
        self.conn = sqlite3.connect(database_arg,timeout=10)
        self.cur = self.conn.cursor()

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

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        #self.execute("DROP TABLE IF EXISTS Users")
        #self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.commit()

        # Add our admin user
        self.add_user('admin', admin_password, admin=1)

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
            Id INTEGER FOREIGN KEY REFERECNES Users(Id)
            salt TEXT);
            """)
        self.commit()


    #Creates two chatlink entries, one for UIDSEND,UIDRECIEVE, and one for UIDRECIEVE,UIDSEND
    # - only called if one of the two entries does not exist already in a table
    # Since this creates both entries, we can assume that if one exists, the other does as well
    
    def create_chatlink(self,UIDSEND,UIDRECIEVE):
        sql_cmd = """
                INSERT into chatlink(UIDSEND,UIDRECIEVE)
                VALUES({UIDSEND},{UIDRECIEVE})
            """
        sql_cmd = sql_cmd.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        self.exectue(sql_cmd)
        self.commit()
        sql_cmd = """
                INSERT into chatlink(UIDSEND,UIDRECIEVE)
                VALUES({UIDRECIEVE},{UIDSEND})
            """
        sql_cmd = sql_cmd.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        self.exectue(sql_cmd)
        self.commit()
        return True

    #Checks to see if a chatlink between sender and reciever exists in table, if it does not exist, create a new one
    def check_chatlink(self,UIDSEND,UIDRECIEVE):

        sql_query = """
                SELECT 1 
                FROM chatlink
                WHERE UIDSEND = '{UIDSEND}' AND UIDRECIEVE = '{UIDRECIEVE}'
            """

        sql_query = sql_query.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        self.execute(sql_query)
        # If our query returns
        if cur.fetchone():
            return True
        else:
            self.create_chatlink(UIDSEND,UIDRECIEVE)
            return False

    #Self explanatory
    def add_chatlog(self,CID,message):
        sql_cmd = """
                INSERT into chatlog
                VALUES({CID},{message},CURRENT_TIMESTAMP)
            """
        sql_cmd = sql_cmd.format(CID=CID,message=message)
        self.execute(sql_cmd)
        self.commit()
        return True



    #SQL query takes in UID send and RECIEVE, joins the messages retrieved, then orders by time sent for chronological order
    #returns a tuple at the moment
    def get_chatlog(self,UIDSEND,UIDRECIEVE):
        sql_cmd = """
                Select message,timestmp from chatlog
                Where chatlog.CID = (SELECT chatlink.CID from chatlink where UIDSEND = '{UIDSEND}}' and UIDRECIEVE = '{UIDRECIEVE}}')
                UNION
                (
                Select message,timestmp from chatlog
                Where chatlog.CID = (SELECT chatlink.CID from chatlink where UIDSEND = '{UIDRECIEVE}' and UIDRECIEVE = '{UIDSEND}}')
                )
                ORDER BY timestmp asc;
            """
        sql_cmd = sql_cmd.format(UIDSEND=UIDSEND, UIDRECIEVE=UIDRECIEVE)
        chats = self.execute(sql_cmd)
        for x in chats:
            print(x)
        return chats

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    #NEED TO EDIT TO ADD SALT!!!
    def add_user(self, username, password, admin=0):

        
        salt = get_random_bytes(16)
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
        Id = result[0]

        sql_cmd = """
            INSERT INTO salts
            VALUES('{Id}','{salt}')
        
        """

        sql_cmd=sql_cmd.format(Id=Id,salt=salt)
        self.execute(sql_cmd)
        self.commit()

        return True

    #-----------------------------------------------------------------------------

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
        Id = result[0]
        password = result[1]

        sql_query = """
                SELECT salt
                FROM salts
                WHERE Id = '{Id}''
            """
        sql_query = sql_query.format(Id=Id)
        self.execute(sql_query)
        salt = self.cur.fetchone()[0]
        # If our query returns
        if salt:
            sql_query = """
                SELECT 1
                FROM Users
                Where password like '{hash}'
            """
            concat = password+salt
            hashobj = SHA256.new(data=concat.encode())
            hashs = hashobj.hexdigest()
            sql_query = sql_query.format(hash=hashs)
            self.execute(sql_query)
            if self.conn.fetchone():
                return True
            else:
                return False
        else:
            return False
