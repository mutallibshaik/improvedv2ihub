import pymysql.cursors
import traffic_api

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='carla',
                             password='carla',
                             database='carla',
                             cursorclass=pymysql.cursors.DictCursor)



def read_db():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * from employees"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        listans= []
        for row in result:
            value = row['name']
            #print("row value is ", value )
            listans.append(value)
            
        cursor.close()
        #print("print",listans)
    return listans


read_db()

#self._info_text += ["A","B","C"]