#! python3
#File: htmlParse.py

"""
Parses the html from node notes so that it can be faithfully fed back through
notes-managing python code.

author: Mike Gravina
last edited: February 2017
"""

from PyQt4 import QtCore


def htmlParse(html):

    #html = str(html)######################################################################## Work all this in Unicode
    html = html
    elements = []
    chars = ''
    previousChar = ''

        #notesText = notesText.replace('\'', '\"')

    for char in html:
        if char == '<':
            # Record the previous passage if needed and start a new tag passage
            # with the opening bracket
            if previousChar != '>':
                chars = chars.replace('\'', '&apos;')
                chars = chars.replace('\"', '&quot;')
                elements.append([chars, 'content'])
            chars = ''
            chars = chars + char
        elif char == '>':
            # Add the closing tag bracket, record the current tag passage and
            # start a new passage
            chars = chars + char
            chars = chars.replace('\'', '\"')
            elements.append([chars, 'tag'])
            chars = ''
        else:
            # Add the character to the current passage
            chars = chars + char
        previousChar = char

    elements = elements[1:]
    parsed = QtCore.QString('')
    for element in elements:
        parsed = parsed + element[0]

    return parsed
