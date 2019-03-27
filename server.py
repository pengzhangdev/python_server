#!/usr/bin/env python
#coding=utf-8

__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]


import os, sys, platform
import posixpath
import BaseHTTPServer
from SocketServer import ThreadingMixIn
import threading
import urllib, urllib2
import cgi
import shutil
import mimetypes
import re
import time
import commands
import datetime

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO


class Clean:
  def __init__(self, file_url):
    self.file_url = file_url
  def delfile(self):
    f =  list(os.listdir(self.file_url))
    print("%s\n  start clean file...." % self.file_url)
    for i in range(len(f)):
      filedate = f[i][:14]

      if f[i].endswith('.py'):
        continue

      #time1 = datetime.datetime.fromtimestamp(filedate).strftime('%Y%m%d%H%M%S')
      time1 = time.mktime(time.strptime(filedate, '%Y%m%d%H%M%S'))
      date1 = time.time()

      num1 =(date1 - time1)/60/60/24
      if num1 >= 10:
        try:
          p = os.path.join(self.file_url, f[i])
          if os.path.isdir(p):
            shutil.rmtree(p)
          else:
            os.remove(p)

          print(u"remove file：%s ： %s" %  (time1, f[i]))
        except Exception as e:
          print(e)
      else:
        print("......")


def showTips():
  print ""
  print '----------------------------------------------------------------------->> '
  try:
    port = int(sys.argv[1])
  except Exception, e:
    print '-------->> Warning: Port is not given, will use deafult port: 8080 '
    print '-------->> if you want to use other port, please execute: '
    print '-------->> python SimpleHTTPServerWithUpload.py port '
    print "-------->> port is a integer and it's range: 1024 < port < 65535 "
    port = 8080

  if not 1024 < port < 65535: port = 8080
  # serveraddr = ('', port)
  print '-------->> Now, listening at port ' + str(port) + ' ...'
  osType = platform.system()
  if osType == "Linux":
    print '-------->> You can visit the URL:   http://127.0.0.1:' +str(port)
  print '----------------------------------------------------------------------->> '
  print ""
  return ('', port)

serveraddr = showTips()

def sizeof_fmt(num):
  for x in ['bytes','KB','MB','GB']:
    if num < 1024.0:
      return "%3.1f%s" % (num, x)
    num /= 1024.0
  return "%3.1f%s" % (num, 'TB')

def modification_date(filename):
  # t = os.path.getmtime(filename)
  # return datetime.datetime.fromtimestamp(t)
  return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(filename)))

