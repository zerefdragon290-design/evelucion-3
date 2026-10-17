import sqlite3


class ErrorBD(Exception):
    pass


class ConexionBD:
    def __init__(self, ruta="empresa.db"):
        self.__ruta = ruta
        self.__conn = None

    def conectar(self):
        try:
            self.__conn = sqlite3.connect(self.__ruta)
            self.__conn.row_factory = sqlite3.Row
            self.__conn.execute("PRAGMA foreign_keys = ON")
            self.__crear_tablas()
            return self.__conn
        except sqlite3.Error as e:
            raise ErrorBD(f"No se pudo conectar a la base de datos: {e}")

    def cerrar(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    # Métodos agregados para soportar el protocolo de contexto (with)
    def __enter__(self):
        return self.conectar()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()

    def __crear_tablas(self):
        self.__conn.executescript("""
            CREATE TABLE IF NOT EXISTS departamento (
                id_depa          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_depa      TEXT NOT NULL UNIQUE,
                gerente_asociado TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS empleado (
                id_unico       INTEGER PRIMARY KEY,
                nombre         TEXT NOT NULL,
                direccion      TEXT,
                telefono       TEXT,
                email          TEXT NOT NULL UNIQUE,
                fecha_contrato TEXT NOT NULL,
                salario        REAL NOT NULL CHECK (salario > 0),
                id_depa        INTEGER REFERENCES departamento(id_depa) ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS proyecto (
                id_proyecto  INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre       TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL,
                descripcion  TEXT
            );
            CREATE TABLE IF NOT EXISTS empleado_proyecto (
                id_unico    INTEGER REFERENCES empleado(id_unico) ON DELETE CASCADE,
                id_proyecto INTEGER REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
                PRIMARY KEY (id_unico, id_proyecto)
            );
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                horas       REAL NOT NULL CHECK (horas > 0),
                fecha       TEXT NOT NULL,
                descripcion TEXT,
                id_unico    INTEGER NOT NULL REFERENCES empleado(id_unico) ON DELETE CASCADE,
                id_proyecto INTEGER NOT NULL REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
            );
        """)


class DAOBase:
    """Clase base: centraliza la ejecución de consultas y el manejo de errores."""

    def __init__(self, conexion):
        self._conn = conexion

    def _ejecutar(self, sql, params=()):
        try:
            with self._conn:  # commit si todo sale bien, rollback si falla
                return self._conn.execute(sql, params)
        except sqlite3.IntegrityError as e:
            raise ErrorBD(f"Dato inválido o duplicado: {e}")
        except sqlite3.Error as e:
            raise ErrorBD(f"Error de base de datos: {e}")


class DepartamentoDAO(DAOBase):
    def insertar(self, nombre_depa, gerente_asociado):
        return self._ejecutar(
            "INSERT INTO departamento (nombre_depa, gerente_asociado) VALUES (?, ?)",
            (nombre_depa, gerente_asociado)).lastrowid

    def consultar(self, id_depa):
        return self._ejecutar(
            "SELECT * FROM departamento WHERE id_depa = ?", (id_depa,)).fetchone()

    def listar(self):
        return self._ejecutar("SELECT * FROM departamento").fetchall()

    def actualizar(self, id_depa, nombre_depa, gerente_asociado):
        return self._ejecutar(
            "UPDATE departamento SET nombre_depa = ?, gerente_asociado = ? WHERE id_depa = ?",
            (nombre_depa, gerente_asociado, id_depa)).rowcount

    def eliminar(self, id_depa):
        return self._ejecutar(
            "DELETE FROM departamento WHERE id_depa = ?", (id_depa,)).rowcount


class EmpleadoDAO(DAOBase):
    def insertar(self, id_unico, nombre, direccion, telefono, email,
                 fecha_contrato, salario, id_depa=None):
        self._ejecutar(
            "INSERT INTO empleado VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (id_unico, nombre, direccion, telefono, email,
             fecha_contrato, salario, id_depa))
        return id_unico

    def consultar(self, id_unico):
        return self._ejecutar(
            "SELECT * FROM empleado WHERE id_unico = ?", (id_unico,)).fetchone()

    def consultar_con_departamento(self, id_unico):
        sql = """
            SELECT e.*, d.nombre_depa 
            FROM empleado e 
            LEFT JOIN departamento d ON e.id_depa = d.id_depa 
            WHERE e.id_unico = ?
        """
        return self._ejecutar(sql, (id_unico,)).fetchone()

    def listar(self):
        return self._ejecutar("SELECT * FROM empleado").fetchall()

    def actualizar(self, id_unico, direccion, telefono, email, salario, id_depa):
        return self._ejecutar(
            """UPDATE empleado SET direccion = ?, telefono = ?, email = ?,
               salario = ?, id_depa = ? WHERE id_unico = ?""",
            (direccion, telefono, email, salario, id_depa, id_unico)).rowcount

    def eliminar(self, id_unico):
        return self._ejecutar(
            "DELETE FROM empleado WHERE id_unico = ?", (id_unico,)).rowcount

    def asignar_proyecto(self, id_unico, id_proyecto):
        self._ejecutar(
            "INSERT OR IGNORE INTO empleado_proyecto (id_unico, id_proyecto) VALUES (?, ?)",
            (id_unico, id_proyecto))

    def quitar_proyecto(self, id_unico, id_proyecto):
        return self._ejecutar(
            "DELETE FROM empleado_proyecto WHERE id_unico = ? AND id_proyecto = ?",
            (id_unico, id_proyecto)).rowcount

    def proyectos_de(self, id_unico):
        return self._ejecutar(
            """SELECT p.* FROM proyecto p
               JOIN empleado_proyecto ep ON ep.id_proyecto = p.id_proyecto
               WHERE ep.id_unico = ?""", (id_unico,)).fetchall()


