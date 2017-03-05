import jaydebeapi
driver, driver_args = 'oracle.jdbc.OracleDriver', \
   ['jdbc:oracle:thin:@//localhost:49161/xe',
    'user', 'password']
conn = jaydebeapi.connect(driver, driver_args)
curs = conn.cursor()
try:
    curs.execute("DROP TABLE Article")
except jaydebeapi.DatabaseError, e:
    print "Warning %s" % e
curs.execute("CREATE TABLE Article (ID INTEGER PRIMARY KEY," \
             "Subject VARCHAR(256)," \
             "Body CLOB" \
#             "Body LONG VARCHAR" \
             ")")
curs.execute("insert into Article values (1, 'my subject', 'A CLOB might be large')")
curs.execute("insert into Article (ID, Subject) values (2, 'my 2nd subject')")
curs.execute("select * from Article")
print curs.description[2]
for i in curs.fetchall():
    print i
