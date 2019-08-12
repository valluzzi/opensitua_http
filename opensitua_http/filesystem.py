# -----------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio for Gecosistema S.r.l.
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
# Name:        filesystem
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     27/12/2012
# -----------------------------------------------------------------------------
import os,sys,re
import shutil
import datetime
import hashlib
import base64
import tempfile
from .strings import listify,tempname,sformat
from .stime import strftime

def file(pathname):
    """
    file - True se pathname e' un file
    """
    return os.path.isfile(pathname) if pathname else False

def isfile(pathname):
    """
    isfile -  alias for file
    """
    return os.path.isfile(pathname) if pathname else False

def directory(pathname):
    """
    directory - True se pathname e'  una cartella
    """
    return os.path.isdir(pathname) if pathname else False

def exists(pathname):
    """
    exists - True se pathname is file or directory
    """
    return os.path.isfile(pathname) or os.path.isdir(pathname) if pathname else False

def normpath(pathname):
    """
    normpath
    """
    if not pathname:
        return ""
    return os.path.normpath(pathname.replace("\\", "/")).replace("\\", "/")

def justdrive(pathname):
    """
    justdrive - ritorna il drive o ptotocollo http: ftp: ... del url
    """
    arr = normpath(pathname).split("/", 2)
    return arr[0] if len(arr) > 1 else ""

def justpath(pathname, n=1):
    """
    justpath
    """
    for j in range(n):
        (pathname, _) = os.path.split(normpath(pathname))
    if pathname=="":
        return "."
    return normpath(pathname)

def justfname(pathname):
    """
    justfname - returns the basename
    """
    return normpath(os.path.basename(normpath(pathname)))

def juststem(pathname):
    """
    juststem
    """
    pathname = os.path.basename(normpath(pathname))
    (root, _) = os.path.splitext(pathname)
    return root

def justext(pathname):
    """
    justext
    """
    pathname = os.path.basename(normpath(pathname))
    (_, ext) = os.path.splitext(pathname)
    return ext.lstrip(".")

def forceext(pathname, newext):
    """
    forceext
    """
    (root, _) = os.path.splitext(normpath(pathname))
    pathname = root + ("." + newext if len(newext.strip()) > 0 else "")
    return normpath(pathname)

def name_without_ext(filename):
    """
    name_without_ext
    """
    return re.sub(r'\.(\w)+$', '', filename, 1, re.I)

def strtofile(text, filename, append=False):
    """
    strtofile
    """
    try:
        flag = "a" if append else "w"
        mkdirs(justpath(filename))
        with open(filename, flag) as stream:
            if text:
                stream.write(text)
    except Exception as ex:
        print(ex)
        return ""
    return filename


def filetostr(filename):
    """
    filetostr
    """
    try:
        with open(filename, "r") as stream:
            return stream.read()
    except:
        return None

def filetoarray(filename):
    """
    filetoarray
    """
    try:
        with open(filename, "r") as stream:
            return stream.readlines()
    except:
        return []

def filesize(filename):
    """
    filesize
    """
    if file(filename):
        return os.path.getsize(filename)
    else:
        return -1

def filectime(filename):
    """
    filectime - get the creation date
    """
    if file(filename) or directory(filename):
        unixtimestamp = os.path.getctime(filename)
        return strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromtimestamp(unixtimestamp))
    else:
        return None

def tempdir():
    """
    tempdir - return the name of temporary folder
    """
    return tempfile.gettempdir()

def tempfname(prefix="",postfix="",ext=""):
    """
    tempfname - return the name of temporary file
    """
    return normpath(tempfile.gettempdir())+"/"+tempname(prefix,postfix,ext)

def rename(filesrc, filedest, overwrite=True):
    """
    rename
    """
    try:
        if file(filedest) and overwrite:
            remove(filedest)
        mkdirs(justpath(filedest))
        os.rename(filesrc, filedest)
        return True
    except Exception as ex:
        print(ex)
    return False


def remove(files):
    """
    remove
    """
    for item in listify(files):
        try:
            if os.path.isfile(item):
                os.remove(item)
            if os.path.isdir(item):
                shutil.rmtree(item)
        except Exception as ex:
            print(ex)
            pass


