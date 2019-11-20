# -------------------------------------------------------------------------------
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
# Name:        stime.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     08/08/2018
# -------------------------------------------------------------------------------
from .strings import isstring
import datetime,random

def strftime(frmt, text):
    """
    strftime
    """
    if not text:
        return datetime.datetime.now().strftime(frmt)
    elif isinstance(text, (datetime.datetime,datetime.date,) ):
        return text.strftime(frmt)
    elif isstring(text):
        date = datetime.datetime.strptime(text, "%Y-%m-%d")
        return date.strftime(frmt)

    return ""

def randint(n):
    """
    randint
    """
    return random.randint(0,n)