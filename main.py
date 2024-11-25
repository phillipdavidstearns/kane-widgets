from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import os
import logging
import signal
from decouple import config

def launch_app():

  class DefaultHandler(RequestHandler):
    def prepare(self):
      self.set_status(404)

  class MainHandler(RequestHandler):
    async def get(self):
      self.render('index.html')
    async def post(self):
      try:
        timestamp = float(self.get_query_argument('timestamp'))
        logging.debug(f"Apply the timestamp value {timestamp} to the system time.")
        self.set_status(200)
        return
      except Exception as e:
        logging.warning(f"{repr(e)}")
        self.set_status(400)
        self.write({'details': repr(e)})
        return

  class TouchyHandler(RequestHandler):
    async def get(self):
      self.render('touchy.html')

  def make_app():
    path = os.path.dirname(os.path.abspath(__file__))
    
    settings = dict(
      template_path = os.path.join(path, 'templates'),
      static_path = os.path.join(path, 'static'),
      debug = True,
      websocket_ping_interval = 10
    )

    urls = [
      (r'/', MainHandler),
      (r'/touchy', TouchyHandler)
    ]

    return Application(urls, **settings)

  application = make_app()
  http_server = HTTPServer(application)
  http_server.listen(config('PORT', default=80, cast=int))
  main_loop = IOLoop.current()
  main_loop.start()

if __name__ == '__main__':

  def signalHandler(signum, frame):
    print()
    logging.warning('Caught termination signal: %s' % signum)
    shutdown(status=1)

  def shutdown(status=1):
    os._exit(status)

  signal.signal(signal.SIGTERM, signalHandler)
  signal.signal(signal.SIGHUP, signalHandler)
  signal.signal(signal.SIGINT, signalHandler)

  logging.basicConfig(
      level=10,
      format='[WIDGETS APP] - %(levelname)s | %(message)s'
    )

  try:
    launch_app()
  except Exception as e:
    logging.error('Uncaught while running main(): %s' % repr(e))
  finally:
    shutdown(0)