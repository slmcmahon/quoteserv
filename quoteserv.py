import webapp2, jinja2, random, datetime, os, logging, time
from google.appengine.ext import ndb
from quote import Quote 
from utils import Utils 

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class AddQuote(webapp2.RequestHandler):
    def post(self):
        Utils.validate_login(self, '/allquotes')

        author = self.request.get('author')
        quote_text = self.request.get('quote_text')
        category = self.request.get('category')

        if author and quote_text and category:
            q = Quote(author = author, quote_text = quote_text, category = category)
            q.put()

        time.sleep(.5)
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

        time.sleep(.5)
        self.redirect('/allquotes', True)

    def get(self):

        if self.request.get('json') == 'true':
            template_name = 'allquotes.json'
            content_type = 'application/json'
        else:
            template_name = 'allquotes.html'
            content_type = 'text/html'
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
        
        qry = Quote.query().order(Quote.date_added)
        quotes = qry.fetch()

        template_values = {
            'quotes': quotes,
            'key': key,
            'quote_text': quote_text,
            'author': author,
            'category': category
        }

        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.headers['Content-Type'] = content_type
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
            rnd = random.SystemRandom()
            quote = qry.fetch(offset = rnd.randint(1, count) - 1)[0]
            quote_text = quote.quote_text
            quote_author = quote.author
            quote_category = quote.category

        if self.request.get('json') == 'true':
            use_xml = True
            template_name = 'quote.json'
            content_type = 'application/json'

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

        time.sleep(.5)
        self.redirect('/allquotes', True)



app = webapp2.WSGIApplication([
    ('/', RandomQuote),
    ('/allquotes', AllQuotes),
    ('/addquote', AddQuote),
    ('/deletequote', DeleteQuote)
], debug=True)
