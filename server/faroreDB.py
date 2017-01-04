# postgre database
import psycopg2

# standard libraries
import sys, os, time, io
import datetime



class db:

    def __init__(self, username, password, database):
        
        self.hostname = 'localhost'
        self.username = username
        self.password = password
        self.database = database
        
        self.connection = psycopg2.connect(
            host = self.hostname,
            user = self.username,
            password = self.password,
            dbname = self.database )
        self.connection.autocommit = True
        
        return
    
    def query(self, query):
        cur = self.connection.cursor()
        cur.execute( query )
        return cur

    def close(self):
        self.connection.close()
        return

    
    ## customized queries
    
    def countSamples(self, datei, datef):
        return self.query("SELECT count(*) FROM MEASUREMENT WHERE timestamp BETWEEN '"
                          +datei+"' AND '"+datef+"' ").fetchall()

    def getSamples(self, nose_id, datei, datef):
        query =  "SELECT * FROM MEASUREMENT WHERE enose_id = " + str(nose_id) \
                 + " AND  timestamp BETWEEN '" + datei + "' AND '" + datef + "' "
        res = self.query(query)
        return res.fetchall()
    
    def getInductionsMetadata(self, limit):
        query = "SELECT * FROM INDUCTION ORDER BY ind_id DESC LIMIT " + str(limit)
        res = self.query(query).fetchall()
        return res
    
    def insertInduction(self, date, t0, tc, delta0, deltac, sample, weather, enose_id):
        query = "INSERT INTO INDUCTION(t0, tc, delta0, deltac, sample, weather_info, conf_id, enose_id) VALUES ("
        query += "'" + date+" "+t0 + "','" + date+" "+tc + "'," + delta0 + "," + deltac
        query += ",'" + sample + "','" + weather + "',NULL," + enose_id
        query += ");"
        print query

        self.query( query )
        return
