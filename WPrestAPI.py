from http.server import SimpleHTTPRequestHandler, BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import cgi
from cgi import parse_header, parse_multipart
import logging
import os
import re
import sqlite3
import mysql.connector
from pprint import pprint
from io import BytesIO

import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

import json
import random
import time

from markdown import markdown
from renderers import Mkd_html

REQUEST = {}
        
#####################################################
#                                                   #
# Dispatcher                                        #
#                                                   #
#####################################################

class Dispatcher:
        
    wpURL = 'http://localhost/REST-API' # change this to suit your environment
    wpUSER = 'bruno'     # your WordPress credentials you type at /wp-admin
    wpPWD = 'gonzo625'  # ditto
    
    #####################################################
    #                                                   #
    # run                                               #
    #                                                   #
    #####################################################

    def run (self, path, method):
        global REQUEST
        self.action = path
        db = DBmanager('sqlite', path)        
        #db = DBmanager('mysql', path) 

        html = self.DoHeaderMenus()
                
        if method == 'GET':
            if 'menu' in REQUEST:
                if REQUEST['menu'][0] == 'blog':
                    with open("README.md", 'r') as myfile:
                         html += markdown(myfile.read(), Mkd_html())

                elif REQUEST['menu'][0] == 'requests':
                    html += db.Reset()
                    html += self.doRequests(db) 
                    html += db.Display(f"select * from press_release_tb", False)

                #elif REQUEST['menu'][0] == 'request':
                #    html += self.processRequest(REQUEST['id'][0]) # show

                #elif REQUEST['menu'][0] == 'delprel':
                #    html += self.deletePressRelease(REQUEST['id'][0]) # delete

                #elif REQUEST['menu'][0] == 'modprel':
                #    html += self.modifyPressRelease(REQUEST['id'][0]) # modify

                elif REQUEST['menu'][0] == 'insprel':
                    db.Synchronize (self.insertPressRelease())
                    html += db.Display(f"select * from press_release_tb", False)

            elif 'order' in REQUEST:
                if 'dir' in REQUEST:
                    html += db.Display(f"select * from {REQUEST['table'][0]} order by {REQUEST['order'][0]} {REQUEST['dir'][0]}")
                else:
                    html += db.Display(f"select * from {REQUEST['table'][0]} order by {REQUEST['order'][0]}")
                       
            elif 'row' in REQUEST:
                html += db.EditTable(REQUEST['table'][0], REQUEST['row'][0])                
                
            elif 'table' in REQUEST:
                html += db.Display(f"select * from {REQUEST['table'][0]}")

        elif method == 'POST':
            if REQUEST['button'][0] == 'SAVE' :
                html += self.modifyPressRelease(REQUEST['wpid'][0]) # modify
            elif REQUEST['button'][0] == 'DELETE':
                html += self.deletePressRelease(REQUEST['wpid'][0]) # delete
                
            myid = db.PostTable()
            if REQUEST['button'][0] == 'NEW':
                db.Synchronize (self.insertPressRelease(), myid)
            html += db.Display(f"select * from press_release_tb order by id desc", False)

        else:
            html += db.Display('select * from press_release_tb order by id desc')
            
        db.Close()
        html += self.DoFooter()

        return bytes(html, 'utf-8')
        
    #####################################################
    #                                                   #
    # SyncLocalPressRelease                             #
    #                                                   #
    #####################################################

    def SyncLocalPressRelease (self, db, pressrel):
        global REQUEST

        REQUEST.pop('menu', None)        
        REQUEST.pop('id', None)        
        REQUEST['table'] = ('press_release_tb', '')
        REQUEST['wpid'] = (pressrel['id'], '')
        REQUEST['date'] = (pressrel['date'], '')
        REQUEST['slug'] = (pressrel['slug'], '')
        REQUEST['title'] = (pressrel['title']['rendered'], '')
        REQUEST['content'] = (pressrel['content']['rendered'], '')
        REQUEST['excerpt'] = (pressrel['excerpt']['rendered'], '')

        REQUEST['topic'] = (pressrel['meta']['topic'], '') 
        REQUEST['desk'] = (pressrel['meta']['desk'], '') 
        REQUEST['link'] = (pressrel['meta']['link'], '') 
        
        if db.RowExists(f"select * from press_release_tb where id = {pressrel['id']}"):
            REQUEST['button'] = ('SAVE', '')
            REQUEST['rowid'] = (pressrel['id'], 0)
        else:
            REQUEST['button'] = ('SYNC', '')
            REQUEST['rowid'] = (pressrel['id'], 0)
       
        return db.PostTable()
 
    #####################################################
    #                                                   #
    # doRequests                                        #
    #                                                   #
    #####################################################

    def doRequests (self, db):    
        r = requests.get(self.wpURL + '/wp-json/wp/v2/press_releases/?per_page=100')     
        content = r.json()
        retval = ''
        i = 0
        for pressrel in content:
            retval += '<hr>'
            for field, value in pressrel.items():
                if field in ['title', 'date', 'id', 'author', 'status']:
                    if type (value) is dict:
                        retval += f"{field}= {value['rendered']} " 
                    else:
                        if field != 'id':
                            retval += f"{field}= {value} " 
                        else:
                            retval += f"id= {value} <a href=\"{self.action}?menu=request&id={value}\">{pressrel['slug']}</a> "
                            retval += f" <a href=\"{self.action}?menu=delprel&id={value}\">DELETE</a> "
                            retval += f" <a href=\"{self.action}?menu=modprel&id={value}\">MODIFY</a> "
            retval += str(self.SyncLocalPressRelease (db, pressrel))
            i = i + 1
            
        retval +=  f"<hr> <a href=\"{self.action}?menu=insprel\">INSERT</a> <br />"   
        retval += time.strftime('%Y-%m-%dT%H:%M:%S')
        
        retval = "<div id=\"tablehead\"><h2>"+ str(i) +" press releases loaded</h2></div>\n"
        return retval 

    #####################################################
    #                                                   #
    # processPlay                                       #
    #                                                   #
    #####################################################

    def processPlay (self):    
        r = requests.get(self.wpURL + '/wp-json/wp/v2/press_releases/')
        content = r.json()
        pprint (content)
        retval = ''
        for pressrel in content:
            retval += '<hr>'
            for field, value in pressrel.items():
                if field in ['title', 'date', 'id', 'author', 'status', 'meta']:
                    if type (value) is dict:
                        if field == 'meta':
                            for f2, v2 in value.items():
                                retval += f"{f2} = {v2} " 
                        else:
                            retval += f"{field}= {value['rendered']} " 
                    else:
                        if field != 'id':
                            retval += f"{field}= {value} " 
                        else:
                            retval += f"id= {value} <a href=\"{self.action}?menu=request&id={value}\">{pressrel['slug']}</a> "
                            retval += f" <a href=\"{self.action}?menu=delprel&id={value}\">DELETE</a> "
                            retval += f" <a href=\"{self.action}?menu=modprel&id={value}\">MODIFY</a> "
            
        retval +=  f"<hr> <a href=\"{self.action}?menu=insprel\">INSERT</a> <br />"   
        retval += time.strftime('%Y-%m-%dT%H:%M:%S')
        
        return retval # json.dumps (r.text)

    #####################################################
    #                                                   #
    # processRequest                                    #
    #                                                   #
    #####################################################

    def processRequest (self, id):    
        r = requests.get(f"{self.wpURL}/wp-json/wp/v2/press_releases/{id}")
        print ('status_code='+str(r.status_code)+ ' id '+str(id))
        content = r.json()
        pprint (content)
        retval = ''
        for field, value in content.items():
            if not field in ['_links', 'categories', 'tags']:
                if type (value) is dict:
                    if field in ['acf', 'meta']:
                        for f2, v2 in value.items():
                            retval += f"\t{f2}= {v2} " 
                    else:
                        retval += f"{field}= {value['rendered']} " 
                else:
                    retval += f"{field}= {value}<br />" 
        
        json.dumps (r.text)
        return retval # json.dumps (r.text)

    #####################################################
    #                                                   #
    # deletePressRelease                                #
    #                                                   #
    #####################################################

    def deletePressRelease (self, id):    
        r = requests.delete(f"{self.wpURL}/wp-json/wp/v2/press_releases/{id}", auth=(self.wpUSER, self.wpPWD))
        print ('status_code='+str(r.status_code))
        content = r.json()
        pprint (content)
        retval = ''
        for field, value in content.items():
            if not field in ['_links', 'categories', 'tags']:
                retval += f"{field}= {value}<br />" 
        
        return retval # json.dumps (r.text)

    #####################################################
    #                                                   #
    # modifyPressRelease                                #
    #                                                   #
    #####################################################

    def modifyPressRelease (self, id):    
        payload = {\
        #'date': REQUEST['date'][0],\
        'status': 'publish',\
        'slug': REQUEST['slug'][0],\
        'title': REQUEST['title'][0],\
        'content': REQUEST['content'][0],\
        'meta':{'desk': REQUEST['desk'][0], \
        'topic': REQUEST['topic'][0], \
        'link': REQUEST['link'][0]}}

        r = requests.put(f"{self.wpURL}/wp-json/wp/v2/press_releases/{id}", json=payload, auth=(self.wpUSER, self.wpPWD))
        print ('status_code='+str(r.status_code))
        content = r.json()
        pprint (content)
        retval = ''
        for field, value in content.items():
            if not field in ['_links', 'categories', 'tags']:
                retval += f"{field}= {value}<br />" 
        
        return retval # json.dumps (r.text)

    #####################################################
    #                                                   #
    # insertPressRelease                                #
    #                                                   #
    #####################################################

    def insertPressRelease (self):    
        global REQUEST
        payload = {\
        #'date': REQUEST['date'][0],\
        'status': 'publish',\
        'slug': REQUEST['slug'][0],\
        'title': REQUEST['title'][0],\
        'content': REQUEST['content'][0],\
        'meta':{'desk': REQUEST['desk'][0], \
        'topic': REQUEST['topic'][0], \
        'link': REQUEST['link'][0]}}
        r = requests.post(f"{self.wpURL}/wp-json/wp/v2/press_releases/", json=payload, auth=(self.wpUSER, self.wpPWD))

        content = r.json()
        retval = 0
        for field, value in content.items():
            if field == 'id':
                retval = value
                                
        return retval

    #####################################################
    #                                                   #
    # DoHeaderMenus                                     #
    #                                                   #
    #####################################################

    def DoHeaderMenus (self):    
        myTitle = "WordPress REST API Python App"
        retval = f'''
<html>
<head>
<title>{myTitle}</title>
<link rel="stylesheet" type="text/css" href="/Schlumpf.css" />
<meta charset="UTF-8">
</head>
<body>

<center><h1>{myTitle}</h1></center>

<center><ul class="nav">
<li> <a href="{self.action}">Home</a></li>
<li> <a href="{self.action}?menu=blog">readme</a></li>
<li> <a href="{self.action}?menu=requests">Load from WP</a></li>
</ul></center>
        '''
        return retval

    #####################################################
    #                                                   #
    # DoFooter                                          #
    #                                                   #
    #####################################################

    def DoFooter (self):    
        retval = f'''
<div id="footer">Say NO to bloatware</div>    
</body>
</html>    
'''
        return retval
      
