#!/usr/bin/python
# The original code for this script was borrowed from the internet. When I find where I got it from,
# I'll credit the original author

import cgi
import json
import mimetypes
import os
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


CWD = os.path.abspath('.')
PORT = os.environ.get('PORT', 8084)


class MyHandler(BaseHTTPRequestHandler):

    def pretty_json_dump(self, data):
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def do_GET(self):
        try:
            url_parts = urlparse.urlparse(self.path)

            if url_parts.path == '/':
                with open(os.curdir + os.sep + 'index.html') as requested_file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(requested_file.read())
            elif url_parts.path == '/list':
                # Read data folder for files, optionally filtering to the requested type
                files = os.listdir(CWD + '/data')

                query = urlparse.parse_qs(url_parts.query)
                if query.get('type'):
                    files = filter(lambda f: f.endswith(query['type'][0]), files)

                out_data = []
                for available_file in sorted(files):
                    out_data.append({
                        'filename': available_file,
                        'url': 'http://localhost:{}/data/{}'.format(PORT, available_file)
                    })

                content = self.pretty_json_dump(out_data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            elif url_parts.path == '/redirect':
                self.send_response(302)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', 0)
                self.send_header('Location', '/list')
                self.end_headers()
            elif url_parts.path.endswith(".html"):
                # Serve up the requested HTML page
                with open(os.curdir + os.sep + url_parts.path) as requested_file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(requested_file.read())
            else:
                # Asked for a specific data file
                with open(os.path.join(CWD, url_parts.path[1:]), 'rb') as requested_file:
                    content = requested_file.read()

                query = urlparse.parse_qs(url_parts.query)
                if query.get('octet'):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    mimetype = mimetypes.guess_type(url_parts.path[1:])
                    self.send_response(200)
                    self.send_header('Content-type', mimetype[0])
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)

        except IOError as e:
            print e
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            url_parts = urlparse.urlparse(self.path)
            if url_parts.path == '/upload':
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile,
                                          headers=self.headers, # headers_,
                                          environ={'REQUEST_METHOD': 'POST'})
                else:
                    raise Exception("Unexpected POST request")

                fs_up = fs['upfile']
                filename = os.path.split(fs_up.filename)[1] # strip the path, if it presents
                fullname = os.path.join(CWD + '/uploads/', filename)

                if os.path.exists(fullname):
                    fullname_test = fullname + '.copy'
                    i = 0
                    while os.path.exists(fullname_test):
                        fullname_test = "%s.copy(%d)" % (fullname, i)
                        i += 1
                    fullname = fullname_test

                if not os.path.exists(fullname):
                    with open(fullname, 'wb') as o:
                        o.write(fs_up.file.read())

                content = self.pretty_json_dump({'location': os.path.split(fullname)[1]})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
        except Exception as e:
            print e
            self.send_error(404, 'POST to "%s" failed: %s' % (self.path, str(e)))

def main():
    try:
        server = HTTPServer(('', PORT), MyHandler)
        print 'started httpserver on {}...'.format(PORT)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()
