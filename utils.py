
from google.appengine.api import users

class Utils(object):
    # sender is the class that called this.  We need this
    # to actually do the redirect.  Maybe later I'll return the
    # responsibility back to the caller in order to reduce the
    # number of arguments.  don't really like this -- but still learning.
    def validate_login(caller, uri):
        user = users.get_current_user()
        if not user or not users.is_current_user_admin():
            caller.redirect(users.create_login_url(uri))
            return

    validate_login = staticmethod(validate_login)