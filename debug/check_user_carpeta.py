import mysql.connector

def main(user_id=11):
    cn = mysql.connector.connect(host='localhost', user='root', password='732137A031E4b@', database='capired')
    cur = cn.cursor(dictionary=True)
    cur.execute("SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, id_roles, carpeta FROM recurso_operativo WHERE id_codigo_consumidor=%s", (user_id,))
    row = cur.fetchone()
    print(row)
    cur.close(); cn.close()

if __name__ == '__main__':
    main(11)