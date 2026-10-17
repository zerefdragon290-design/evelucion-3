class Departamento:
    def __init__(self, dao, nombre_depa, gerente_asociado, id_depa=None):
        self.__dao = dao
        self.__id_depa = id_depa
        self.__nombre_depa = nombre_depa
        self.__gerente_asociado = gerente_asociado

    def crear_depa(self):
        self.__id_depa = self.__dao.insertar(self.__nombre_depa, self.__gerente_asociado)
        return self.__id_depa

    def editar_depa(self, nombre_depa, gerente_asociado):
        self.__nombre_depa = nombre_depa
        self.__gerente_asociado = gerente_asociado
        return self.__dao.actualizar(self.__id_depa, nombre_depa, gerente_asociado) > 0

    def buscar_depa(self):
        fila = self.__dao.consultar(self.__id_depa)
        if fila is None:
            print("Departamento no encontrado")
            return None
        self.__nombre_depa = fila["nombre_depa"]
        self.__gerente_asociado = fila["gerente_asociado"]
        print(f"Departamento: {self.__nombre_depa} | Gerente: {self.__gerente_asociado}")
        return self

    def eliminar_depa(self):
        return self.__dao.eliminar(self.__id_depa) > 0


class Empleado:
    def __init__(self, idUnico, nombre, direccion, telefono, email,
                 fechaContrato, salario, id_depa=None):
        self.__idUnico = idUnico
        self.__nombre = nombre
        self.__direccion = direccion
        self.__telefono = telefono
        self.__email = email
        self.__fechaContrato = fechaContrato
        self.__salario = salario
        self.__id_depa = id_depa  # la relación con Departamento vive en la BD

    def trabajar(self):
        print("trabajando...")

    def informacionDe_empleado(self):
        print(f"ID del: {self.__idUnico}\nNombre: {self.__nombre}\nDirección: {self.__direccion}\n"
              f"Teléfono: {self.__telefono}\nEmail: {self.__email}\n"
              f"Fecha de contrato: {self.__fechaContrato}\nSalario: {self.__salario}")

    def departamentoDe_empleado(self):
        if self.__id_depa is None:
            print("El empleado no tiene departamento asignado")
        return self.__id_depa


class Proyecto:
    def __init__(self, dao, nombre, fechaInicio, descripcion, id_proyecto=None):
        self.__dao = dao
        self.__id_proyecto = id_proyecto
        self.__nombre = nombre
        self.__fechaInicio = fechaInicio
        self.__descripcion = descripcion

    def crear_proyecto(self):
        self.__id_proyecto = self.__dao.insertar(
            self.__nombre, self.__fechaInicio, self.__descripcion)
        return self.__id_proyecto

    def editar_proyecto(self, nombre, fechaInicio, descripcion):
        self.__nombre = nombre
        self.__fechaInicio = fechaInicio
        self.__descripcion = descripcion
        return self.__dao.actualizar(
            self.__id_proyecto, nombre, fechaInicio, descripcion) > 0

    def buscar_proyecto(self):
        fila = self.__dao.consultar(self.__id_proyecto)
        if fila is None:
            print("Proyecto no encontrado")
            return None
        self.__nombre = fila["nombre"]
        self.__fechaInicio = fila["fecha_inicio"]
        self.__descripcion = fila["descripcion"]
        print(f"Proyecto: {self.__nombre} | Inicio: {self.__fechaInicio} | {self.__descripcion}")
        return self

    def eliminar_proyecto(self):
        return self.__dao.eliminar(self.__id_proyecto) > 0


class RegistroTiempo:
    def __init__(self, dao, horas_trabajadas, fechaDe_trabajo, descripcionDel_trabajo,
                 id_unico, id_proyecto):
        self.__dao = dao
        self.__horas_trabajadas = horas_trabajadas
        self.__fechaDe_trabajo = fechaDe_trabajo
        self.__descripcionDel_trabajo = descripcionDel_trabajo
        self.__id_unico = id_unico
        self.__id_proyecto = id_proyecto

    def registro_proyecto_particular(self):
        filas = self.__dao.listar_por_proyecto(self.__id_proyecto)
        for f in filas:
            print(f"[{f['fecha']}] {f['horas']} h - {f['descripcion']} (empleado {f['id_unico']})")
        return filas

    def registro_empleado_particular(self):
        filas = self.__dao.listar_por_empleado(self.__id_unico)
        for f in filas:
            print(f"[{f['fecha']}] {f['horas']} h - {f['descripcion']} (proyecto {f['id_proyecto']})")
        return filas


class Informes:
    def informe_empleado(self, empleado):
        empleado.informacionDe_empleado()

    def informe_departamento(self, departamento):
        departamento.buscar_depa()

    def informe_proyecto(self, proyecto):
        proyecto.buscar_proyecto()

    def informe_registro_tiempo(self, registros):
        for f in registros:
            print(f"[{f['fecha']}] {f['horas']} h - {f['descripcion']}")

    def exportar_pdf(self):
        print("Pendiente: exportar a PDF (por ejemplo con reportlab)")

    def exportar_excel(self):
        print("Pendiente: exportar a Excel (por ejemplo con openpyxl)")