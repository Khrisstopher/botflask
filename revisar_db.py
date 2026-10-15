# Este es un script para revisar las bases de datos SQLite y listar las tablas que contienen, excluyendo las tablas internas de SQLite.
# Se usó para pruebas.

import sqlite3

for ruta in [
    r"instance\botflask.db",
    r"instance\migration_temp.db",
]:
    conexion = sqlite3.connect(ruta)
    tablas = conexion.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    conexion.close()

    print(f"\nBase de datos: {ruta}")
    print(f"Tablas: {tablas}")