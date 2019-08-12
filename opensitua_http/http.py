# -----------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        http.py.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     28/07/2018
# -----------------------------------------------------------------------------
from .filesystem import *
from .strings import *
from jinja2 import Environment, FileSystemLoader
import os,sys,math
import json,base64, urllib
from cgi import FieldStorage
from builtins import str as unicode
import sqlite3


def urlencode(s):
    return urllib.quote(s)

def urldecode(s):
    return urllib.unquote(s).decode('utf8')


class Form:
    """
    Form
    """
    def __init__(self, environ):
        try:
            form = get_post_form(environ)
            self.form = {}
            for key in form:
                value = form.getvalue(key)
                value = urllib.unquote(value).decode('utf8')
                self.form[key] = value
        except:
            _environ = {}
            for key in environ:
                value = environ[key]
                value = urllib.unquote(value).decode('utf8')
                _environ[key] = value
            self.form = _environ

        if "encoded" in self.form and self.form["encoded"] == "true":
            for key in self.form:
                if key != "encoded":
                    try:
                        self.form[key] = base64.b64decode(self.form[key])
                    except:
                        pass
    def keys(self):
        """
        keys
        """
        return self.form

    def getvalue(self, key, default=None):
        """
        getvalue
        """
        if self.form.has_key(key):
            return self.form[key]
        else:
            return default

    def toObject(self):
        """
        toObject
        """
        return self.form

class InputProcessed(object):
    """
    InputProcessed
    """

    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')

    readline = readlines = __iter__ = read

def get_post_form(environ):
    """
    get_post_form
    """
    input = environ['wsgi.input']
    post_form = environ.get('wsgi.post_form')
    if post_form is not None and post_form[0] is input:
        return post_form[2]
    # This must be done to avoid a bug in cgi.FieldStorage
    environ.setdefault('QUERY_STRING', '')
    form = FieldStorage(fp=input, environ=environ, keep_blank_values=1)
    new_input = InputProcessed()
    post_form = (new_input, input, form)
    environ['wsgi.post_form'] = post_form
    environ['wsgi.input'] = new_input
    return form

def webpath(filename, pivot ):
    """
    webpath -  pivot = "/apps/"
    """
    return "/" + rightpart(normpath(filename), pivot)

def loadscripts(dirnames,type="js"):
    """
    loadjs
    """
    text = ""
    dirnames = listify(dirnames, sep=",")

    for dirname in dirnames:
        filenames = ls(dirname, r'.*\.%s$'%(type), recursive=True)
        for filename in filenames:
            filename = webpath(filename,"/apps/")
            if filename != '/':
                if   type=="js":
                    text += sformat("<script type='text/javascript' src='{filename}'></script>\n", {"filename": filename});
                elif type=="css":
                    text += sformat("<link href='{filename}' rel='stylesheet' type='text/css'/>\n",{"filename": filename});

    return text

def loadlibs(dirnames, type, DOCUMENT_ROOT):
    """
    loadlibs
    """
    text = ""
    dirnames = listify(dirnames, sep=",")

    filever = DOCUMENT_ROOT + "/lib/js/core/version.js"
    version = filetostr(filever)
    if version:
        version = version.replace("__VERSION__=", "").strip("'\"\t ;")

    for dirname in dirnames:
        filenames = ls(dirname, r'.*\.%s$'%(type), recursive=True)
        for filename in filenames:
            #DOCUMENT_ROOT = leftpart(normpath(filename), "/lib/")
            webname = "/lib/" + rightpart(normpath(filename), "/lib/")
            if webname and webname != '/lib/':
                if   type=="js":
                    text += sformat("<script type='text/javascript' src='{filename}?v={version}'></script>\n", {"filename": webname,"version":version});
                elif type=="css":
                    text += sformat("<link href='{filename}?v={version}' rel='stylesheet' type='text/css'/>\n",{"filename": webname,"version":version});

    return text

def template(filetpl, fileout=None, env = None):
    """
    template -  generate text from jinja2 template file
    """
    env = env if env else {}
    workdir = justpath(filetpl)
    workdir = workdir if workdir else "."
    environ = Environment(loader=FileSystemLoader(workdir))
    t = environ.get_template(justfname(filetpl))
    text = t.render(env).encode("utf-8")
    if fileout:
        strtofile(text, fileout)
    return text

