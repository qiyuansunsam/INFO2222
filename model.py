'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import sql
from Crypto.PublicKey import RSA

# Initialise our views, all arguments are defaults for the template
page_view = view.View()
sql_db = sql.SQLDatabase("samnchad.db")
#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index")

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords
        :: username :: The username
        :: password :: The password
        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds
    login = True

    login = sql_db.check_credentials(username, password)
    #if username != "admin": # Wrong Username
    #    err_str = "Incorrect Username"
    #    login = False

    #if password != "password": # Wrong password
    #   err_str = "Incorrect Password"
    #   login = False
    err_str = "Incorrect Password"
    if login:
        return page_view("temp", name=username)
    else:
        return page_view("invalid", reason=err_str)

#-----------------------------------------------------------------------------
def view_temp():
    return page_view("temp")

def register_form():
    return page_view("register", message="")

#-----------------------------------------------------------------------------
def register(username, password, publicKey):
    if sql_db.check_user(username): return "-1"
    id = sql_db.add_user(username, password)
    sql_db.fetch_friends_list(id)
    sql_db.addkey(id, publicKey)
    return str(id)

#-----------------------------------------------------------------------------


def chatroom():
    return page_view("chatroom")

#-----------------------------------------------------------------------------
def store_message(message,SID,RID):
    chatID = sql_db.check_chatlink(SID,RID)
    sql_db.add_chatlog(chatID,message)
    return page_view("chatroom")
#-----------------------------------------------------------------------------
def get_message(SID, RID):
    return sql_db.get_chatlog(SID,RID)
#-----------------------------------------------------------------------------
def add_friend_page():
    return page_view("addfriend")

#-----------------------------------------------------------------------------
## FriendReq table

# 1 2 "pub"
# 2 1 "SSK"
# 1 2 "confirmed"


def add_friend(SID, RID, message, resType):
    if (resType == "pull"):
        return sql_db.pull(SID,RID)
    if (resType == "rsaPublicKey"):
        rpk = "rsaPublicKey "+sql_db.pull_public_key(SID)
        sql_db.write_key(SID,RID,rpk)

        return ""
    if (resType == "SSK"):
        rpk = "SSK "+ sql_db.pull_public_key(SID)+":"+message
        sql_db.write_key(SID,RID,rpk)
        return ""
    if (resType == "confirmed"):
        sql_db.wipekeys(SID,RID)
        sql_db.create_chatlink(SID,RID)
        return ""
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.",
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


def contact():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("Contact us", garble=contact_garble())



# Returns a random string each time
def contact_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["contacted"]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)