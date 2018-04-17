# -*- encoding: utf-8 -*-
"""
self = {}

boundary_str = b"\r\n" + b'-----ddd' + b'\r\n'
boundary_end = b"\r\n" + boundary_str + b'--' + b'\r\n'
bre = re.compile(b'(\r\n' + boundary_str + b'(?:--)?\r\n)')


def get_file_name(hd):
    return 'hahah' + hd


chunks = ['1,', '33']


msg_rmn = b''
real_msg = msg_rmn + b'chunk'
msg = b''
flg = 0


for chunk_virtual in bre.split(real_msg):
    msg += chunk_virtual
    if flg == 0:
        if b'\r\n\r\n' not in msg:
            continue
        else:
            hd, tr = msg.split(b'\r\n\r\n', 1)
            fn = get_file_name(hd)
            flg = 1
            self.file = open(fn, 'wb')
            msg = tr
    if flg == 1:
        if b'\r\n' not in msg:
            continue
        else:
            if boundary_str in msg:
                self.file.write(msg.split(boundary_str)[0])
                self.file.close()
                msg = b''
                flg = 0
            elif boundary_end in msg:
                self.file.write(msg.split(boundary_end)[0])
                self.file.close()
                msg = b''
                flg = 0
            elif len(msg[msg.rindex(b'\r\n'):]) <= len(boundary_end):
                self.file.write(msg[0: msg.rindex(b'\r\n')])
                msg = msg[msg.rindex(b'\r\n'):]
            else:
                self.file.write(msg)
                msg = b''


msg_rmn = msg
msg = b''
"""
import tornado.ioloop
import tornado.web
from tornado import options
from tornado.httpserver import HTTPServer


from urllib.parse import unquote


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

# def get_



def handle_payload(self, chunk):
    pass


@tornado.web.stream_request_body
class PUTHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.bytes_read = 0
        # self.redirect('/')


    def data_received(self, chunk):
        if self.bytes_read == 0:
            print(self.request.headers)
            # print(chunk)
        # print('get chunk')
        print(chunk)
        self.bytes_read += len(chunk)

    def post(self):
        # filename = unquote(filename)
        mtype = self.request.headers.get('Content-Type')
        # print('post "%s" "%s" %d bytes', 'file_name', mtype, self.bytes_read)
        # print(self.request.headers)
        self.write('OK')

    def get(self):
        self.write(page)

    def on_finish(self):
        print('finish.')


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(page)

    def post(self):
        # self.write(page)
        return


def make_app():
    return tornado.web.Application([
        (r"/up", PUTHandler),
        (r"/.*", IndexHandler)
    ], autoreload=True)


# curl -vX POST --data-binary @cache.zip http://192.168.1.200:8888
# url -vX POST --data-binary @cache.zip http://127.0.0.1:8888
if __name__ == "__main__":
    # Tornado configures logging.
    # options.parse_command_line()
    app = make_app()
    max_buffer_size = 10 * 1024 ** 5  # 4GB
    http_server = HTTPServer(
        app,
        max_buffer_size=max_buffer_size,
    )
    http_server.listen(8888)
    # app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