class ProyectoDAO(DAOBase):
    def insertar(self, nombre, fecha_inicio, descripcion):
        return self._ejecutar(
            "INSERT INTO proyecto (nombre, fecha_inicio, descripcion) VALUES (?, ?, ?)",
            (nombre, fecha_inicio, descripcion)).lastrowid

    def consultar(self, id_proyecto):
        return self._ejecutar(
            "SELECT * FROM proyecto WHERE id_proyecto = ?", (id_proyecto,)).fetchone()

    def listar(self):
        return self._ejecutar("SELECT * FROM proyecto").fetchall()

    def actualizar(self, id_proyecto, nombre, fecha_inicio, descripcion):
        return self._ejecutar(
            """UPDATE proyecto SET nombre = ?, fecha_inicio = ?, descripcion = ?
               WHERE id_proyecto = ?""",
            (nombre, fecha_inicio, descripcion, id_proyecto)).rowcount

    def eliminar(self, id_proyecto):
        return self._ejecutar(
            "DELETE FROM proyecto WHERE id_proyecto = ?", (id_proyecto,)).rowcount


class RegistroTiempoDAO(DAOBase):
    def listar(self):
        return self._ejecutar("SELECT * FROM registro_tiempo ORDER BY fecha").fetchall()

    def insertar(self, horas, fecha, descripcion, id_unico, id_proyecto):
        return self._ejecutar(
            """INSERT INTO registro_tiempo (horas, fecha, descripcion, id_unico, id_proyecto)
               VALUES (?, ?, ?, ?, ?)""",
            (horas, fecha, descripcion, id_unico, id_proyecto)).lastrowid

    def consultar(self, id_registro):
        return self._ejecutar(
            "SELECT * FROM registro_tiempo WHERE id_registro = ?", (id_registro,)).fetchone()

    def listar_por_empleado(self, id_unico):
        return self._ejecutar(
            "SELECT * FROM registro_tiempo WHERE id_unico = ? ORDER BY fecha",
            (id_unico,)).fetchall()

    def listar_por_proyecto(self, id_proyecto):
        return self._ejecutar(
            "SELECT * FROM registro_tiempo WHERE id_proyecto = ? ORDER BY fecha",
            (id_proyecto,)).fetchall()

    def actualizar(self, id_registro, horas, fecha, descripcion):
        return self._ejecutar(
            """UPDATE registro_tiempo SET horas = ?, fecha = ?, descripcion = ?
               WHERE id_registro = ?""",
            (horas, fecha, descripcion, id_registro)).rowcount

    def eliminar(self, id_registro):
        return self._ejecutar(
            "DELETE FROM registro_tiempo WHERE id_registro = ?", (id_registro,)).rowcount