import re
from datetime import datetime

from bd import (ConexionBD, ErrorBD, DepartamentoDAO, EmpleadoDAO,
                ProyectoDAO, RegistroTiempoDAO)
from modelo import Departamento, Empleado, Proyecto, RegistroTiempo


def pedir_texto(msg):
    valor = input(msg).strip()
    while not valor:
        valor = input("Este campo es obligatorio. " + msg).strip()
    return valor


def pedir_entero(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Debe ser un número entero.")


def pedir_real_positivo(msg):
    while True:
        try:
            valor = float(input(msg))
            if valor > 0:
                return valor
            print("Debe ser mayor que cero.")
        except ValueError:
            print("Debe ser un número.")


def pedir_email(msg):
    while True:
        email = input(msg).strip()
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return email
        print("Email inválido (ejemplo: nombre@dominio.cl).")


def pedir_fecha(msg):
    while True:
        texto = input(msg).strip()
        try:
            datetime.strptime(texto, "%Y-%m-%d")
            return texto
        except ValueError:
            print("Formato inválido. Usa AAAA-MM-DD.")


def elegir(filas, campo_id, campos):
    """Muestra una lista numerada y devuelve el ID de la fila elegida, o None."""
    if not filas:
        print("No hay registros disponibles")
        return None
    for i, f in enumerate(filas, start=1):
        print(f"{i}. " + " | ".join(str(f[c]) for c in campos))
    while True:
        op = input("Seleccione un número (0 para cancelar): ").strip()
        if op == "0":
            return None
        if op.isdigit() and 1 <= int(op) <= len(filas):
            return filas[int(op) - 1][campo_id]
        print("Número inválido.")


def menu_departamentos(conn):
    dao = DepartamentoDAO(conn)
    cols = ["nombre_depa", "gerente_asociado"]
    while True:
        print("\n--- DEPARTAMENTOS ---\n 1) Crear\n 2) Consultar\n 3) Editar\n 4) Eliminar\n 0) Volver\n")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                depto = Departamento(dao, pedir_texto("Nombre: "), pedir_texto("Gerente: "))
                print(f"Departamento creado con id {depto.crear_depa()}")
            elif op == "2":
                id_depa = elegir(dao.listar(), "id_depa", cols)
                if id_depa is not None:
                    Departamento(dao, "", "", id_depa).buscar_depa()
            elif op == "3":
                id_depa = elegir(dao.listar(), "id_depa", cols)
                if id_depa is not None:
                    ok = Departamento(dao, "", "", id_depa).editar_depa(
                        pedir_texto("Nuevo nombre: "), pedir_texto("Nuevo gerente: "))
                    print("Departamento editado" if ok else "No encontrado")
            elif op == "4":
                id_depa = elegir(dao.listar(), "id_depa", cols)
                if id_depa is not None:
                    ok = Departamento(dao, "", "", id_depa).eliminar_depa()
                    print("Departamento eliminado" if ok else "No encontrado")
            elif op == "0":
                return
            else:
                print("Opción inválida")
        except ErrorBD as e:
            print(f"Error: {e}")


def menu_empleados(conn):
    dao = EmpleadoDAO(conn)
    proy_dao = ProyectoDAO(conn)
    cols = ["nombre", "email"]
    while True:
        print("\n--- EMPLEADOS ---\n 1) Crear\n 2) Consultar\n 3) Editar\n 4) Eliminar\n 5) Asignar proyecto\n 0) Volver")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                dao.insertar(
                    pedir_entero("ID único: "),
                    pedir_texto("Nombre: "),
                    pedir_texto("Dirección: "),
                    pedir_texto("Teléfono: "),
                    pedir_email("Email: "),
                    pedir_fecha("Fecha de contrato (AAAA-MM-DD): "),
                    pedir_real_positivo("Salario: "),
                    pedir_entero("ID departamento (0 si no tiene): ") or None)
                print("Empleado registrado")
            elif op == "2":
                id_unico = elegir(dao.listar(), "id_unico", cols)
                if id_unico is not None:
                    f = dao.consultar(id_unico)
                    emp = Empleado(f["id_unico"], f["nombre"], f["direccion"], f["telefono"],
                                   f["email"], f["fecha_contrato"], f["salario"], f["id_depa"])
                    emp.informacionDe_empleado()
                    emp.departamentoDe_empleado()
            elif op == "3":
                id_unico = elegir(dao.listar(), "id_unico", cols)
                if id_unico is not None:
                    ok = dao.actualizar(
                        id_unico,
                        pedir_texto("Nueva dirección: "),
                        pedir_texto("Nuevo teléfono: "),
                        pedir_email("Nuevo email: "),
                        pedir_real_positivo("Nuevo salario: "),
                        pedir_entero("ID departamento (0 si no tiene): ") or None)
                    print("Empleado actualizado" if ok else "Empleado no encontrado")
            elif op == "4":
                id_unico = elegir(dao.listar(), "id_unico", cols)
                if id_unico is not None:
                    ok = dao.eliminar(id_unico)
                    print("Empleado eliminado" if ok else "Empleado no encontrado")
            elif op == "5":
                id_unico = elegir(dao.listar(), "id_unico", cols)
                if id_unico is not None:
                    id_proyecto = elegir(proy_dao.listar(), "id_proyecto",
                                         ["nombre", "fecha_inicio"])
                    if id_proyecto is not None:
                        dao.asignar_proyecto(id_unico, id_proyecto)
                        print("Proyecto asignado")
            elif op == "0":
                return
            else:
                print("Opción inválida")
        except ErrorBD as e:
            print(f"Error: {e}")


def menu_proyectos(conn):
    dao = ProyectoDAO(conn)
    cols = ["nombre", "fecha_inicio"]
    while True:
        print("\n--- PROYECTOS ---\n 1) Crear\n 2) Consultar\n 3) Editar\n 4) Eliminar\n 0) Volver")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                proy = Proyecto(dao, pedir_texto("Nombre: "),
                                pedir_fecha("Fecha de inicio (AAAA-MM-DD): "),
                                pedir_texto("Descripción: "))
                print(f"Proyecto creado con id {proy.crear_proyecto()}")
            elif op == "2":
                id_proyecto = elegir(dao.listar(), "id_proyecto", cols)
                if id_proyecto is not None:
                    Proyecto(dao, "", "", "", id_proyecto).buscar_proyecto()
            elif op == "3":
                id_proyecto = elegir(dao.listar(), "id_proyecto", cols)
                if id_proyecto is not None:
                    ok = Proyecto(dao, "", "", "", id_proyecto).editar_proyecto(
                        pedir_texto("Nuevo nombre: "),
                        pedir_fecha("Nueva fecha de inicio (AAAA-MM-DD): "),
                        pedir_texto("Nueva descripción: "))
                    print("Proyecto editado" if ok else "No encontrado")
            elif op == "4":
                id_proyecto = elegir(dao.listar(), "id_proyecto", cols)
                if id_proyecto is not None:
                    ok = Proyecto(dao, "", "", "", id_proyecto).eliminar_proyecto()
                    print("Proyecto eliminado" if ok else "No encontrado")
            elif op == "0":
                return
            else:
                print("Opción inválida")
        except ErrorBD as e:
            print(f"Error: {e}")


def menu_registros(conn):
    dao = RegistroTiempoDAO(conn)
    emp_dao = EmpleadoDAO(conn)
    proy_dao = ProyectoDAO(conn)
    cols_emp = ["nombre", "email"]
    cols_proy = ["nombre", "fecha_inicio"]
    cols_reg = ["fecha", "horas", "descripcion"]
    while True:
        print("\n--- REGISTRO DE TIEMPO ---\n 1) Registrar\n 2) Ver por empleado\n 3) Ver por proyecto\n 4) Editar\n 5) Eliminar\n 0) Volver")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                id_unico = elegir(emp_dao.listar(), "id_unico", cols_emp)
                id_proyecto = elegir(proy_dao.listar(), "id_proyecto", cols_proy) if id_unico is not None else None
                if id_unico is not None and id_proyecto is not None:
                    id_reg = dao.insertar(
                        pedir_real_positivo("Horas trabajadas: "),
                        pedir_fecha("Fecha (AAAA-MM-DD): "),
                        pedir_texto("Descripción del trabajo: "),
                        id_unico, id_proyecto)
                    print(f"Registro creado con id {id_reg}")
            elif op == "2":
                id_unico = elegir(emp_dao.listar(), "id_unico", cols_emp)
                if id_unico is not None:
                    RegistroTiempo(dao, 0, "", "", id_unico, 0).registro_empleado_particular()
            elif op == "3":
                id_proyecto = elegir(proy_dao.listar(), "id_proyecto", cols_proy)
                if id_proyecto is not None:
                    RegistroTiempo(dao, 0, "", "", 0, id_proyecto).registro_proyecto_particular()
            elif op == "4":
                id_reg = elegir(dao.listar(), "id_registro", cols_reg)
                if id_reg is not None:
                    ok = dao.actualizar(
                        id_reg,
                        pedir_real_positivo("Nuevas horas: "),
                        pedir_fecha("Nueva fecha (AAAA-MM-DD): "),
                        pedir_texto("Nueva descripción: "))
                    print("Registro actualizado" if ok else "No encontrado")
            elif op == "5":
                id_reg = elegir(dao.listar(), "id_registro", cols_reg)
                if id_reg is not None:
                    ok = dao.eliminar(id_reg)
                    print("Registro eliminado" if ok else "No encontrado")
            elif op == "0":
                return
            else:
                print("Opción inválida")
        except ErrorBD as e:
            print(f"Error: {e}")


def main():
    try:
        with ConexionBD() as conn:
            while True:
                print("\n=== SISTEMA DE GESTIÓN DE EMPLEADOS ===\n"
                      " 1) Departamentos\n 2) Empleados\n 3) Proyectos\n 4) Registro de tiempo\n 0) Salir")
                op = input("Opción: ").strip()
                if op == "1":
                    menu_departamentos(conn)
                elif op == "2":
                    menu_empleados(conn)
                elif op == "3":
                    menu_proyectos(conn)
                elif op == "4":
                    menu_registros(conn)
                elif op == "0":
                    break
                else:
                    print("Opción inválida")
    except ErrorBD as e:
        print(f"Error de conexión: {e}")


if __name__ == "__main__":
    main()