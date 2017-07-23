
import tornado.ioloop
import tornado.web
import logging
import os, uuid
from tornado.options import define, options, parse_command_line



define("port", default=8888, help="run on the given port", type=int)

clients = dict()

__UPLOADS__ = "uploads/"

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class SecondPageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("test.html")

app = tornado.web.Application([
    ('/', IndexHandler),
    ('/anotherpage', SecondPageHandler),
])

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
