# -*- coding: utf-8 -*-
"""
Snippets in Flowlauncher.

Simple plugin to save key/value snippets and copy to clipboard.
"""

from flowlauncher import FlowLauncher, FlowLauncherAPI
import sys
import ctypes
import sqlite3
import pyperclip

def getValue(dbName, key):
    value = {}
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM snippets WHERE key=?", (key,))
    result = cursor.fetchone()
    if result:
        value = result[0]
    else:
        value = ""
    conn.close()
    return value

def searchValues(dbName, key):
    value = {}
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    cursor.execute("SELECT key, value FROM snippets WHERE key LIKE ? ORDER BY key = ? DESC, key LIKE ? DESC LIMIT 10", ('%' + key + '%', key, key + '%'))
    result = cursor.fetchall()
    if result:
        value = result
    else:
        value = ""
    conn.close()
    return value

def saveValue(dbName, key, value):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO snippets (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    copy2clip(dbName, value)

def deleteValue(dbName, key):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM  snippets WHERE key=?", (key,))
    conn.commit()
    conn.close()

def copy2clip(dbName, value):
    """Put snippets into clipboard."""
    pyperclip.copy(value)

def summaryValue(value, length=24):
    """Return a summary of the value."""
    displayValue = value.strip().replace("\n", " ").replace("\r", " ")
    return displayValue[:length] + "..." if len(displayValue) > length else displayValue

class Snippets(FlowLauncher):

    def __init__(self, dbName):
        self.dbName = dbName
        super().__init__()
 
    def query(self, query):
        results = []
        try:
            if len(query.strip()) != 0:
                if ':' in query.strip():
                    key, value = query.strip().split(':', 1)
                    results.append({
                        "Title": "Save Code Snippet",
                        "SubTitle": "Key=" + key + ", Value=" + value,
                        "IcoPath": "assets/snippets.png", 
                        "ContextData": [key, value],
                        "JsonRPCAction": {"method": "save", "parameters": [key.strip(), value.strip()], }})
                else:
                    values = searchValues(self.dbName, query.strip())
                    for data in values:
                        key, value = data
                        results.append({
                            "Title": "⭐ " + key,
                            "SubTitle": summaryValue(value) + " (Enter to copy, Shift+Enter to delete)",
                            "IcoPath": "assets/snippets.png",
                            "ContextData": [key, value],
                            "JsonRPCAction": {"method": "copy", "parameters": [value], }})

                    if query.strip() not in [x[0] for x in values]:
                        clipboardValue = pyperclip.paste()
                        displayValue = summaryValue(clipboardValue, 36)
                        if len(clipboardValue) != 0:
                            results.append({
                                "Title": "Save from clipboard",
                                "SubTitle": "Key=" + query.strip() + ", Value=" + displayValue,
                                "IcoPath": "assets/snippets.png",
                                "ContextData": [query.strip(), clipboardValue],
                                "JsonRPCAction": {"method": "save", "parameters": [query.strip(), clipboardValue], }})

        except:
            value = sys.exc_info()
            print('Error opening %s: %s' % (value.filename, value.strerror))
            results.append({
                "Title": "Code Snippets Error",
                "SubTitle": "Please, Verify and try again",
                "IcoPath": "assets/snippets.png", "ContextData": "ctxData"})

        return results
    
    def context_menu(self, data):
        results = []
        results.append({
                        "Title": "Delete Code Snippet",
                        "SubTitle": "Key=" + data[0] + ", Value=" + data[1],
                        "IcoPath": "assets/snippets.png",
                        "JsonRPCAction": {"method": "delete", "parameters": [data[0]], }})
        return results

    def copy(self, value):
        """Copy Snippets to clipboard."""
        copy2clip(self.dbName, value)

    def save(self, key, value):
        """Save Snippets into sqlite"""
        saveValue(self.dbName, key.strip(), value.strip())

    def delete(self, key):
        """Delete Snippets from sqlite"""
        deleteValue(self.dbName, key.strip())

if __name__ == "__main__":
    Snippets()
