from datetime import date

from Servidor.Dominio.DominioEntities.aviso_secretaria import AvisoSecretaria
from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria

# Fuente pública: https://esiiab.uclm.es/eventos/
AVISOS_ESIIAB_MUESTRA = (
    AvisoSecretaria(
        titulo="Conferencia «IA simbólica para la composición musical con Prolog»",
        tipo=TipoAvisoSecretaria.CHARLA,
        fecha=date(2026, 5, 15),
        hora="09:45",
        lugar="Salón de Actos ESII",
        url="https://esiiab.uclm.es/eventos/",
        descripcion="Conferencia oficial de la ESIIAB.",
    ),
    AvisoSecretaria(
        titulo="Charla «Estrategias y Herramientas para el Acceso al Mercado de Trabajo»",
        tipo=TipoAvisoSecretaria.CHARLA,
        fecha=date(2026, 5, 12),
        hora="11:30",
        lugar="Salón de Actos ESII",
        url="https://esiiab.uclm.es/noticia/charla-estrategias-y-herramientas-para-el-acceso-al-mercado-de-trabajo-4/",
        descripcion="Orientación laboral impartida por D. Javier Pineda (CIPE).",
    ),
    AvisoSecretaria(
        titulo="Charla «Del código a las estrellas: la informática no tiene límites»",
        tipo=TipoAvisoSecretaria.CHARLA,
        fecha=date(2026, 9, 16),
        hora="12:00",
        lugar="ESII Albacete",
        url="https://esiiab.uclm.es/eventos/",
        descripcion="Charla sobre salidas profesionales del Grado en Ingeniería Informática.",
    ),
    AvisoSecretaria(
        titulo="XVII Edición del Ciclo de Cine «Informática en Pantalla Grande»",
        tipo=TipoAvisoSecretaria.TALLER,
        fecha=date(2026, 9, 23),
        hora="18:00",
        lugar="ESII Albacete",
        url="https://esiiab.uclm.es/eventos/",
        descripcion="Ciclo de cine organizado por la ESII.",
    ),
    AvisoSecretaria(
        titulo="Acto de Graduación 2025-2026",
        tipo=TipoAvisoSecretaria.AVISO,
        fecha=date(2026, 10, 16),
        hora="12:00",
        lugar="Paraninfo Universitario Campus de Albacete",
        url="https://esiiab.uclm.es/eventos/",
        descripcion="Acto oficial de graduación de la ESII.",
    ),
)
