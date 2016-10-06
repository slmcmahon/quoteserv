import webapp2
import jinja2
import random
import datetime
import os
import logging
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Quote(ndb.Model):
    quote_text = ndb.StringProperty(indexed=False)
    author = ndb.StringProperty(indexed=True)
    category = ndb.StringProperty(indexed=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        c = Quote()
        self.response.out.write(c.show())

class AddQuote(webapp2.RequestHandler):
    def post(self):
        Utils.validate_login(self, '/allquotes')

        author = self.request.get('author')
        quote_text = self.request.get('quote_text')
        category = self.request.get('category')

        if author and quote_text and category:
            q = Quote(author = author, quote_text = quote_text, category = category)
            q.put()
        self.redirect('/allquotes', True)

class AllQuotes(webapp2.RequestHandler):
    def post(self):
        Utils.validate_login(self, '/allquotes')

        key = ndb.Key(urlsafe=self.request.get('key'))
        qry = Quote.query(ancestor=key)
        q = qry.fetch(1)[0]

        q.author = self.request.get('author')
        q.quote_text = self.request.get('quote_text')
        q.category = self.request.get('category')
        q.date_added = datetime.datetime.now()
        q.put()

        self.redirect('/allquotes', True)

    def get(self):
        Utils.validate_login(self, '/allquotes')

        quote_text = ''
        author = ''
        category = ''

        key = self.request.get('key')
        if key:
            k = ndb.Key(urlsafe=key)
            qry = Quote.query(ancestor=k)
            q = qry.fetch(1)[0]
            quote_text = q.quote_text
            author = q.author
            category = q.category
        
        qry = Quote.query()#.order('-date_added')
        quotes = qry.fetch()

        template_values = {
            'quotes': quotes,
            'key': key,
            'quote_text': quote_text,
            'author': author,
            'category': category
        }

        template = JINJA_ENVIRONMENT.get_template('allquotes.html')
        self.response.write(template.render(template_values))


class RandomQuote(webapp2.RequestHandler):
    def get(self):
        use_xml = False
        template_name = 'quote.html'
        content_type = 'text/html'

        qry = Quote.query()
        count = qry.count(limit=None)

        if count == 0:
            quote_text = 'No quote found'
            quote_author = 'nobody'
            quote_category = 'none'
        else:
            rnd = random.randint(1, count)
            quote = qry.fetch(offset = rnd-1)
            quote_text = quote.quote_text
            quote_author = quote.author
            quote_category = quote.category

        if self.request.get('xml') == 'true':
            use_xml = True
            template_name = 'quote.xml'
            content_type = 'text/xml'

        template_values = {
            'quote_text': quote_text,
            'author': quote_author,
            'category': quote_category
        }

        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.headers['Content-Type'] = content_type
        self.response.write(template.render(template_values))

class DeleteQuote(webapp2.RequestHandler):
    def get(self):
        Utils.validate_login(self, '/deletequote?key=%(key)s' % { 'key': self.request.get('key') })
        # retrieve the quote associated with the given key and zap it.
        key = ndb.Key(urlsafe=self.request.get('key'))
        key.delete()

        self.redirect('/allquotes', True)

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

app = webapp2.WSGIApplication([
    ('/', RandomQuote),
    ('/allquotes', AllQuotes),
    ('/addquote', AddQuote),
    ('/deletequote', DeleteQuote)
], debug=True)