def httpResponse(text, status, start_response):
    """
    httpResponse
    """
    text = "%s" % str(text)
    response_headers = [('Content-type', 'text/html'), ('Content-Length', str(len(text)))]
    if start_response:
        start_response(status, response_headers)
    return [ text.encode('utf-8')]

def httpResponseOK(text, start_response):
    """
    httpResponseOK
    """
    return httpResponse(text, "200 OK", start_response)

def httpResponseNotFound(start_response):
    """
    httpResponseNotFound
    """
    return httpResponse("404 NOT FOUND", "404 NOT FOUND", start_response)

def JSONResponse(obj, start_response):
    """
    JSONResponse
    """
    if isstring(obj):
        res = obj
    elif isinstance(obj, (dict, list)):
        res = unicode(json.dumps(obj))
    else:
        res = obj
    return httpResponse(res, "200 OK", start_response)

def getCookies(environ):
    """
    getCookies
    """
    HTTP_COOKIE = environ["HTTP_COOKIE"] if "HTTP_COOKIE" in environ else ""
    return mapify(HTTP_COOKIE,";")


def htmlResponse(environ, start_response=None, checkuser=False):
    """
    htmlResponse - return a Html Page
    """

    if checkuser and not check_user_permissions(environ):
        environ["url"] = justpath(environ["SCRIPT_FILENAME"])+"/back.html"
        return htmlResponse(environ, start_response)

    url = environ["url"] if "url" in environ else normpath(environ["SCRIPT_FILENAME"])
    url = forceext(url, "html")

    DOCUMENT_ROOT = environ["DOCUMENT_ROOT"] if "DOCUMENT_ROOT" in environ else ""

    if not isfile(url):
        return httpResponseNotFound(start_response)

    workdir    = justpath(url)
    index_html = justfname(url)

    jss = (DOCUMENT_ROOT + "/lib/js",
           justpath(url),)

    csss = (DOCUMENT_ROOT + "/lib/css",
            DOCUMENT_ROOT + "/lib/js",
            DOCUMENT_ROOT + "/lib/images",
            justpath(url),)

    env = Environment(loader=FileSystemLoader(workdir))
    t = env.get_template(index_html)

    import opensitua_core

    variables = {
        "loadjs":  loadlibs(jss, "js", DOCUMENT_ROOT),
        "loadcss": loadlibs(csss, "css", DOCUMENT_ROOT),
        "APPNAME": juststem(workdir),
        "os": os,
        "math": math,
        "gecosistema_core": opensitua_core,
        "environ":environ,
        "__file__":url
    }
    html = t.render(variables)  #.encode("utf-8","replace")
    return httpResponseOK(html, start_response)


def check_user_permissions(environ):
    """
    check_user_permissions
    """
    url = normpath(environ["SCRIPT_FILENAME"])
    filedb = justpath(url) + "/htaccess.sqlite"
    if not isfile(filedb):
        DOCUMENT_ROOT = environ["DOCUMENT_ROOT"] if "DOCUMENT_ROOT" in environ else leftpart(normpath(__file__), "/apps/")
        filedb = DOCUMENT_ROOT + "/htaccess.sqlite"

    HTTP_COOKIE = getCookies(environ)

    if os.path.isfile(filedb):
        conn = sqlite3.connect(filedb)
        conn.create_function("md5", 1, md5text)
        c = conn.cursor()
        HTTP_COOKIE["__token__"] = HTTP_COOKIE["__token__"] if "__token__" in HTTP_COOKIE else ""

        sql = """
        SELECT COUNT(*),[mail] FROM [users] 
        WHERE ('{__token__}' LIKE md5([token]||strftime('%Y-%m-%d','now')) AND [enabled])
                OR ([mail] LIKE 'everyone' AND [enabled]);"""
        sql = sformat(sql, HTTP_COOKIE)

        c.execute(sql)
        (user_enabled,mail) = c.fetchone()
        conn.close()
        return mail if user_enabled else False

    return False