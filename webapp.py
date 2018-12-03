import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import sqlite3
from sqlite3 import Error
import json


class WebApp(object):
    dbsqlite = 'data/db.sqlite3'
    dbjson = 'data/db.json'

    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('webapp', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )


########################################################################################################################
#   Utilities

    def set_user(self, username=None):
        if username == None:
            cherrypy.session['user'] = {'is_authenticated': False, 'username': ''}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username}


    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']


    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)


    def db_connection(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None


    def do_authenticationDB(self, usr, pwd):
        user = self.get_user()
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "select password from users where username == '{}'".format(usr)
        cur = db_con.execute(sql)
        row = cur.fetchone()
        if row != None:
            if row[0] == pwd:
                self.set_user(usr)
        db_con.close()


    def do_authenticationJSON(self, usr, pwd):
        user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                self.set_user(usr)
                break

    def register_userJSON(self, usr, pwd):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        dict_aux = {'username' : usr, 'password' : pwd}
        users.append(dict_aux)
        json.dump(db_json, open(WebApp.dbjson, 'w'))

    def fillInDB(self):
        db_json = json.load(open(WebApp.dbjson))
        professionals = db_json['enfermeiros'] + db_json['babysitter'] + db_json['fisioterapeutas'] + db_json['limpeza']

        for d in professionals:
            d['path'] = "http://placehold.it/400x250/000/fff"
            d['descricao'] = "Texto descritivo do profissional"
        json.dump(db_json, open(WebApp.dbjson, 'w'))


########################################################################################################################
#   Controllers

    @cherrypy.expose
    def index(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('index.html', tparams)


    @cherrypy.expose
    def about(self):
        tparams = {
            'title': 'About',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('about.html', tparams)

    @cherrypy.expose
    def cameras(self):
        tparams = {
            'title': 'Cameras',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('cameras.html', tparams)

    @cherrypy.expose
    def contact(self):
        tparams = {
            'title': 'Contact',
            'message': 'Your contact page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('contact.html', tparams)


    @cherrypy.expose
    def login(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('login.html', tparams)
        else:
            self.do_authenticationJSON(username, password)
            #self.do_authenticationDB(username, password)
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Login',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def register(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Register',
                'message': 'Register account.',
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('register.html', tparams)
        else:
            self.register_userJSON(username, password)
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Register',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('register.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def list(self):
        database = json.load(open(WebApp.dbjson))
        tparams = {
            'title': 'Listagem',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
            'database': database['users']
        }
        return self.render('people.html', tparams)

    @cherrypy.expose
    def enfermeiros(self):
        database = json.load(open(WebApp.dbjson))
        tparams = {
            'title': 'Enfermeiros',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
            'database': database['enfermeiros']
        }
        return self.render('professionals.html', tparams)

    @cherrypy.expose
    def fisioterapeutas(self):
        database = json.load(open(WebApp.dbjson))
        tparams = {
            'title': 'Fisioterapeutas',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
            'database': database['fisioterapeutas']
        }
        return self.render('professionals.html', tparams)

    @cherrypy.expose
    def babysitter(self):
        database = json.load(open(WebApp.dbjson))
        tparams = {
            'title': 'Babysitter',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
            'database': database['babysitter']
        }
        return self.render('professionals.html', tparams)

    @cherrypy.expose
    def limpeza(self):
        database = json.load(open(WebApp.dbjson))
        tparams = {
            'title': 'Limpeza',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
            'database': database['limpeza']
        }
        return self.render('professionals.html', tparams)

    @cherrypy.expose
    def professionals(self,dat,appt,name):
        user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == user['username']:
                serv_aux = u['servicos']
                serv_aux.append(name.replace('Contratar-','')+"-"+str(dat)+"-"+str(appt))
                break
        json.dump(db_json, open(WebApp.dbjson, 'w'))
        return self.list()

    @cherrypy.expose
    def hiredProfessionals(self):
        user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == user['username']:
                serv_aux = u['servicos'].copy()
                break

        listaAux=[]
        for u in serv_aux:
            f = u.split('-')
            for v in db_json['enfermeiros']:
                if(v['nome']==f[0]):
                    print("enfermeiro")
                    v['dataC'] = f[1]+"-"+f[2]+"-"+f[3]
                    v['horaC'] = f[4]
                    listaAux.append(v)
            for v in db_json['babysitter']:
                if(v['nome']==f[0]):
                    print("baby")
                    v['dataC'] = f[1]+"-"+f[2]+"-"+f[3]
                    v['horaC'] = f[4]
                    listaAux.append(v)
            for v in db_json['fisioterapeutas']:
                if(v['nome']==f[0]):
                    print("fisio")
                    v['dataC'] = f[1]+"-"+f[2]+"-"+f[3]
                    v['horaC'] = f[4]
                    listaAux.append(v)
            for v in db_json['limpeza']:
                if(v['nome']==f[0]):
                    print("limpeza")
                    v['dataC'] = f[1]+"-"+f[2]+"-"+f[3]
                    v['horaC'] = f[4]
                    listaAux.append(v)

        tparams = {
            'title': 'Profissionais contratados',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
            'database': listaAux
        }
        json.dump(db_json, open(WebApp.dbjson, 'w'))
        return self.render('hiredProfessionals.html', tparams)

    @cherrypy.expose
    def termination(self, password1 = None, password2 = None):
        print("Termination")
        tparams = {
            'title': 'Settings',
            'errors': False,
            'changed': False,
            'user': self.get_user(),
            'year': datetime.now().year,
        }

        user = self.get_user()
        print("user: ", user)
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']

        if password1 == password2:
            for d in users:
                if d['username'] == user['username']:
                    if d['password'] == password1:
                        print("encontrado")
                        users.remove(d)
                        json.dump(db_json, open(WebApp.dbjson, 'w'))
                        return self.logout()

        return self.render('settings.html', tparams)

    @cherrypy.expose
    def cancelarServico(self,name):
        user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == user['username']:
                serv_aux = u['servicos']
                break
        for u in serv_aux:
            f = u.split('-')
            if name.replace('Cancelar-','')==f[0]:
                print("aqui")
                serv_aux.remove(u)
        json.dump(db_json, open(WebApp.dbjson, 'w'))
        return self.hiredProfessionals()

    @cherrypy.expose
    def settings(self, currentPassword=None, newPassword1=None, newPassword2=None):
        tparams = {
            'title': 'Settings',
            'errors': False,
            'changed': False,
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        if currentPassword == None:
            return self.render('settings.html', tparams)
        else:
            if newPassword1 == newPassword2:
                user = self.get_user()['username']
                print("user",user)
                db_json = json.load(open(WebApp.dbjson))
                users = db_json['users']
                for d in users:
                    if d['username'] == user:
                        d['password'] = newPassword1
                        print("mudado")
                json.dump(db_json, open(WebApp.dbjson, 'w'))
                tparams = {
                    'title': 'Settings',
                    'errors': False,
                    'changed': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('settings.html', tparams)
            else:
                tparams = {
                    'title': 'Settings',
                    'errors': True,
                    'changed': False,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('settings.html', tparams)

    @cherrypy.expose
    def logout(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def signup(self):
        pass

    @cherrypy.expose
    def shut(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.quickstart(WebApp(), '/', conf)
