import pydb2

resultSet = pydb2.runselectquery("Select * from atmdata order by safe_factor;")



counter = 0;
list_one = []
for row in resultSet:
    a = (row['id'])
    list_one = list_one + [a]
   


value = 0
while value <24:
    for x in list_one:
        print(x)
        pydb2.runsqlquery(f'UPDATE ATMDATA SET position="{value+1}" WHERE id = "{x}"')
        #print(f'ID is {x} and rank is {value+1}')
        #print(value+1)
        value+=1