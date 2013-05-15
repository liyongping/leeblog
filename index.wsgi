import sae

from app import WsgiApplication

app = WsgiApplication()

application = sae.create_wsgi_app(app)

















