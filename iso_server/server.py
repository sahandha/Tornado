import tornado.ioloop
import tornado.web
import subprocess
import os
import motor.motor_tornado
from tornado import gen



__ROOT__     = os.path.join(os.path.dirname(__file__))
__IMAGES__   = os.path.join(os.path.dirname(__file__),"images/")
__UPLOADS__  = os.path.join(os.path.dirname(__file__),"uploads/")
__SCRIPTS__  = os.path.join(os.path.dirname(__file__),"scripts/")
__STATIC__   = os.path.join(os.path.dirname(__file__),"static/")
__TEMPLATE__ = os.path.join(os.path.dirname(__file__),"templates/")
__RESOURCE__ = os.path.join(os.path.dirname(__file__),"resources/")
__USERS__ = os.path.join(os.path.dirname(__file__),"users/")


db = motor.motor_tornado.MotorClient().IsolationForest

print(db)

@gen.coroutine
def Authenticate(username, password):
     userlookup = yield db.users.find({"username":username, "password":password}).to_list(length=1)
     return userlookup

def CreateUser(username, password,fullname,email):
    # insert user info into database
    db.users.insert_one({
    'username':username,
    'password':password,
    'fullname':fullname,
    'email':email,
    'projects':['default']
    })

    # create appropriate directories for each user
    userdir = __USERS__+"/"+username
    if not os.path.exists(userdir):
        os.makedirs(userdir)

@gen.coroutine
def getProjects(username):
    doc = yield db.users.find({"username":username}).to_list(length=1)
    return doc[0]["projects"]

@gen.coroutine
def Updatedb(username,field,newvalue):
    result = yield db.users.update_one({ "username":username }, { "$set" : {field:newvalue} })

'''
@gen.coroutine
def putPaths(username,project):
    basepath = __USERS__+username+"/"+project
    result = yield db.users.update_one({ "username":username },
    { "$set" :
        {project:{"imagepath":basepath+"/"+"images",
                  "treespath":basepath+"/"+"trees",
                  "uploadspath":basepath+"/"+"uploads"}}
         })
'''

def getPaths(username,project):
    basepath = __USERS__+username+"/"+project
    images  = basepath+"/"+"images"
    trees   = basepath+"/"+"trees"
    uploads = basepath+"/"+"uploads"
    return(images, trees, uploads)

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.current_user    = self.application.settings['current_user']
        self.projects        = self.application.settings['projects']
        self.current_project = self.application.settings['current_project']

    def get(self):
        if self.current_user == 'no_user':
            self.render('login.html',failmessage="")
        else:
            self.render('user_landing_page.html', username=self.current_user, projects=self.projects, current_project=self.current_project)

class LoginHandler(tornado.web.RequestHandler):
    def initialize(self, **configs):
        self.db = self.application.settings['db']
    @gen.coroutine
    def post(self):
        username = self.get_argument('lg_username')
        password = self.get_argument('lg_password')
        userlookup = yield Authenticate(username, password)

        if userlookup:
            projects = yield getProjects(username)
            self.application.settings['current_user'] = username
            self.application.settings['projects'] = projects
            self.current_user = username
            self.projects     = projects
            self.redirect('/')
        else:
            self.render('login.html',failmessage="Invalid username or password")

class LogoutHandler(tornado.web.RequestHandler):
    def initialize(self, **configs):
        self.application.settings['current_user'] = 'no_user'
        self.application.settings['current_project'] = 'default'
        self.current_user = self.application.settings['current_user']
    def get(self):
        self.redirect('/')

class RegisterationPage(tornado.web.RequestHandler):
    def get(self):
        self.render('register.html',failmessage='')

class RegistrationHandler(tornado.web.RequestHandler):

    def post(self):
        username = self.get_argument('reg_username')
        password = self.get_argument('reg_password')
        passwdco = self.get_argument('reg_password_confirm')
        email    = self.get_argument('reg_email')
        fullname = self.get_argument('reg_fullname')
        if password == passwdco:
            try:
                CreateUser(username, password,fullname,email)
            except:
                self.render('register.html',failmessage='Error creating user account')
            self.application.settings['current_user'] = username
            self.current_user = self.application.settings['current_user']
            self.redirect('/')
        else:
            self.render('register.html',failmessage='Password does not match')

class ForgotPasswordHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('forgot_password.html')

class ProjectLoader(tornado.web.RequestHandler):
    def initialize(self, **configs):
        self.current_user = self.application.settings['current_user']

    def get(self):
        self.application.settings['current_project'] = (self.request.uri).lstrip('/projectload')
        self.redirect('/')

class Upload(tornado.web.RequestHandler):
    def initialize(self, **configs):
        self.db = self.application.settings['db']
        self.current_user = self.application.settings['current_user']
        self.current_project = self.application.settings['current_project']
        self.projects = self.application.settings['projects']


    def post(self):
        project = self.get_argument('projectname')
        self.CreateProject(self.current_user,project)
        self.current_project = project
        imagespath, treespath, uploadspath = getPaths(self.current_user, self.current_project)

        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        #cname = str(uuid.uuid4()) + extn #this is to scramble the name of the file
        fh = open(uploadspath+"/"+fname, 'wb')
        fh.write(fileinfo['body'])
        fh.close()
        self.write("Data uploaded successfully")
        subprocess.call([__SCRIPTS__+'submitsparkjob.sh', __RESOURCE__+'iso_forest-master.zip', __ROOT__+'/train.py', uploadspath+"/"+fname, treespath])
        #subprocess.call([__SCRIPTS__+'submitsparkjob.sh', __ROOT__+'isoforestcalls.py', cname, __RESOURCE__+'iso_forest-master.zip'])
        self.get()
    def get(self):
        self.redirect('/')

    def CreateProject(self,username,project):
        projectdir = __USERS__+"/"+username+"/"+project
        useruploads=projectdir+"/uploads"
        if not os.path.exists(useruploads):
            os.makedirs(useruploads)

        userimages=projectdir+"/images"
        if not os.path.exists(userimages):
            os.makedirs(userimages)

        usertrees=projectdir+"/trees"
        if not os.path.exists(usertrees):
            os.makedirs(usertrees)

        self.application.settings["current_project"] = project
        self.projects.append(project)
        self.application.settings['projects'] = self.projects
        Updatedb(self.current_user,'projects', self.projects)
        #putPaths(self.current_user, project)

settings=dict(
    template_path=__TEMPLATE__,
    static_path=__STATIC__,
    current_user='no_user',
    projects=[],
    current_project='default',
    db=db,
    debug=True
)

application = tornado.web.Application([
    (r"/getfile", Upload),
    (r"/logout", LogoutHandler),
    (r"/login", LogoutHandler),
    (r"/logininfo", LoginHandler),
    (r"/registerinfo", RegistrationHandler),
    (r"/register", RegisterationPage),
    (r"/forgot_password", ForgotPasswordHandler),
    (r"/projectload.*", ProjectLoader),
    (r"/", MainHandler)
],**settings)

if __name__=="__main__":
    print("server running...")
    print("press ctrl+c to close.")
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