class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  """Simple HTTP request handler with GET/HEAD/POST commands.

  This serves files from the current directory and any of its
  subdirectories. The MIME type for files is determined by
  calling the .guess_type() method. And can reveive file uploaded
  by client.

  The GET/HEAD/POST requests are identical except that the HEAD
  request omits the actual contents of the file.

  """

  server_version = "SimpleHTTPWithUpload/" + __version__

  def do_GET(self):
    """Serve a GET request."""
    # print "....................", threading.currentThread().getName()
    f = self.send_head()
    if f:
      self.copyfile(f, self.wfile)
      f.close()

  def do_HEAD(self):
    """Serve a HEAD request."""
    f = self.send_head()
    if f:
      f.close()

  def do_POST(self):
    """Serve a POST request."""
    r, info = self.deal_post_data()
    print r, info, "by: ", self.client_address
    f = StringIO()
    f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
    if r:
      f.write('<script language="javascript" type="text/javascript"> ')
      f.write("window.location.href='%s';" % info)
      f.write('</script>')
    else:
      f.write("<html>\n<title>Upload Result Page</title>\n")
      f.write("<body>\n<h2>Upload Result Page</h2>\n")
      f.write("<hr>\n")
      if r:
        f.write("<strong>Success:</strong>")
      else:
        f.write("<strong>Failed:</strong>")
        f.write(info)
        f.write("<br><a href=\"%s\">back</a>" % self.headers['referer'])
        f.write("<hr><small>Powered By: bones7456, check new version at ")
        f.write("<a href=\"http://li2z.cn/?s=SimpleHTTPServerWithUpload\">")
        f.write("here</a>.</small></body>\n</html>\n")
    length = f.tell()
    f.seek(0)
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.send_header("Content-Length", str(length))
    self.end_headers()
    if f:
      self.copyfile(f, self.wfile)
      f.close()

  def deal_post_data(self):
    clean = Clean(os.getcwd())
    clean.delfile()
    boundary = self.headers.plisttext.split("=")[1]
    remainbytes = int(self.headers['content-length'])
    line = self.rfile.readline()
    remainbytes -= len(line)
    if not boundary in line:
      return (False, "Content NOT begin with boundary")
    line = self.rfile.readline()
    remainbytes -= len(line)
    #fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
    fn = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if not fn:
      return (False, "Can't find out file name...")
    path = self.translate_path(self.path)
    osType = platform.system()
    basename = fn
    fn = os.path.join(path, fn)

    while os.path.exists(fn):
      fn += "_"

    basename = os.path.basename(fn)
    line = self.rfile.readline()
    remainbytes -= len(line)
    line = self.rfile.readline()
    remainbytes -= len(line)
    try:
      out = open(fn, 'wb')
    except IOError:
      return (False, "Can't create file to write, do you have permission to write?")

    preline = self.rfile.readline()
    remainbytes -= len(preline)
    while remainbytes > 0:
      line = self.rfile.readline()
      remainbytes -= len(line)
      if boundary in line:
        preline = preline[0:-1]
        if preline.endswith('\r'):
          preline = preline[0:-1]
        out.write(preline)
        out.close()
        # call process to convert the uploaded file
        commands.getstatusoutput("chkbugreport --no-limit -ml:{} -sl:{}".format(basename, basename))

        return (True, "%s_out/index.html" % basename)
      else:
        out.write(preline)
        preline = line

    return (False, "Unexpect Ends of data.")

  def send_head(self):
    """Common code for GET and HEAD commands.

    This sends the response code and MIME headers.

    Return value is either a file object (which has to be copied
    to the outputfile by the caller unless the command was HEAD,
    and must be closed by the caller under all circumstances), or
    None, in which case the caller has nothing further to do.

    """
    path = self.translate_path(self.path)
    f = None
    if os.path.isdir(path):
      if not self.path.endswith('/'):
        # redirect browser - doing basically what apache does
        self.send_response(301)
        self.send_header("Location", self.path + "/")
        self.end_headers()
        return None
      for index in "index.html", "index.htm":
        index = os.path.join(path, index)
        if os.path.exists(index):
          path = index
          break
      else:
        return self.list_directory(path)
    ctype = self.guess_type(path)
    try:
      # Always read in binary mode. Opening files in text mode may cause
      # newline translations, making the actual size of the content
      # transmitted *less* than the content-length!
      f = open(path, 'rb')
    except IOError:
      self.send_error(404, "File not found")
      return None
    self.send_response(200)
    self.send_header("Content-type", ctype)
    fs = os.fstat(f.fileno())
    self.send_header("Content-Length", str(fs[6]))
    self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
    self.end_headers()
    return f

  def list_directory(self, path):
    """Helper to produce a directory listing (absent index.html).

    Return value is either a file object, or None (indicating an
    error). In either case, the headers are sent, making the
    interface the same as for send_head().

    """
    try:
      list = os.listdir(path)
    except os.error:
      self.send_error(404, "No permission to list directory")
      return None
    list.sort(key=lambda a: a.lower())
    f = StringIO()
    displaypath = cgi.escape(urllib.unquote(self.path))
    f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
    f.write("<html>\n<title>A simple http server</title>\n")



    # f.write("<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
    # f.write("<input name=\"file\" type=\"file\"/>")
    # f.write("<input type=\"submit\" value=\"upload\"/>")
    # f.write("              ")
    # f.write("<input type=\"button\" value=\"HomePage\" onClick=\"location='/'\">")
    # f.write("</form>\n")

    f.write("""<head>
    <script type="text/javascript">""");
    f.write("""function fileSelected() {
        var file = document.getElementById('fileToUpload').files[0];
        if (file) {
          var fileSize = 0;
          if (file.size > 1024 * 1024)
            fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString() + 'MB';
          else
            fileSize = (Math.round(file.size * 100 / 1024) / 100).toString() + 'KB';

          document.getElementById('fileName').innerHTML = 'Name: ' + file.name;
          document.getElementById('fileSize').innerHTML = 'Size: ' + fileSize;
          document.getElementById('fileType').innerHTML = 'Type: ' + file.type;
        }
      }""")

    f.write("""function uploadFile() {
        var fd = new FormData();
        fd.append("fileToUpload", document.getElementById('fileToUpload').files[0]);
        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener("progress", uploadProgress, false);
        xhr.addEventListener("load", uploadComplete, false);
        xhr.addEventListener("error", uploadFailed, false);
        xhr.addEventListener("abort", uploadCanceled, false);
        xhr.open("POST", "/");
        xhr.send(fd);
      }
    """)

    f.write("""function uploadProgress(evt) {
        if (evt.lengthComputable) {
          var percentComplete = Math.round(evt.loaded * 100 / evt.total);
          document.getElementById('progressNumber').innerHTML = percentComplete.toString() + '%';
        }
        else {
          document.getElementById('progressNumber').innerHTML = '无法计算';
        }
      }
    """)

    f.write("""function uploadComplete(evt) {
        /* 当服务器响应后，这个事件就会被触发 */
        alert(evt.target.responseText);
      }

      function uploadFailed(evt) {
        alert("Failed to upload");
      }""")


    f.write("""function uploadCanceled(evt) {
        alert("Connection fialed");
      }
    """)

    f.write("""</script>
    </head>""");
    f.write("<body>\n<h2>Tasks:</h2>\n")
    f.write("<hr>\n")
    f.write("""<form id="form1" enctype="multipart/form-data" method="post" action="Upload.aspx">
    <div class="row">
      <label for="fileToUpload">Select a File to Upload</label><br />
      <input type="file" name="fileToUpload" id="fileToUpload" onchange="fileSelected();"/>
    </div>
    <div id="fileName"></div>
    <div id="fileSize"></div>
    <div id="fileType"></div>
    <div class="row">
      <input type="button" onclick="uploadFile()" value="Upload" />
    </div>
    <div id="progressNumber"></div>
  </form>
    """)
    f.write("<hr>\n<ul>\n")
    for name in list:
      if not name.endswith(".html"):
          continue
      fullname = os.path.join(path, name)
      colorName = displayname = linkname = name
      # Append / for directories or @ for symbolic links
      if os.path.isdir(fullname):
        colorName = '<span style="background-color: #CEFFCE;">' + name + '/</span>'
        displayname = name
        linkname = name + "/"
      if os.path.islink(fullname):
        colorName = '<span style="background-color: #FFBFFF;">' + name + '@</span>'
        displayname = name
        # Note: a link to a directory displays with @ and links with /
      filename = os.getcwd() + '/' + displaypath + displayname
      f.write('<table><tr><td width="60%%"><a href="%s">%s</a></td><td width="20%%">%s</td><td width="20%%">%s</td></tr>\n'
          % (urllib.quote(linkname), colorName,
            sizeof_fmt(os.path.getsize(filename)), modification_date(filename)))
    f.write("</table>\n<hr>\n</body>\n</html>\n")
    length = f.tell()
    f.seek(0)
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.send_header("Content-Length", str(length))
    self.end_headers()
    return f

  def translate_path(self, path):
    """Translate a /-separated PATH to the local filename syntax.

    Components that mean special things to the local file system
    (e.g. drive or directory names) are ignored. (XXX They should
    probably be diagnosed.)

    """
    # abandon query parameters
    path = path.split('?',1)[0]
    path = path.split('#',1)[0]
    path = posixpath.normpath(urllib.unquote(path))
    words = path.split('/')
    words = filter(None, words)
    path = os.getcwd()
    for word in words:
      drive, word = os.path.splitdrive(word)
      head, word = os.path.split(word)
      if word in (os.curdir, os.pardir): continue
      path = os.path.join(path, word)
    return path

  def copyfile(self, source, outputfile):
    """Copy all data between two file objects.

    The SOURCE argument is a file object open for reading
    (or anything with a read() method) and the DESTINATION
    argument is a file object open for writing (or
    anything with a write() method).

    The only reason for overriding this would be to change
    the block size or perhaps to replace newlines by CRLF
    -- note however that this the default server uses this
    to copy binary data as well.

    """
    shutil.copyfileobj(source, outputfile)

  def guess_type(self, path):
    """Guess the type of a file.

    Argument is a PATH (a filename).

    Return value is a string of the form type/subtype,
    usable for a MIME Content-type header.

    The default implementation looks the file's extension
    up in the table self.extensions_map, using application/octet-stream
    as a default; however it would be permissible (if
    slow) to look inside the data to make a better guess.

    """

    base, ext = posixpath.splitext(path)
    if ext in self.extensions_map:
      return self.extensions_map[ext]
    ext = ext.lower()
    if ext in self.extensions_map:
      return self.extensions_map[ext]
    else:
      return self.extensions_map['']

  if not mimetypes.inited:
    mimetypes.init() # try to read system mime.types
  extensions_map = mimetypes.types_map.copy()
  extensions_map.update({
    '': 'application/octet-stream', # Default
    '.py': 'text/plain',
    '.c': 'text/plain',
    '.h': 'text/plain',
    })

class ThreadingServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
  pass

def test(HandlerClass = SimpleHTTPRequestHandler,
    ServerClass = BaseHTTPServer.HTTPServer):
  BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
  # test()

  #单线程
  # srvr = BaseHTTPServer.HTTPServer(serveraddr, SimpleHTTPRequestHandler)

  #多线程
  print("Start clean data... ")
  clean = Clean(os.getcwd())
  clean.delfile()
  print("Start service ...")
  srvr = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)

  srvr.serve_forever()
