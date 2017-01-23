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

    def copy(self, tablename, filename):
        SQL_STATEMENT = """
            COPY %s FROM STDIN WITH
            CSV
            DELIMITER AS ','
            NULL as 'NULL'
        """
        file_object = open(filename)

        cur = self.connection.cursor()
        cur.copy_expert(sql=SQL_STATEMENT % tablename, file=file_object )
        cur.close()
        file_object.close()
	return

    def close(self):
        self.connection.close()
        return


    ## customized queries

    def countSamples(self, datei, datef):
        return self.query("SELECT count(*) FROM MEASUREMENT WHERE timestamp BETWEEN '"
                          +datei+"' AND '"+datef+"' ").fetchall()


    def getSamples(self, nose_id, datei, datef):
        """Retrieves the time series between the given time stamps for the
        given enose_id.

        If you want to retrieve the time series recorded for an
        induction, use getSamplesInduction instead.

        """
        query =  "SELECT * FROM MEASUREMENT WHERE enose_id = " + str(nose_id) \
                 + " AND  timestamp BETWEEN '" + datei + "' AND '" + datef + "' "
        res = self.query(query)
        return res.fetchall()


    def getSamplesInduction(self, ind_id, enose_id):
        """Uses ind_id from metadata to get inductions. It's supposed to be
        faster than using timestamp.

        """
        query =  "SELECT * FROM MEASUREMENT WHERE ind_id = " + str(ind_id) \
                 + " AND  enose_id = " + str(enose_id) + " "
        res = self.query(query)
        return res.fetchall()


    def getEnoseConfs(self):
        query = "SELECT * FROM ENOSE_CONF"
        res = self.query(query).fetchall()
        return res

    def getInductionsMetadata(self, sample = '', ind_id = '', limit = 50):
        """Searches metadatada from inductions.

        If ind_id is provided, sample is ignored. There is on
        semantics in searching for ind_id & sample, as ind_id is
        primary key.

        """

        ## Constructing the query
        query = "SELECT * FROM INDUCTION "

        if ind_id != '':
            query += "WHERE ind_id = '"+ str(ind_id) +"' "
        elif sample != '':
            query += "WHERE sample = '"+ sample +"' "

        query += "ORDER BY ind_id DESC LIMIT " + str(limit)

        ## Processing the query
        res = self.query(query).fetchall()
        return res


    def getInductionList(self):
        query = "SELECT sample, count(*), avg(tc-t0) FROM INDUCTION GROUP BY SAMPLE;"
        res = self.query(query).fetchall()
        return res


    def insertEnoseConf(self, enose_id, date, S, T, location):

        label_s = ''
        label_t = ''
        for j in range(1,9):
            label_s += 'sensor_' + str(j) + ','
            label_t += 'heat_' + str(j) + ','
        label_s += 'sensor_9,sensor_10,'


        query = "INSERT INTO ENOSE_CONF(date," + label_s + label_t
        query += "location, enose_id) VALUES ("
        query += "'" + date + "',"

        val_s = ''
        val_t = ''
        for j in range(0,8):
            val_s += "'" + S[j] + "',"
            val_t += "'" + T[j] + "',"
        val_s += "'" + S[8] + "','" + S[9] + "',"

        query += val_s + val_t
        query += "'" + location + "'," + enose_id + ");"


        self.query( query )

        return


    def updateInductionIndexingMeasurement(self, ind_id, enose_id, datei, datef):
        """Table MEASUREMENT has ind_id to be indexed for fast retrieval of
        experiments. This function updates this column.

        """

        query  = "UPDATE MEASUREMENT SET ind_id = " + str(ind_id) + " "
        query += "WHERE enose_id = " + str(enose_id) + " AND "
        query += "      timestamp BETWEEN '" + datei + "' AND '" + datef + "' "

        self.query(query)
        return

    def updateAllInductionIndexingMeasurement(self ):
        """Table MEASUREMENT has ind_id to be indexed for fast retrieval of
        experiments. This function updates this column.

        """
        query  = "SELECT ind_id, enose_id, t0 - (delta0 ||' minute')::INTERVAL,"
        query += " tc + (deltac ||' minute')::INTERVAL FROM induction WHERE not updated"
        cursor = self.query(query)

        inds = "("
        flag = False
        separator =""
        for row in cursor:
            query  = "UPDATE MEASUREMENT SET ind_id = " + str(row[0]) + " "
            query += "WHERE enose_id = " + str(row[1]) + " AND "
            query += "      timestamp BETWEEN '" + str(row[2]) + "' AND '" + str(row[3])+ "' "

            inds += separator+str(row[0])
            if(not flag):
                flag = True
                separator = ","
            self.query(query)

        inds += ")"
        query  = "UPDATE INDUCTION SET updated = true  "
        query += "WHERE ind_id IN  " + inds
        self.query(query)


        return


    def insertInduction(self, date, t0, tc, delta0, deltac, sample, weather, enose_id):
        query = "INSERT INTO INDUCTION(t0, tc, delta0, deltac, sample, weather_info, conf_id, enose_id) VALUES ("
        query += "'" + date+" "+t0 + "','" + date+" "+tc + "'," + delta0 + "," + deltac
        query += ",'" + sample + "','" + weather + "',NULL," + enose_id
        query += ");"

        self.query( query )
        return
