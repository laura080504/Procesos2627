"""Plan 406 del Grado en Ingeniería Informática, campus de Albacete.

Las materias comunes y las cuatro menciones son las del plan publicado
por la UCLM (BOE de 27/10/2020). Cada curso vive en su propia tabla.
"""

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura

P = CursoAsignatura.PRIMERO
S = CursoAsignatura.SEGUNDO
T = CursoAsignatura.TERCERO
C = CursoAsignatura.CUARTO


def _fila(codigo: str, nombre: str, nombre_ingles: str, curso: CursoAsignatura, cuatrimestre: int, creditos: int = 6) -> Asignatura:
    return Asignatura(codigo, nombre, nombre_ingles, curso, creditos, cuatrimestre)


CATALOGO_INFORMATICA_ALBACETE: tuple[Asignatura, ...] = (
    _fila("42300", "Cálculo y Métodos Numéricos", "Calculus and Numerical Methods", P, 1),
    _fila("42301", "Fundamentos Físicos de la Informática", "Physical Foundations of Computer Science", P, 1),
    _fila("42302", "Fundamentos de Programación I", "Programming Fundamentals I", P, 1),
    _fila("42303", "Tecnología de Computadores", "Computer Technology", P, 1),
    _fila("42304", "Fundamentos de Gestión Empresarial", "Fundamentals of Business Management", P, 1),
    _fila("42305", "Álgebra y Matemática Discreta", "Algebra and Discrete Mathematics", P, 2),
    _fila("42306", "Fundamentos de Programación II", "Programming Fundamentals II", P, 2),
    _fila("42307", "Estructura de Computadores", "Computer Structure", P, 2),
    _fila("42308", "Redes de Computadores I", "Computer Networks I", P, 2),
    _fila("42309", "Sistemas de Información", "Information Systems", P, 2),
    _fila("42310", "Lógica", "Logic", S, 1),
    _fila("42311", "Organización de Computadores", "Computer Organization", S, 1),
    _fila("42312", "Estructura de Datos", "Data Structures", S, 1),
    _fila("42313", "Sistemas Operativos I", "Operating Systems I", S, 1),
    _fila("42314", "Ingeniería del Software I", "Software Engineering I", S, 1),
    _fila("42315", "Estadística", "Statistics", S, 2),
    _fila("42316", "Metodología de la Programación", "Programming Methodology", S, 2),
    _fila("42317", "Programación Concurrente y Tiempo Real", "Concurrent and Real-Time Programming", S, 2),
    _fila("42318", "Redes de Computadores II", "Computer Networks II", S, 2),
    _fila("42319", "Bases de Datos", "Databases", S, 2),
    _fila("42320", "Interacción Persona-Ordenador I", "Human-Computer Interaction I", T, 1),
    _fila("42321", "Sistemas Inteligentes", "Intelligent Systems", T, 1),
    _fila("42322", "Sistemas Distribuidos", "Distributed Systems", T, 1),
    _fila("42323", "Arquitectura de Computadores", "Computer Architecture", T, 1),
    _fila("42324", "Ingeniería del Software II", "Software Engineering II", T, 1),
    _fila("42325", "Aspectos Profesionales de la Informática", "Professional Aspects of Computer Science", T, 2),
    _fila("42326", "Ingeniería de Requisitos", "Requirements Engineering", T, 2),
    _fila("42327", "Diseño de Software", "Software Design", T, 2),
    _fila("42328", "Desarrollo de Bases de Datos", "Database Development", T, 2),
    _fila("42329", "Sistemas de Información Empresariales", "Enterprise Information Systems", T, 2),
    _fila("42334", "Sistemas Operativos II", "Operating Systems II", T, 2),
    _fila("42335", "Diseño de sistemas basados en Microprocesador", "Microprocessor-Based Systems Design", T, 2),
    _fila("42336", "Gestión y Administración de Redes", "Network Management and Administration", T, 2),
    _fila("42337", "Diseño de Infraestructura de Red", "Network Infrastructure Design", T, 2),
    _fila("42342", "Teoría de Autómatas y Computación", "Automata Theory and Computation", T, 2),
    _fila("42343", "Programación Declarativa", "Declarative Programming", T, 2),
    _fila("42344", "Diseño de Algoritmos", "Algorithm Design", T, 2),
    _fila("42345", "Sistemas Basados en el Conocimiento", "Knowledge-Based Systems", T, 2),
    _fila("42350", "Integración de Sistemas Informáticos", "Information Systems Integration", T, 2),
    _fila("42351", "Interacción Persona-Ordenador II", "Human-Computer Interaction II", T, 2),
    _fila("42352", "Diseño y Gestión de Redes", "Network Design and Management", T, 2),
    _fila("42353", "Gestión de Sistemas de Información", "Information Systems Management", T, 2),
    _fila("42330", "Procesos de Ingeniería del Software", "Software Engineering Processes", C, 1),
    _fila("42331", "Calidad de Sistemas Software", "Software Systems Quality", C, 1),
    _fila("42332", "Gestión de Proyectos Software", "Software Project Management", C, 1),
    _fila("42333", "Seguridad de Sistemas Software", "Software Systems Security", C, 1),
    _fila("42338", "Computadores Avanzados", "Advanced Computers", C, 1),
    _fila("42339", "Sistemas Empotrados", "Embedded Systems", C, 1),
    _fila("42340", "Seguridad en Redes", "Network Security", C, 1),
    _fila("42341", "Planificación e Integración de Sistemas y Servicios", "Systems and Services Planning and Integration", C, 1),
    _fila("42346", "Sistemas Multiagentes", "Multi-Agent Systems", C, 1),
    _fila("42347", "Diseño de Sistemas Interactivos", "Interactive Systems Design", C, 1),
    _fila("42348", "Minería de Datos", "Data Mining", C, 1),
    _fila("42349", "Procesadores de Lenguajes", "Language Processors", C, 1),
    _fila("42354", "Tecnologías y Sistemas Web", "Web Technologies and Systems", C, 1),
    _fila("42355", "Comercio Electrónico", "Electronic Commerce", C, 1),
    _fila("42356", "Multimedia", "Multimedia", C, 1),
    _fila("42357", "Seguridad en Sistemas Informáticos", "Computer Systems Security", C, 1),
    _fila("42358", "Trabajo Fin de Grado", "Final Degree Project", C, 2, 12),
    _fila("42366", "Auditoría de Sistemas de Información", "Information Systems Auditing", C, 2),
    _fila("42373", "Diseño VLSI", "VLSI Design", C, 2),
    _fila("42381", "Ingeniería de Negocio", "Business Engineering", C, 1),
    _fila("42382", "Bases de Datos Avanzadas", "Advanced Databases", C, 2),
    _fila("42386", "Desarrollo de Sistemas Web", "Web Systems Development", C, 2),
    _fila("42387", "Análisis Forense Informático", "Computer Forensics", C, 2),
    _fila("42392", "Técnicas de Aprendizaje Automático", "Machine Learning Techniques", C, 1),
    _fila("42393", "Gráficos por Computador", "Computer Graphics", C, 2),
    _fila("42395", "Redes y Servicios Móviles", "Mobile Networks and Services", C, 2),
    _fila("42396", "Aplicaciones Distribuidas en Internet", "Distributed Internet Applications", C, 1),
    _fila("42397", "Inglés Técnico I", "Technical English I", C, 1),
    _fila("42398", "Inglés Técnico II", "Technical English II", C, 2),
    _fila("42399", "Prácticas en Empresas", "Company Internship", C, 2, 12),
)
