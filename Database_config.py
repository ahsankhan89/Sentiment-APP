import cx_Oracle
##cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_6")
try:
    # connection = cx_Oracle.connect(
    #     user='apex_data',
    #     password='AM_APEXDATA',
    #     dsn='10.10.204.109:1521/ART',
    #     encoding='UTF-8'
    # )
    # con = cx_Oracle.connect('apex_data/AM_APEXDATA@ART')
    # print("Connected to Oracle Database", con.version)
    dsn_tns = cx_Oracle.makedsn('10.10.204.109', '1521', service_name='ART')
    conn = cx_Oracle.connect(user='apex_data', password='AM_APEXDATA', dsn=dsn_tns)
    c = conn.cursor()

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print("Oracle-Error-Code:", error.code)
    print("Oracle-Error-Message:", error.message)
except Exception as ex:
    print("General error:", ex)