#####################################################
#                                                   #
# DBmanager                                         #
#                                                   #
#####################################################

class DBmanager:
            
    def __init__(self, engine, action):
        global REQUEST
        self.dsn = engine
        self.action = action
        self.db_name = 'db_name'
        if self.dsn == 'sqlite':
            
            if os.path.isfile('Schlumpf.db') == False:
                self.cnx = sqlite3.connect('Schlumpf.db')
                self.Populate()
                print ("building sqlite schema")
            else:            
                self.cnx = sqlite3.connect('Schlumpf.db')
                print ("connecting to sqlite")
        else:
            self.cnx = mysql.connector.connect(host='localhost',
                                     user='DB_USER',
                                     password='DB_PASSWORD',
                                     db=self.db_name)
            print ("connecting to mysql")
                       
    def __exit__(self, exc_type, exc_value, traceback):
        self.cnx.close()

    #####################################################
    #                                                   #
    # Reset                                             #
    #                                                   #
    #####################################################

    def Reset(self):
        cursor = self.cnx.cursor()
        string = "delete from press_release_tb"
        html = string
        if self.dsn == 'sqlite':
            try:
                cursor.execute (string)
            except sqlite3.Error as e:
                html += f'An error occurred: {e.args[0]}' 
        else:
            try:
                cursor.execute (string)
            except mysql.connector.Error as err:
                html += "Failed creating database: {}".format(err)

        cursor.close()
        return html

    #####################################################
    #                                                   #
    # Synchronize                                       #
    #                                                   #
    #####################################################

    def Synchronize(self, wpid, myid):
        cursor = self.cnx.cursor()
         
        sql = f'update press_release_tb set wpid = {wpid} where id = {myid}'

        if self.dsn == 'sqlite':
            try:
                cursor.execute (sql)
            except sqlite3.Error as e:
                print (f'An error occurred: {e.args[0]}')
        else:
            try:
                cursor.execute (sql)
            except mysql.connector.Error as err:
                print ("Failed creating database: {}".format(err))

        cursor.close()
        
    #####################################################
    #                                                   #
    # Populate                                          #
    #                                                   #
    #####################################################

    def Populate(self):
        html = ''
            
        strings = [
        'drop table if exists press_release_tb',
        "create table if not exists press_release_tb ("\
        "id integer primary key AUTO_INCREMENT,"\
        "wpid integer,"\
        "date text NOT NULL,"\
        "slug text NULL,"\
        "title text NOT NULL,"\
        "topic text NULL,"\
        "link text NULL,"\
        "desk text NULL,"\
        "content text NOT NULL,"\
        "excerpt text NULL)",
       ]
        cursor = self.cnx.cursor()
        for string in strings:
            if self.dsn == 'sqlite':
                string = re.sub(r'AUTO_INCREMENT', "AUTOINCREMENT", string)
                try:
                    cursor.execute (string)
                except sqlite3.Error as e:
                    html += f'An error occurred: {e.args[0]}' 
            else:
                try:
                    cursor.execute (string)
                except mysql.connector.Error as err:
                    html += "Failed creating database: {}".format(err)

        cursor.close()
        return html

    #####################################################
    #                                                   #
    # Close                                             #
    #                                                   #
    #####################################################

    def Close(self):
        cursor = self.cnx.cursor()
        
        if self.dsn == 'mysql':
            #cursor.commit()
            cursor.close()
        else:
            self.cnx.commit()
            self.cnx.close()
    
    #####################################################
    #                                                   #
    # RowExists                                         #
    #                                                   #
    #####################################################

    def RowExists(self, sql):
        cursor = self.cnx.cursor()
        cursor.execute(sql)
        
        for row in cursor:
            return True
            
        return False

    #####################################################
    #                                                   #
    # Display                                           #
    #                                                   #
    #####################################################

    def Display(self, sql, title=True):
        global REQUEST
        html = ''#sql+'<br />'
        matches = re.search(r'from\s+(\S+)', sql)
        view = matches.group(1)
        table = re.sub(r'_view', "", matches.group(1)) #preg_replace ("/_view/i", "", $view);
        if title:
            html += "<div id=\"tablehead\"><h2>"+re.sub(r'_tb$', '', table)+"</h2></div>\n"
        html += f'<a href="{self.action}?table={table}&row=-1">new item</a>'
        html += '<table id="Schlumpf">'
        colTypes = self.FetchColumnTypes (view)
        #pprint (colTypes)
        cursor = self.cnx.cursor()
        cursor.execute(sql)
        colname=[]
        html += '<tr>'
        i=0
        for column in list(map(lambda x: x[0], cursor.description)):
            if 'dir' in REQUEST:
                if REQUEST['dir'][0] == 'asc':
                    html += f'<th><a href="{self.action}?table={view}&order={column}&dir=desc">{column}</a></th>'
                else:
                    html += f'<th><a href="{self.action}?table={view}&order={column}&dir=asc">{column}</a></th>'
            else:
                html += f'<th><a href="{self.action}?table={view}&order={column}&dir=asc">{column}</a></th>'
            colname.insert(i, column)
            i = i+1
        html += '</tr>'
        
        for row in cursor:
            html += '<tr>'
            i=0
            for col in row:
                if colname[i] == 'id':
                    html += f'<td><a href="{self.action}?table={table}&row={col}">{col}</a></td>'
                elif colname[i] == 'link':
                    if re.search("^http", col) != None:
                        html += f'<td><a href="{col}">{col}</a></td>' #f'<td>{col} ({mytype})</td>'
                    else:
                        html += f'<td>{col}</td>' #f'<td>{col} ({mytype})</td>'
                else:
                    html += f'<td>{col}</td>' #f'<td>{col} ({mytype})</td>'
                        
                i = i+1
            html += '</tr>'
        
        html += '</table>'
        return html

    #####################################################
    #                                                   #
    # PostTable                                         #
    #                                                   #
    #####################################################

    def PostTable(self):
        global REQUEST
        sql = ''
        table = ''
        button = ''
        html = ''
        rowid = 0
        if 'rowid' in REQUEST:
            rowid = int(REQUEST['rowid'][0])
        if 'table' in REQUEST:
            table = REQUEST['table'][0]
        if 'button' in REQUEST:
            button = REQUEST['button'][0]

        if button == 'DELETE':
            rowid *= -1

        if button == 'NEW':
            rowid = -1

        REQUEST.pop('rowid', None)        
        REQUEST.pop('table', None)        
        REQUEST.pop('button', None)        
        
        html = f'<hr>rowid={rowid} table={table} button={button}<hr>'
        
        if (rowid == -1) and (button == 'NEW'):
            sql = f"insert into {table} ("
            j = 0;
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                    
                sql += field
                j=j+1
            sql += ") values ("
            
            j = 0
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                    
                sql += repr(value[0]).strip()
                
                j=j+1
                        
            sql += ");"

        elif (button == 'SYNC'):
            sql = f"insert into {table} ("
            j = 0;
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                    
                sql += field
                j=j+1
            sql += ") values ("
            
            j = 0
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                
                sql += repr(re.sub('\n', '', str(value[0]))).strip()
                
                j=j+1
                        
            sql += ");"
            
        elif (int(rowid) > 0) and (button == 'SAVE'):
            sql = f"update {table} set "
            
            j = 0
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "
                    
                sql += field
                sql += " = ";
                sql += repr(re.sub('\n', '', str(value[0]))).strip()
                    
                j=j+1
                        
            sql += f" where id = {rowid};"

        elif (int(rowid) < 0) and (button == 'DELETE'):
            rowid = abs(rowid)
            sql = f"delete from {table} where id = {rowid};"
            
        cursor = self.cnx.cursor()

        if self.dsn == 'sqlite':
            try:
                cursor.execute (sql)
            except sqlite3.Error as e:
                html += f'An error occurred: {e.args[0]} <br />with {sql}<hr>' 
        else:
            try:
                cursor.execute (sql)
            except mysql.connector.Error as err:
                html += "Failed sql statement: {}".format(err) + ' <br />with ' +sql + "<hr>"
        
        cursor.close()
        REQUEST.update({"button": [button]})
    
        html += '<hr>PostTable '+sql+' All done!<br />'
        return cursor.lastrowid
     
     
    #####################################################
    #                                                   #
    # EditTable                                         #
    #                                                   #
    #####################################################

    def EditTable (self, table, row):
        colTypes  = self.FetchColumnTypes(table)
        colValues = self.FetchColumnValues(table, row)
        
        html = f'<form class="edittable" name="myform" action="{self.action}" method="post" enctype="multipart/form-data">'
        html += '<table id="Schlumpf">'
        for key, value in colTypes.items():
            if key.lower() != 'id' and key != 'wpid':
                if re.search('\_id$', key): # a lookup field
                    lookupName = re.sub(r'\_id$', '', key) # $lookupName = preg_replace("/_id$/", "", $key);

                    lookup = re.sub(r'authority', 'person', lookupName) # bug fix 7 Feb 2019

                    html += f"<tr><td>{lookupName}</td><td>"
                    html += f'<SELECT NAME="{key}">'
                    luid = luval = ''

                    cursor = self.cnx.cursor()
                    cursor.execute(f'select id, {lookup} from {lookup}_tb order by {lookup}')
                    for lurow in cursor:
                        selected = ''
                        i=0
                        for lucol in lurow:
                            if i == 0:
                                luid = lucol
                            else:
                                luval = lucol          
                                if int(row) != -1:
                                    if colValues is True :
                                        if colValues[key] == luid:
                                            selected = "selected"
                            i=i+1
                            
                        html += f'<OPTION VALUE="{luid}" {selected}>{luval}'                   
                    html += "</td></tr>\n"
                    
                elif (key in ['topic', 'desk']) :
                    html += f"<tr><td>{key}</td><td>"
                    html += f'<SELECT NAME="{key}">'

                    cursor = self.cnx.cursor()
                    cursor.execute(f'select distinct {key} from {table} order by {key}')
                    for drow in cursor:
                        selected = ''
                        if colValues[key] == drow[0]:
                            selected = "selected"
                            
                        html += f'<OPTION VALUE="{drow[0]}" {selected}>{drow[0]}'                   
                    html += "</td></tr>\n"

                else:    
                    html += f'<tr><td>{key}</td><td>'
                    if not colValues :
                        myvalue = ''
                    else :
                        myvalue = colValues[key]
                        
                    if key in ['date', 'datetime']:
                        html += f'<input type="datetime-local" name="{key}" value="{myvalue}">'
                        
                    elif (key == 'int') or (key == 'integer') or (key == 'float'):
                        html += f'<input type="number-local" name="{key}" value="{myvalue}">'

                    elif key in ['content', 'excerpt']:
                        html += f'<textarea name="{key}" rows="4" cols="75">{myvalue}</textarea>'
                    else:
                        html += f'<input type="text" name="{key}" size=75 value="{myvalue}">'
                        
                    html += "</td></tr>\n"    
            
        if int(row) != -1:
            mywp = colValues['wpid']
        else:
            mywp = -1
        html +=  f'<tr><td><input type="hidden" name="wpid" value="{mywp}"/>'
        html +=  f'<tr><td><input type="hidden" name="rowid" value="{row}"/>'
        html +=  f'<input type="hidden" name="table" value="{table}"/>'
        if int(row) == -1:
            html +=  f'</td><td><input type="submit" name="button" value="NEW"/></td</tr>'
        else:
            html +=  f'<input type="submit" name="button" OnClick="return confirm(\'Are you sure you want to delete this record ?\');"value="DELETE"/></td><td>\n'
            html +=  f'<input type="submit" name="button" value="SAVE"/></td</tr>\n'
            
        html +=  f'</table>\n</form>'
        return html
    
    #####################################################
    #                                                   #
    # FetchColumnTypes                                  #
    #                                                   #
    #####################################################

    def FetchColumnTypes(self, table):
        cursor = self.cnx.cursor()
        cols = {}
        if self.dsn == 'sqlite':
            cursor.execute(f"select * from sqlite_master where type='table' and name='{table}'")
            i=0
            mycol=0
            for column in list(map(lambda x: x[0], cursor.description)):
                if column == 'sql':
                    mycol = i
                i = i+1

            for row in cursor:
                sql = row[mycol]

                sql = sql.replace("\n", "")
                sql = sql.replace("\t", " ")
                
                matches = re.search(r'\((.+)\)', sql)
                sqldef = matches.group(1)
                fields = re.split(r',', sqldef)
                
                for field in fields:
                    matches = re.search(r'(\S+)\s+(\w+)', field)
                    name = matches.group(1)
                    name = name.replace("\"", "")
                    attribute = matches.group(2)
                    cols[name] = attribute
                
        else:
            cursor.execute(f"select column_name, data_type from information_schema.columns where table_name = '{table}' and table_schema = '{self.db_name}'")
            for row in cursor:
                cols[row[0]] = row[1]
             
        return cols

    #####################################################
    #                                                   #
    # FetchColumnValues                                 #
    #                                                   #
    #####################################################

    def FetchColumnValues (self, table, id):    
        cursor = self.cnx.cursor()
        cols = {}
        
        if id == -1:
            idd = 1
        else:
            idd = id
        
        cursor.execute(f'select * from {table} where id = {idd}')
        colname=[]
        i=0
        for column in list(map(lambda x: x[0], cursor.description)):
            colname.insert(i, column)
            i = i+1
        
        for row in cursor:
            i=0
            for col in row:
                if id == -1:
                    cols[colname[i]] = ''
                else:
                    cols[colname[i]] = col
                i=i+1
        return cols

