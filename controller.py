'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file

import model

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    # Call the appropriate method
    return model.login_check(username, password)



#-----------------------------------------------------------------------------

@get('/chatroom')
def get_chatroom_controller():

    return model.chatroom()


# -----------------------------------------------------------------------------

@post('/chatroom')
def post_chatroom():

    # Handle the form processing
    message = request.forms.get('message')
    SID = request.forms.get('SID')
    RID = request.forms.get('RID')

    if message is not None:
        # mac = request.forms.get('mac')
        #friday Job 
        return model.store_message(message,'SID','RID')
    
    
    return model.get_message(SID, RID)
    # Call the appropriate method



# -----------------------------------------------------------------------------
@get('/addfriend')
def get_add_friend_controller():

    return model.add_friend_page()


# -----------------------------------------------------------------------------

@post('/addfriend')
def post_addfriend():
    SID = request.forms.get('SID')
    RID = request.forms.get('RID')
    message = request.forms.get('message')
    resType = request.forms.get('resType')
    return model.add_friend(SID, RID, message, resType)
# -----------------------------------------------------------------------------

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

@get('/Contact us')
def get_contact():
    '''
        get_about

        Serves the about page
    '''
    return model.contact()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
