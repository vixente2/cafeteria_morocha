from django.conf import settings
import pymysql

class ConexionDB:
    def conectar(self):
        return pymysql.connect(
            host=settings.DB_CONFIG['HOST'],
            user=settings.DB_CONFIG['USER'],
            password=settings.DB_CONFIG['PASSWORD'],
            database=settings.DB_CONFIG['NAME'],
            port=settings.DB_CONFIG['PORT'],
            cursorclass=pymysql.cursors.DictCursor
        )
    def ejecutar(self, sql,params=None):
        conexion = self.conectar()
        cursor= conexion.cursor()

        cursor.execute(sql,params)
        conexion.commit()

        cursor.close()
        conexion.close()

    def verificar(self,sql,params=None):
        conexion=self.conectar()
        cursor=conexion.cursor()

        cursor.execute(sql,params)
        resultado = cursor.fetchone()

        cursor.close()
        conexion.close()

        return resultado is not None

    def consultar(self,sql,params=None):
        conexion= self.conectar()
        cursor= conexion.cursor()

        cursor.execute(sql,params)
        resultado = cursor.fetchall()

        cursor.close()
        conexion.close()

        return resultado    