
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
    return db.GqlQuery("SELECT * FROM Blog order by created desc LIMIT " + str(limit) + " OFFSET " + str(offset))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class ViewPostHandler(Handler):
    def get(self, id):
        # id = self.request.get("id")
        id = int(id)

        called_entry = Blog.get_by_id(id, parent=None)

        if called_entry:
            self.render("singlepost.html", title = called_entry.title, entry = called_entry.entry)
        else:
            self.redirect("/blog")

class AddPosts(Handler):
    def render_entry(self, title="", entry="", error=""):
        self.render("entry.html", title = title, entry=entry, error=error)

    def get(self):
        self.render_entry()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")
        if title and entry:
            blog = Blog(title = title, entry = entry)
            blog.put()
            self.redirect("/blog")
        else:
            error = "You need to enter BOTH a title and a post to play with the K-BLOG!"
            self.render_entry(title, entry, error)

class Index(Handler):
        def render_blog(self):
            current = get_posts(5, 0)
            # more = next()
            self.render("blog.html", current = current)

        def get(self):
            self.render_blog()

        # def next(self):
        #     if Blog.count() > 5:
        #         next = get_posts(5, (page-1)*5)
        #         return next


app = webapp2.WSGIApplication([
    ('/blog', Index),
    ('/newpost', AddPosts),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
