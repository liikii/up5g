# -*- encoding: utf-8 -*-
"""
"""
from uuid import uuid4
import re

import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado import web


page = """<!DOCTYPE html>
<html>
<body>

<form action="/up" method="post" enctype="multipart/form-data">
  Select images: <input type="file" name="files" multiple/>
  <input type="submit" value='up it'>
</form>

<p>Try selecting more than one file when browsing for files.</p>

<p><strong>Note:</strong> The multiple attribute of the input tag is not supported in Internet Explorer 9 and earlier versions.</p>

</body>
</html>"""


def get_boundary(hd):
    ctp = hd.get('Content-Type', '')
    if ctp.startswith('multipart/form-data; boundary='):
        return ctp[30:].encode()


def get_file_name(hd):
    fn = str(uuid4()) + '.data'
    s = hd.decode('utf8')
    for ln in s.splitlines():
        if ln.startswith('Content-Disposition: form-data; '):
            try:
                fn = ln.split(';')[2].strip()[10:-1] or fn
            except IndexError:
                pass
    return fn


@tornado.web.stream_request_body
class PUTHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.bytes_read = 0
        self.rf = 1
        self.boundary_str = None
        self.boundary_end = None
        self.bre = None
        self.msg_rmn = b''
        self.file = None
        self.flg = 0
        super(PUTHandler, self).__init__(application, request, **kwargs)

    def initialize(self):
        self.bytes_read = 0
        boundary = get_boundary(self.request.headers)
        if boundary is not None:
            self.rf = 0
            self.boundary_str = b"\r\n--" + boundary + b'\r\n'
            self.boundary_end = b"\r\n--" + boundary + b'--' + b'\r\n'
            self.bre = re.compile(b'(\r\n--' + boundary + b'(?:--)?\r\n)')

    def data_received(self, chunk):
        if self.rf:
            return

        real_msg = self.msg_rmn + chunk
        msg = b''

        for chunk_virtual in self.bre.split(real_msg):
            msg += chunk_virtual
            if self.flg == 0:
                if b'\r\n\r\n' not in msg:
                    continue
                else:
                    hd, tr = msg.split(b'\r\n\r\n', 1)
                    fn = get_file_name(hd)
                    self.flg = 1
                    self.file = open(fn, 'wb')
                    msg = tr
            if self.flg == 1:

                if self.boundary_str in msg:
                    mhd, mtr = msg.split(self.boundary_str)
                    self.file.write(mhd)
                    self.file.close()
                    msg = mtr
                    self.flg = 0
                elif self.boundary_end in msg:
                    mhd, mtr = msg.split(self.boundary_end)
                    self.file.write(mhd)
                    self.file.close()
                    msg = mtr
                    self.flg = 0
                elif b'\r' in msg and len(msg[msg.rindex(b'\r'):]) < len(self.boundary_end):
                    self.file.write(msg[0: msg.rindex(b'\r')])
                    msg = msg[msg.rindex(b'\r'):]
                else:
                    self.file.write(msg)
                    msg = b''

        self.msg_rmn = msg

    def post(self):
        self.write('OK')

    def get(self):
        self.write(page)

    def on_finish(self):
        print('finish.')


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(page)

    def post(self):
        return


def make_app():
    return tornado.web.Application([
        (r"/up", PUTHandler),
        # (r"/?", IndexHandler),
        (r"/?()", web.StaticFileHandler, {"path": './static', 'default_filename': 'index.html'}),
        (r"/s/(.*)", web.StaticFileHandler, {"path": './static'})
    ], autoreload=True)


if __name__ == "__main__":
    app = make_app()
    max_buffer_size = 1024 ** 3 * 10  # 4GB
    http_server = HTTPServer(
        app,
        max_buffer_size=max_buffer_size,
    )
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()
