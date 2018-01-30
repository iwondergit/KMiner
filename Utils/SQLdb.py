import sqlite3

class SQLdb():
    
    def __init__(self, dbType, dbConnPara):
        self.dbType = dbType
        if(dbType == 'sqlite'):
            self.dbConn = sqlliteConnection(dbConnPara) 
        
    def connect(self):
        self.dbConn.connect()
        
    def create(self, tableName, cols, colTypes, colParas = None):
        if(colParas == None):
            colParas = ['']*len(cols)
        query = "CREATE TABLE " + tableName
        if(self.dbType == 'sqlite'):
            query += " ("
            for col, colType, colPara in zip(cols, colTypes, colParas):
                query += col + " " + colType + " " + colPara + ", "
            query = query[:-2] + ")"
        try:
            self.execute(query)
        except sqlite3.OperationalError as e:
            print(e)
            print(query)
        
    def insert(self, tableName, values):
        query = "INSERT INTO " + tableName + " VALUES "
        if(self.dbType == 'sqlite'):
            if(isinstance(values, list)):
                query += "(?"
                query += ", ?" * (len(values[0]) - 1)
                query += ")"
                self.executemany(query, values)
            else:
                query += str(values)
                self.execute(query)
        
    def select(self, tableName, cols, conditions = None):
        if(type(cols) == list):
            cols = str(cols)[1:-1].replace('\'', '')
        query = "SELECT " + cols + " FROM " + tableName
        if(conditions):
            query += " WHERE " + conditions
        return self.execute(query)
        
    def drop(self, tableName):
        query = "DROP " + tableName + "IF EXISTS"
        self.execute(query)
        self.commit()
        
    def execute(self, query):
        return self.dbConn.execute(query)
        
    def executemany(self, query, values):
        return self.dbConn.executemany(query, values)
        
    def commit(self):
        self.dbConn.commit()
        
    def close(self):
        self.dbConn.close()
    
class sqlliteConnection():
    
    def __init__(self, dbConnPara):
        self.dbPath = dbConnPara['dbPath']
            
    def connect(self):
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()
    
    def execute(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
        
    def executemany(self, query, values):
        self.cursor.executemany(query, values)
            
    def commit(self):
        self.conn.commit()
            
    def close(self):
        self.conn.close()
        
if __name__ == '__main__':
    connPara = {'dbPath': ':memory:'}
    a = SQLdb('sqlite', connPara)
    a.connect()
    cols = ['date', 'trans', 'symbol', 'qty', 'price']
    coltypes = ['text', 'text', 'text', 'real', 'real']
    a.create('stocks', cols, coltypes)
    v = ('2006-01-06', 'sell', 'rhat', 100, 35.14)
    a.insert('stocks', v)
    vs = [('2006-01-07', 'buy', 'rhat', 100, 35.14), ('2006-01-08', 'buy', 'rhat', 100, 35.14)]
    a.insert('stocks', vs)
    a.commit()
    print(list(a.select('stocks', '*')))
    print(list(a.select('stocks', 'qty')))
    print(list(a.select('stocks', ['symbol', 'price'])))
    print(list(a.select('stocks', '*', "date = '2006-01-08'")))
    a.close()