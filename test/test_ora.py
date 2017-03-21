import jaydebeapi
driver, url, driver_args = 'oracle.jdbc.OracleDriver', \
                           'jdbc:oracle:thin:@//localhost:41521/xe', \
                           [ 'mydb', 'mydb']
conn = jaydebeapi.connect(driver, url, driver_args)
curs = conn.cursor()
try:
    curs.execute("DROP TABLE Article")
except jaydebeapi.DatabaseError, e:
    print "Warning %s" % e
curs.execute("CREATE TABLE Article (ID INTEGER PRIMARY KEY," \
             "Subject VARCHAR(256)," \
             "Body CLOB" \
#             "Body LONG VARCHAR" \
             ",Created TIMESTAMP" \
             ")")
curs.execute("insert into Article values (1, 'my subject', 'A CLOB might be large', TO_DATE('1890/05/03 21:02:44', 'yyyy/mm/dd hh24:mi:ss'))")
#SYSDATE)")
curs.execute("insert into Article (ID, Subject) values (2, 'my 2nd subject')")
curs.execute("select * from Article")
print curs.description[2]
for i in curs.fetchall():
    print i