def mkdirs(pathname):
    """
    mkdirs - create a folder
    """
    try:
        if file(pathname):
            pathname = justpath(pathname)
        os.makedirs(pathname)
    except:
        pass
    return directory(pathname)

def chdir(pathname):
    """
    chdir - change directory
    """
    pathname = justpath(pathname) if os.path.isfile(pathname) else pathname
    if os.path.isdir(pathname):
        os.chdir(pathname)
        return True
    return False

def pwd():
    """
    pwd - get current working directory
    """
    return os.getcwd()


def ls(dirname=".", filter=r'.*', recursive=True, exclude=""):
    """
    ls - list all files in dirname
    """
    res = []
    dirname = normpath(dirname)
    if os.path.isdir(dirname):
        try:
            # Some dir could not be accessible
            filenames = os.listdir(dirname)
            filenames.sort()
        except:
            filenames = []

        for filename in filenames:
            filename = dirname + "/" + filename
            if os.path.isfile(filename) and re.match(filter, filename, re.IGNORECASE):

                if (not exclude) or (exclude and not (exclude.lower() in filename.lower())):
                    text = "%s" % (filename)
                    res += [text]

            if os.path.isdir(filename) and recursive:
                res += ls(filename, filter, True, exclude)

    return res


def listdir(dirname=".", filter=r'.*', recursive=True, sortby="name"):
    """
    listdir - list all directoriesin dirname
    """
    res = []
    dirname = normpath(dirname)
    if os.path.isdir(dirname):
        try:
            # Some dir could not be accessible
            items = os.listdir(dirname)
            if  sortby=="name":
                items.sort()
            elif sortby=="ctime":
                items = [{"name":item,"ctime":filectime(item)} for item in items]
                items.sort(key=lambda k:k["ctime"])
                items = [item["name"] for item in items]
        except:
            items = []
        for item in items:
            item = dirname + "/" + item
            if os.path.isdir(item) and re.match(filter, item, re.IGNORECASE):
                res += ["%s" % (item)]
                if recursive:
                    res += listdir(item, filter=filter, recursive=True, sortby=sortby)
    return res


def findpath(searchdir=".", filter=r".*", maxdepth=-1, firstonly=False):
    """
    findpath
    """
    res = []

    # Limit depth search
    if maxdepth == 0:
        return res

    try:
        items = os.listdir(searchdir)
        for item in items:
            pathname = os.path.join(searchdir, item)
            if os.path.isdir(pathname):
                if re.match(filter, item, re.IGNORECASE):
                    if firstonly:
                        return [pathname]
                    res.append(pathname)
        # Recursion
        for item in items:
            pathname = os.path.join(searchdir, item)
            if os.path.isdir(pathname):
                results = findpath(pathname, filter, maxdepth - 1, firstonly)
                if len(results) and firstonly:
                    return results[0]
                res += results
    except Exception:
        # print ex
        pass
    return res




def md5sum(filename):
    """
    md5sum - returns themd5 of the file
    """
    if file(filename):
        f = open(filename, mode='rb')
        d = hashlib.md5()
        while True:
            buf = f.read(4096)
            if not buf:
                break
            d.update(buf)
        f.close()
        return d.hexdigest()
    else:
        return ""

def md5text(text):
    """
    md5text - Returns the md5 of the text
    """
    if (text!=None):
        hash = hashlib.md5()
        hash.update(text)
        return hash.hexdigest()
    return None

def filehaschanged(filename, filemd5="", updatemd5=False):
    """
    filehaschanged - It needs an .md5 file to check
    """
    filemd5 = filemd5 if filemd5 else forceext(filename, "md5")
    oldmd5 = filetostr(filemd5)
    if oldmd5:
        newmd5 = md5sum(filename)
        if oldmd5.upper() == newmd5.upper():
            return False
    # If specified update the .md5 file
    if updatemd5:
        strtofile(md5sum(filename), filemd5)
    return True


def b64(filename):
    """
    b64
    """
    data = ""
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            data = f.read()

    return base64.standard_b64encode(data)


