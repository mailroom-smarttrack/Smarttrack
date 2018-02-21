import MySQLdb

db = MySQLdb.connect(user='root', password='wks01admin',
                              host='localhost',
                              database='smarttrack')


cursor=db.cursor()

ins_sql = 'insert into smarttrack.employees (employees.EmpFirstName, employees.EmpLastName) values  (%(first)s , %(last)s)'    
ins_val = {'first' : 'firstname' , 'last' : 'lastname'}
cursor.execute(ins_sql ,ins_val)
db.commit()


sql1='SELECT EmpFirstName, EmpLastName FROM smarttrack.employees where EmpID = 500;'

db.commit()
cursor.execute(sql1)
data=cursor.fetchall()
print (data[0][0])
print (data[0][1])
db.close()