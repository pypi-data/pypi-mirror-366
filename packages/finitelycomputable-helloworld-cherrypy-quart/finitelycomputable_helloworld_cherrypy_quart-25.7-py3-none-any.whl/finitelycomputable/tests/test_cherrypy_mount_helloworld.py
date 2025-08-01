import cherrypy.test.helper
import pytest

from finitelycomputable import cherrypy_mount

class CherrypyMountTest(cherrypy.test.helper.CPWebCase):
    cherrypy.test.helper.CPWebCase.interactive = False

    def setup_server():
        cherrypy_mount.setup_server()
    setup_server = staticmethod(setup_server)

    def test_helloworld_cherrypy(self):
        self.getPage('/hello_world/')
        self.assertStatus('200 OK')
        self.assertInBody(b'says "hello, world"\n')
        self.assertInBody(b'CherryPy')

    def test_env_info(self):
        self.getPage('/env_info/')
        self.assertStatus('200 OK')
        self.assertInBody(b'finitelycomputable.helloworld_cherrypy')
        self.assertInBody(b'finitelycomputable.cherrypy_mount')

    def test_index(self):
        self.getPage('/')
        self.assertStatus('200 OK')
        self.assertInBody(b'finitelycomputable-helloworld-cherrypy')
        self.assertInBody(b'finitelycomputable.cherrypy_mount')
