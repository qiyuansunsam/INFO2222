import sqlite3


# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg=":memory:"):
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
            Id INT,
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.commit()
        # Add our admin user
        self.add_user('admin', admin_password, admin=1)
        self.add_user('t1', admin_password, admin=1)
        self.add_user('t2', admin_password, admin=1)
        self.add_user('t3', admin_password, admin=1)

    # -----------------------------------------------------------------------------
    # User handling
    # -----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, admin=0):
        sql_cmd = """
                INSERT INTO Users
                VALUES({id}, '{username}', '{password}', {admin})
            """

        self.id += 1
        sql_cmd = sql_cmd.format(id=self.id, username=username, password=password, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    # -----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT Id 
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """

        sql_query = sql_query.format(username=username, password=password)

        # If our query returns
        self.execute(sql_query)
        temp = self.cur.fetchone()
        if temp:
            UID = temp[0]
            self.fetch_friends_list([2, 3], UID)
            return True
        else:
            return False

    def fetch_friends_list(self, fl, UID):
        sql_queary = """SELECT * FROM Users"""
        self.cur.execute(sql_queary)
        p = "<p>Friends:</p>"
        result = self.cur.fetchall()
        print("")
        for row in result:
            if row[0] in fl:
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