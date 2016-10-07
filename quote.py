
from google.appengine.ext import ndb

class Quote(ndb.Model):
    quote_text = ndb.StringProperty(indexed=False)
    author = ndb.StringProperty(indexed=True)
    category = ndb.StringProperty(indexed=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)