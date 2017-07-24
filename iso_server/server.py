import tornado.ioloop
import tornado.web
import logging
import os, uuid
from tornado.options import define, options, parse_command_line
import isoforestcalls as iso
import subprocess

define("port", default=8888, help="run on the given port", type=int)

clients = dict()

__UPLOADS__ = "uploads/"

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("./html/index.html")

class SinglePoint(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        value = self.get_argument("SinglePoint", "")
        print(value)
        self.write(value)

class Upload(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        fh = open(__UPLOADS__ + cname, 'wb')
        fh.write(fileinfo['body'])
        print(__UPLOADS__ + cname)
        subprocess.call(['./scripts/submitsparkjob.sh', $ISOFOREST + "/" + __UPLOADS__ + cname])
        #iso.main(fileinfo['body'])
        self.render("./html/results.html")

class ImageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./html/results.html")


app = tornado.web.Application([
    ('/', IndexHandler),
    ('/getfile', Upload),
    (r"/img", ImageHandler),
    (r"/plots/(.*)", tornado.web.StaticFileHandler, {
        "path": "./plots"
    }),
    (r"/score_point", SinglePoint)
])

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
