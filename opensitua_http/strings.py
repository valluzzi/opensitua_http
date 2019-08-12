# -----------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2019 Luzzi Valerio
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
# Name:        strings.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     27/12/2012
# -----------------------------------------------------------------------------
import re
import six
import random

def isstring(var):
    """
    isstring - Returns True if the variable is a string
    """
    #return isinstance(var, (str, unicode))  #Python2
    return isinstance(var, six.string_types) #Python2 Python3

def isarray(var):
    """
    isarray - Returns True if the variable is a list
    """
    return isinstance(var, (list, tuple))

def isnumeric(text):
    """
    isnumeric - say yes if it'a number
    """
    match =  re.match("^[-+]?((\d+(\.\d*)?)|(\d*\.\d+))([eE][-+]?\d+)?$", text.strip())
    return True if match else False

def isquery(text):
    """
    isquery
    """
    pattern = r'^\s*((SELECT|PRAGMA|INSERT|DELETE|REPLACE|UPDATE|CREATE).*)'
    res = re.match(pattern, text, re.IGNORECASE)
    return True if res else False

def sformat(text, args):
    """
    sformat
    """
    for key in args:
        text = text.replace("{%s}" % key, "%s" % (args[key]))
    return text

def lower(text):
    """
    lower
    """
    if isstring(text):
        return text.lower()
    elif isarray(text):
        return [lower(item) for item in text]
    return ""

def upper(text):
    """
    upper
    """
    if isstring(text):
        return text.upper()
    elif isarray(text):
        return [upper(item) for item in text]
    return ""


def padr(text, n, c):
    """
    padr - right pad of text with character c
    """
    text = str(text)
    return text + str(c) * (n - len(text))


def padl(text, n, c):
    """
    left pad of text with character c
    """
    text = str(text)
    return str(c) * (n - len(text)) + text


def trim(text, toremove=' '):
    """
    trim - trim all array
    """
    toremove = toremove[0]
    if isstring(text):
        return text.strip(toremove)
    elif isarray(text):
        return [trim(item, toremove) for item in text if len(item) > 0]
    return text


def ltrim(text, toremove):
    """
    ltrim - left trim
    """
    toremove = toremove[0]
    if isstring(text):
        return text.lstrip(toremove)
    elif isarray(text):
        return [ltrim(item, toremove) for item in text if len(item) > 0]
    return text


def chrtran(text, tosearch, toreplace):
    """
    chrtran
    """
    for j in range(0, len(tosearch)):
        c = toreplace[j] if j in range(0, len(toreplace)) else ""
        text = text.replace(tosearch[j], c)
    return text


def startswith(text, elenco, casesensitive=True):
    """
    startswith - Returns True if the text starts with one of ...
    """
    for item in listify(elenco, ","):
        if casesensitive:
            if text.startswith(item):
                return True
        else:
            if text.lower().startswith(item.lower()):
                return True
    return False


def endswith(text, elenco, casesensitive=True):
    """
    endswith - Returns True if the text ends with one of ...
    """

    for item in listify(elenco, ","):
        if casesensitive:
            if text.endswith(item):
                return True
        else:
            if text.lower().endswith(item.lower()):
                return True
    return False


def leftpart(text, sep):
    """
    leftpart
    """
    if isstring(text):
        arr = text.split(sep, 1)
        if len(arr) >= 1:
            return arr[0]
    elif isarray(text):
        return [leftpart(item, sep) for item in text]


def rightpart(text, sep):
    """
    rightpart
    """
    if isstring(text):
        arr = text.split(sep, 1)
        if len(arr) > 1:
            return arr[1]
    elif isarray(text):
        return [rightpart(item, sep) for item in text]
    return ""


def tempname(prefix="", postfix="", ext=""):
    """
    tempname -returns a temporary name
    """
    uid = random.randint(0,1e6)
    ext = "."+ext if ext else ""
    return "%s%s%s%s"%(prefix,uid,postfix,ext)


def textin(text, prefix, postfix, casesensitive=True):
    """
    textin - return text between prefix and suffix excluded
    """

    if casesensitive:
        g = re.search(r'(?<=' + prefix + ')(.*?)(?=' + postfix + ')', text)
    else:
        g = re.search(r'(?<=' + prefix + ')(.*?)(?=' + postfix + ')', text, re.IGNORECASE)

    return g.group() if g else ""


def textbetween(text, prefix, postfix, casesensitive=True):
    """
    textin - return text between prefix and suffix excluded
    """
    if casesensitive:
        g = re.search(r'' + prefix + '(.*?)' + postfix, text, re.DOTALL)
    else:
        g = re.search(r'' + prefix + '(.*?)' + postfix, text, re.IGNORECASE|re.DOTALL)
    return g.group() if g else ""


def normalizestring(text):
    """
    normalizestring
    """
    return re.sub(r'\s+', ' ', text)


def wrap(text, leftc, rightc=None):
    """
    wrap
    """
    if isstring(text):
        rightc = leftc if rightc is None else rightc
        return leftc + text + rightc
    elif isarray(text):
        return [wrap(item, leftc, rightc) for item in text]


def unwrap(text, leftc, rightc=None):
    """
    unwrap
    """
    if isstring(text):
        rightc = leftc if rightc is None else rightc
        start = len(leftc)
        end = len(rightc)
        while text.startswith(leftc) and text.endswith(rightc):
            text = text[start:-end]
        return text
    elif isarray(text):
        return [unwrap(item, leftc, rightc) for item in text]


def split(text, sep=" ", glue="'", removeEmpty=False):
    """
    split - a variant of split with glue characters
    """
    res = []
    word = ""
    dontsplit = False
    lookahead = len(sep)
    for j in range(0, len(text)):
        c = text[j]
        ca = text[j:j+lookahead]
        if c in glue:
            dontsplit = not dontsplit
        if ca == sep and not dontsplit:
            res.append(word)
            word = ""
        else:
            word += c

    if not removeEmpty or len(word.strip()) > 0:
        res.append(word)

    return res


def listify(text, sep=",", glue="\""):
    """
    listify -  make a list from string
    """
    if text is None:
        return []
    elif isstring(text):
        return split(text, sep, glue, removeEmpty=True)
    elif isarray(text):
        return text
    return [text]

def mapify(text, sep=",", kvsep="=", strip_char=" ", glue= "\"", parsing=False):
    """
    Growup a dictionary from text string
    """
    # text = "hello=world,good=bye"
    items = listify(text, sep, glue)
    res = {}
    for item in items:
        item = item.strip(strip_char)
        arr = item.split(kvsep, 1)
        if len(arr)==1:
            key, value = arr[0], ""
        elif len(arr)==2:
            key, value = arr
        key, value = key.strip(strip_char).strip(glue), value.strip(strip_char).strip(glue)

        if parsing:
            #value  = parseValue(value)
            value = (value)

        res[key] = value

    return res



def replaceAll(text, search, replace):
    """
    replaceAll
    """
    return re.sub(text, search, replace )

