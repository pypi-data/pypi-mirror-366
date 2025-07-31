# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 08:37:08 2025

@author: grios5
"""

import pandas as pd
import sqlite3

class DBConexion:
    def __init__(self, nombre_db: str, nombre_tabla: str = None, df: pd.DataFrame = None):
        self.df = df
        self.nombre_db = nombre_db
        self.nombre_tabla = nombre_tabla
        self.conn = sqlite3.connect(nombre_db)
        self.cursor = self.conn.cursor()

    def map_dtype_to_sqlite(self, dtype):
        if pd.api.types.is_integer_dtype(dtype):
            return 'INTEGER'
        elif pd.api.types.is_float_dtype(dtype):
            return 'REAL'
        elif pd.api.types.is_bool_dtype(dtype):
            return 'INTEGER'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return 'DATETIME'
        else:
            return 'TEXT'

    def create_table_if_not_exists(self):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.nombre_tabla}';")
        if not self.cursor.fetchone():
            columns = []
            for col in self.df.columns:
                col_type = self.map_dtype_to_sqlite(self.df[col].dtype)
                columns.append(f'"{col}" {col_type}')
            columns_str = ", ".join(columns)
            create_stmt = f'CREATE TABLE "{self.nombre_tabla}" ({columns_str});'
            self.cursor.execute(create_stmt)
            self.conn.commit()

    def upload(self):
        self.create_table_if_not_exists()
        self.df.to_sql(self.nombre_tabla, self.conn, if_exists='append', index=False)

    def close(self):
        self.conn.close()

    def descargar_tabla(self, nombre_tabla: str = None) -> pd.DataFrame:
        '''
        Descarga una tabla de la base de datos como DataFrame.
        '''
        if nombre_tabla is None:
            nombre_tabla = self.nombre_tabla
        query = f'SELECT * FROM "{nombre_tabla}"'
        df_resultado = pd.read_sql_query(query, self.conn)
        return df_resultado

    def eliminar_tabla(self, nombre_tabla: str = None):
        '''
        Elimina una tabla de la base de datos.
        '''
        if nombre_tabla is None:
            nombre_tabla = self.nombre_tabla
        self.cursor.execute(f'DROP TABLE IF EXISTS "{nombre_tabla}"')
        self.conn.commit()


    def listar_tablas(self, nombre_db: str = None) -> list[str]:
        """
        Devuelve una lista con los nombres de todas las tablas en la base de datos.
        Si se proporciona un nombre de base de datos, se conecta temporalmente a esa base.
        """
        if nombre_db:
            # Conexión temporal a otra base de datos
            with sqlite3.connect(nombre_db) as temp_conn:
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tablas = [fila[0] for fila in temp_cursor.fetchall()]
        else:
            # Usa la conexión actual
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [fila[0] for fila in self.cursor.fetchall()]
        return tablas

# Funciones

def Subir_DF(df: pd.DataFrame, nombre_db: str, nombre_tabla: str):
    """
    Definicion
    ----------
    Se conecta a base de datos y crea la tabla en caso de no existir, o hace un append de la informacion si ya existe la tabla
     
    Argumentos;
    -----------
        df (DataFrame): Indicamos dataframe a cargar
        nombre Base de datos (str): Indicamos base de datos a conectar (.sqlite o .db)
        nombre de Tabla (str): Indicamos nombre de la tabla a Crear o actualizar

    Resultado;
    ---------
        Sube dataframe a la base de datos

    Ejemplo;
    --------
        uploader = SQLUploader(df, 'base_dato.db', 'usuarios')
        uploader.upload_and_close()  # subimos la tabla 'usuarios' a la base 'base_dato.db'y luego cierra la conexion
    """
    uploader = DBConexion(nombre_db, nombre_tabla, df)
    uploader.upload()
    uploader.close()

def Descargar_DF(nombre_db: str, nombre_tabla: str):
    """
    Definicion
    ----------
    Se conecta a base de datos y descarga tablas en caso de existir

    Argumentos;
    -----------
        nombre Base de datos (str): Indicamos base de datos a conectar (.sqlite o .db)
        nombre de Tabla (str): Indicamos nombre de la tabla a Crear o actualizar

    Resultado;
    ---------
        Entrega dataframe en caso de existir

    Ejemplo;
    --------
          base_datos = DBConexion("base_datos_ficticia.sqlite")  # creamos conexion
          df = base_datos.get_table("usuarios")     # Llamo tabla "usuarios"
          base_datos.close() # Cerramos la conexión
    """
    downloader = DBConexion(nombre_db, nombre_tabla)
    df_descargado = downloader.descargar_tabla()
    downloader.close()
    return df_descargado

def Eliminar_Tabla_de_DB(nombre_db: str, nombre_tabla: str):
    """
    Definicion
    ----------
    Se conecta a base de datos y eliminar Tabla en caso de existir

    Argumentos;
    -----------
        nombre Base de datos (str): Indicamos base de datos a conectar (.sqlite o .db)
        nombre de Tabla (str): Indicamos nombre de la tabla a Crear o actualizar

    Resultado;
    ---------
        Elimina tabla en caso de existir

    Ejemplo;
    --------
          base_datos = DBConexion("base_datos_ficticia.sqlite")   # creamos conexion
          base_datos.delete_table("usuarios")  # elimino tabla "usuarios" si existe
          base_datos.close() # Cerramos la conexión
    """
    cleaner = DBConexion(nombre_db, nombre_tabla)
    cleaner.eliminar_tabla()
    cleaner.close()

def Tablas_en_base(nombre_db: str):
    """
    Definicion
    ----------
    Se conecta a base de datos y entrega lista con todas las tablas disponibles en una BD

    Argumentos;
    -----------
        nombre Base de datos (str): Indicamos base de datos a conectar (.sqlite o .db)
        nombre de Tabla (str): Indicamos nombre de la tabla a Crear o actualizar

    Resultado;
    ---------
        Lista de nombres de tablas

    Ejemplo;
    --------
          base_datos = DBConexion("base_datos_ficticia.sqlite")   # creamos conexion
          tablas = lister.get_tablenames()  # lista de tablas
          lister.close()    # Cerramos la conexión
          """
    tablas = DBConexion(nombre_db)
    lista = tablas.listar_tablas()
    tablas.close()
    return lista

# Ejemplo de uso
if __name__ == "__main__":
    help(Tablas_en_base)