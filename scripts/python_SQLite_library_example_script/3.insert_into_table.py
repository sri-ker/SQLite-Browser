# http://www.runoob.com/sqlite/sqlite-python.html

import sqlite3

import random

conn = sqlite3.connect('test.db')
print "Opened database successfully";

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (1, 'Paul', 32, 'California', 20000.00 )");

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");

# conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");


for i in range(10000000):
	name=random.choice('fsdajkldfsajklfewjqiok')
	age=round(random.random()*100.0)
	salary=round(random.random()*10000.0)
	conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES ("+str(i)+", '"+name+"', "+str(age)+", 'Rich-Mond ', "+str(salary)+" )");

conn.commit()
print "Records created successfully";
conn.close()