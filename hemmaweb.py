# -*- coding: utf-8 -*-

import web
import os
import db
from jose import jwt

web.config.debug = False

render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/login', 'login',
    '/logout', 'logout',
    '/sensors', 'sensors',
    '/(js|css)/(.*)', 'static',
    '/images/(.*)', 'images',
)


class images:
    def GET(self, name):
        ext = name.split(".")[-1]  # Gather extension

        cType = {
            "png": "images/png",
            "jpg": "images/jpeg",
            "gif": "images/gif",
            "ico": "images/x-icon"}

        if name in os.listdir('images'):  # Security
            web.header("Content-Type", cType[ext])  # Set the Header
            return open('images/%s' % name, "rb").read()  # Notice 'rb' for reading images
        else:
            raise web.notfound()


def notLogdeIn():
    token = web.cookies().get('akey')
    if token is None:
        return True

    if jwt.decode(token, 'Hemligt', algorithms=['HS256'])['logedin'] == 'true':
        return False
    else:
        return True


class login:
    def GET(self):

        return render.login()

    def POST(self):
        s = web.input(user=None, password=None)

        if db.verifyUser(s.user, s.password):
            token = jwt.encode({'user': s.user, 'logedin': 'true'}, 'Hemligt', algorithm='HS256')
            web.setcookie('akey', token, 864000)
            raise web.seeother('/')

        return render.login()


# This code is for serving static files
class static:
    def GET(self, media, file):
        try:
            f = open(media+'/'+file, 'r')
            return f.read()
        except:
            return ''  # you can send an 404 error here if you want


class sensors:
    def GET(self):
        if notLogdeIn():
            raise web.seeother('/login')
        else:
            return db.getSensorsDataJSON()


class index:
    def GET(self):
        if notLogdeIn():
            raise web.seeother('/login')
        else:
            return render.index()

    def POST(self):
        # TODO check if logged in
        s = web.input(lamp=None, op=None, dimmerLevel=None)

        if s.lamp == "0":
            if s.op == "on":
                # ser.write(s.dimmerLevel)
                message_queue.put(s.dimmerLevel)
                print 'Set dimmer to level ' + s.dimmerLevel

            if s.op == "off":
                # ser.write('0')
                print 'Turn dimmer off'

        if s.lamp == "1":
            if s.op == "on":
                # ser.write('18')
                print 'Turn lamp 1 on'

            if s.op == "off":
                # ser.write('17')
                print 'Turn lamp 1 off'

        if s.lamp == "2":
            if s.op == "on":
                # ser.write('20')
                print 'Turn lamp 2 on'

            if s.op == "off":
                # ser.write('19')
                print 'Turn lamp 2 off'

        return


class logout:
    def GET(self):
        # just overwrite the key in the coockie
        web.setcookie('akey', 'logout', 1)
        return render.logout()


def start_web(w_queue):
    app = web.application(urls, globals())
    app.run()

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()