#####################################################
#                                                   #
# web server                                        #
#                                                   #
#####################################################
class S(SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global REQUEST
        print ('self.path is '+self.path)
        if (self.path != '/') and (not re.search(r'^\/\?', self.path)):
            print ("serving a file..."+self.path)  # serving a file.../?menu=blog
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
        else:
            print ("parsing and dispatch")
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_response()
            (scheme, netloc, pathology, params, query, fragment) = urlparse (self.path)  # returns a tuple   
            REQUEST.clear()
            REQUEST = parse_qs (query)
            if len(query) == 0:
                method = ''
            else:
                method = 'GET'
                
            d = Dispatcher()
            self.wfile.write(d.run(pathology, method))       

    def list_directory(self, path): #disable it
        return None

    def do_POST(self):
        global REQUEST
        REQUEST.clear()
        
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        
        boundary = pdict['boundary'].encode("utf-8") # some kludge
        pdict['boundary'] = boundary # to circumvent bugs in cgi
        pdict['CONTENT-LENGTH'] = int(self.headers['content-length'])
        
        if ctype == 'multipart/form-data':
            REQUEST = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            REQUEST = cgi.parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        else:
            REQUEST = {}
            
        path = ''
        d = Dispatcher()
        self._set_response()
        self.wfile.write(d.run(path, 'POST'))       

#####################################################
#                                                   #
# main loop                                         #
#                                                   #
#####################################################

def run(server_class=HTTPServer, handler_class=S, port=3000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting httpd on port {port}...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
