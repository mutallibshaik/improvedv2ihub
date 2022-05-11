import time
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='carla',
                             password='carla',
                             database='carla',
                             cursorclass=pymysql.cursors.DictCursor)

def runsqlquery(x):
    with connection.cursor() as cursor:
        sql = str(x)
        cursor.execute(sql)
        cursor.execute("commit")     
        cursor.close()
        #print("succesfully ran query",x)

def runselectquery(x):
    with connection.cursor() as cursor:
        sql = str(x)
        cursor.execute(sql)
        records = cursor.fetchall()     
        cursor.close()
        return records
        #print("succesfully ran query",x)

def gettrafficupdates():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * from trafficupdates"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        listans= []
        for row in result:
            value = "AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            #print(value )
            listans.append(value)     
        cursor.close()
        #print(listans)
    return listans

def mqtt_gettrafficupdates():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * from trafficupdates"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        strans= ''
        for row in result:
            value = "AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            strans = strans+value+ "\n"
        #print(strans)
        cursor.close()
    return strans

def mqtt_getweatherupdates():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * from weatherupdates"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        strans= ''
        for row in result:
            value = str(row['message'])
            strans = strans+value+ "\n"
        #print(strans)
        cursor.close()
    return strans
#mqtt_gettrafficupdates()
def insert_traffic_updates(criticality,desc,entryTime):
        with connection.cursor() as cursor:
            sql = f"insert into trafficupdates value('{criticality}', '{desc}','{entryTime}')"
            cursor.execute(sql)
            #print(f"Database insert: {criticality} with {desc} ")
            sql = "commit;"
            cursor.execute(sql)
            cursor.close()
def gettrafficupdates_critical():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from trafficupdates where level = 'critical'"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        listans= []
        for row in result:
            value = "Received:-->AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            #print(value )
            listans.append(value)     
        cursor.close()
        #print(listans)
    return listans

def gettrafficupdates_noncritical():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from trafficupdates where level != 'critical'"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        listans= []
        for row in result:
            value = "Received:-->AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            #print(value )
            listans.append(value)     
        cursor.close()
        #print(listans)
    return listans
#gettrafficupdates()

def get_atmupdates():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from atmdata"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(type(result)) is a list
        listans= []
        for row in result:
            date = row['Date']
            hour = row['hour']
            slip_message = row['slip_message']
            visibility_message = row['visibility_message']
            safe_message = row['safe_message']
            print(f'At {date}:{hour}, You have {slip_message} road conditions with {visibility_message} and {safe_message}')
            #value = "Received:-->AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            #print(value )
            #listans.append(value)     
        cursor.close()
        #print(listans)
    return 0
#get_atmupdates()

def get_atmupdates_noncrical():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from atmdata where slip_message = 'Normal' and safe_message IN ('Safe Driving Conditions','Best Driving Conditions' );"
        cursor.execute(sql)
        result = cursor.fetchall()
        strans= ''
        for row in result:
            date = row['Date']
            hour = row['hour']
            slip_message = row['slip_message']
            visibility_message = row['visibility_message']
            safe_message = row['safe_message']
            value = (f'At {date}:{hour}, You have {slip_message} road conditions with {visibility_message} and {safe_message}')
            #value = "Received:-->AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            strans = strans+value+ "\n"     
        cursor.close()
        
    return strans
#get_atmupdates()

def get_atmupdates_critical():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from atmdata where slip_message != 'Normal' or safe_message NOT IN ('Safe Driving Conditions','Best Driving Conditions' );"
        cursor.execute(sql)
        result = cursor.fetchall()
        strans= ''
        for row in result:
            date = row['Date']
            hour = row['hour']
            slip_message = row['slip_message']
            visibility_message = row['visibility_message']
            safe_message = row['safe_message']
            value = (f'At {date}:{hour}, You have {slip_message} road conditions with {visibility_message} and {safe_message}')
            strans = strans+value+ "\n"     
        cursor.close()
        
    return strans

def get_carla_atmupdates_noncritical():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from atmdata where slip_message = 'Normal' and safe_message IN ('Safe Driving Conditions','Best Driving Conditions' );"
        cursor.execute(sql)
        result = cursor.fetchall()
        listans= []
        for row in result:
            date = row['Date']
            hour = row['hour']
            slip_message = row['slip_message']
            visibility_message = row['visibility_message']
            safe_message = row['safe_message']
            value = (f'At {date}:{hour}, You have {slip_message} road conditions with {visibility_message} and {safe_message}')
            #value = "Received:-->AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            listans.append(value)     
        cursor.close()
        
    return listans

def get_carla_atmupdates_critical():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from atmdata where slip_message = 'Normal' and safe_message IN ('Safe Driving Conditions','Best Driving Conditions' );"
        cursor.execute(sql)
        result = cursor.fetchall()
        listans= []
        for row in result:
            date = row['Date']
            hour = row['hour']
            slip_message = row['slip_message']
            visibility_message = row['visibility_message']
            safe_message = row['safe_message']
            value = (f'At {date}:{hour}, You have {slip_message} road conditions with {visibility_message} and {safe_message}')
            #value = "Received:-->AlertLevel:"+str(row['level']) +" with Message:" +str(row['message'] +" at " +str(row['time']))
            listans.append(value)     
        cursor.close()
        
    return listans

def get_dataset_difference():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from dataset;"
        cursor.execute(sql)
        result = cursor.fetchall()
        listans= []
        for row in result:
            difference = row['difference']
            value = difference
            listans.append(value)     
        cursor.close()
        
    return listans

def get_dataset_windspeed():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from dataset;"
        cursor.execute(sql)
        result = cursor.fetchall()
        listans= []
        for row in result:
            windspeed = row['windspeed']
            value = windspeed
            listans.append(value)     
        cursor.close()
        
    return listans

# def get_dataset_safefactor():

#     with connection.cursor() as cursor:
#         # Read a single record
#         sql = "select * from dataset;"
#         cursor.execute(sql)
#         result = cursor.fetchall()
#         listans= []
#         for row in result:
#             safe_factor = row['safe_factor']
#             value = safe_factor
#             listans.append(value)     
#         cursor.close()
        
    return listans

def get_dataset_safefactor():

    with connection.cursor() as cursor:
        # Read a single record
        sql = "select * from dataset;"
        cursor.execute(sql)
        result = cursor.fetchall()
        listans= []
        for row in result:
            safe_factor = row['safe_factor']
            value = safe_factor
            listans.append(value)     
        cursor.close()
        
    return listans