# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librer�a de QUILL (versi�n de Spectrum). Parte com�n a editor, compilador e int�rprete
# Copyright (C) 2010, 2018-2020 Jos� Manuel Ferrer Ortiz
#
# *****************************************************************************
# *                                                                           *
# *  This program is free software; you can redistribute it and/or modify it  *
# *  under the terms of the GNU General Public License version 2, as          *
# *  published by the Free Software Foundation.                               *
# *                                                                           *
# *  This program is distributed in the hope that it will be useful, but      *
# *  WITHOUT ANY WARRANTY; without even the implied warranty of               *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU         *
# *  General Public License version 2 for more details.                       *
# *                                                                           *
# *  You should have received a copy of the GNU General Public License        *
# *  version 2 along with this program; if not, write to the Free Software    *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA  *
# *                                                                           *
# *****************************************************************************


# Variables que se exportan (fuera del paquete)

# S�lo se usar� este m�dulo de condactos
mods_condactos = ('condactos_quill',)

conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Palabras de los objetos
num_objetos    = [0]  # N�mero de objetos (en lista para pasar por referencia)
tablas_proceso = []   # Tablas de proceso (la de estado y la de eventos)
vocabulario    = []   # Vocabulario

# Identificadores (para hacer el c�digo m�s legible) predefinidos
ids_locs = {  0 : 'INICIAL',
                  'INICIAL'    :   0,
            252 : 'NO_CREADOS',
                  'NO_CREADOS' : 252,
            253 : 'PUESTOS',
                  'PUESTOS'    : 253,
            254 : 'LLEVADOS',
                  'LLEVADOS'   : 254}

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = ()  # Ninguna, de momento
# Funci�n que crea una nueva base de datos (vac�a)
func_nueva = 'nueva_bd'

# Mensajes de sistema predefinidos
nuevos_sys = (
  'Todo est� oscuro. No veo nada.',
  'Tambi�n veo:-',
  '\nEspero tu orden.',
  '\nEstoy listo para recibir instrucciones.',
  '\nDime qu� hago.',
  '\nDame tu orden.',
  'Lo siento, no entiendo eso. Intenta otras palabras.',
  'No puedo ir en esa direcci�n.',
  'No puedo.',
  'Llevo conmigo:-',
  '(puesto)',
  'Nada de nada.',
  '�Seguro que quieres salir?',
  '\nFIN DEL JUEGO\n�Quieres volver a probar?',
  'Adi�s. Que tengas un buen d�a.',
  'De acuerdo.',
  'Pulsa cualquier tecla para continuar',
  'He cogido ',
  ' turno',
  's',
  '.',
  'Has completado el ',
  '%',
  'No lo llevo puesto.',
  'No puedo. Mis manos est�n llenas.',
  'Ya lo tengo.',
  'No est� aqu�',
  'No puedo cargar m�s cosas.',
  'No lo tengo.',
  'Ya lo llevo puesto.',
  'S',
  'N'
)


# Constantes que se exportan (fuera del paquete)

INDIRECCION      = False    # El parser no soporta indirecci�n (para el IDE)
MAX_LOCS         = 252      # N�mero m�ximo de localidades posible
MAX_MSGS_USR     = 255      # N�mero m�ximo de mensajes de usuario posible
MAX_PROCS        = 2        # N�mero m�ximo de tablas de proceso posible
NUM_ATRIBUTOS    = [0]      # N�mero de atributos de objeto
NUM_BANDERAS     = 38       # N�mero de banderas del parser, para compatibilidad. XXX: considerar usar constantes para las banderas del sistema
NUM_BANDERAS_ACC = 33       # N�mero de banderas del parser accesibles por el programador
NOMBRE_SISTEMA   = 'QUILL'  # Nombre de este sistema
# Nombres de las primeras tablas de proceso (para el IDE)
NOMBRES_PROCS    = ('Tabla de estado', 'Tabla de eventos')
TIPOS_PAL        = ('Palabra',)  # Nombres de los tipos de palabra (para el IDE)


# Diccionarios de condactos

# El formato es el siguiente:
# c�digo : (nombre, lista_par�metros)
# Donde lista_par�metros es una lista con el tipo de cada par�metro
# Y los tipos de los par�metros se definen as�:
# 0          : N�mero de bandera (flagno), de 0 a 255
# 1          : N�mero de localidad (locno), de 0 a num_localidades
# 2          : N�mero de mensaje de usuario (mesno), de 0 a num_msgs_usuario
# 3          : N�mero de mensaje de sistema (sysno), de 0 a num_msgs_sistema
# 4          : N�mero de objeto (objno), de 0 a num_objetos
# 5          : N�mero de tabla de proceso (prono), de 0 a num_procesos
# 10-16      : N�mero de palabra de vocabulario (word), de tipo n�mero - 10,
#              siendo: 0 verbo, 1 adverbio, 2 nombre, 3 adjetivo, 4 preposici�n,
#              5 conjunci�n, 6 pronombre
# (m�n, m�x) : Rango de valores, de m�n a m�x

# Diccionario de condiciones
condiciones = {
   0 : ('AT',      (      1,         )),
   1 : ('NOTAT',   (      1,         )),
   2 : ('ATGT',    (      1,         )),
   3 : ('ATLT',    (      1,         )),
   4 : ('PRESENT', (      4,         )),
   5 : ('ABSENT',  (      4,         )),
   6 : ('WORN',    (      4,         )),
   7 : ('NOTWORN', (      4,         )),
   8 : ('CARRIED', (      4,         )),
   9 : ('NOTCARR', (      4,         )),
  10 : ('CHANCE',  ((1, 99),         )),  # FIXME: Comprobar si sirven 0 y 100
  11 : ('ZERO',    (      0,         )),
  12 : ('NOTZERO', (      0,         )),
  13 : ('EQ',      (      0, (0, 255))),
  14 : ('GT',      (      0, (0, 255))),
  15 : ('LT',      (      0, (0, 255)))
}

# Diccionario de acciones
# TODO: A�adir los que falten
acciones = {
   0 : ('INVEN',   ()                  ),
   1 : ('DESC',    ()                  ),
   2 : ('QUIT',    ()                  ),
   3 : ('END',     ()                  ),
   4 : ('DONE',    ()                  ),
   5 : ('OK',      ()                  ),
   6 : ('ANYKEY',  ()                  ),
   7 : ('SAVE',    ()                  ),
   8 : ('LOAD',    ()                  ),
   9 : ('TURNS',   ()                  ),
  10 : ('SCORE',   ()                  ),
  17 : ('PAUSE',   ((0, 255),         )),
  21 : ('GOTO',    (       1,         )),
  22 : ('MESSAGE', (       2,         )),
  23 : ('REMOVE',  (       4,         )),
  24 : ('GET',     (       4,         )),
  25 : ('DROP',    (       4,         )),
  26 : ('WEAR',    (       4,         )),
  27 : ('DESTROY', (       4,         )),
  28 : ('CREATE',  (       4,         )),
  29 : ('SWAP',    (       4,        4)),
  31 : ('SET',     (       0,         )),
  32 : ('CLEAR',   (       0,         )),
  33 : ('PLUS',    (       0, (0, 255))),
  34 : ('MINUS',   (       0, (0, 255))),
  35 : ('LET',     (       0, (0, 255)))
}


# Crea una nueva base de datos de The Quill (versi�n de Spectrum)
def nueva_bd ():
  # Creamos la localidad 0
  desc_locs.append  ('Descripci�n de la localidad 0, la inicial.')
  conexiones.append ([])  # Ninguna conexi�n en esta localidad
  # Creamos una palabra para el objeto 0
  vocabulario.append(('luz', 13, 0))  # 0 es el tipo de palabra
  # Creamos el objeto 0
  desc_objs.append      ('Descripci�n del objeto 0, emisor de luz.')
  locs_iniciales.append (ids_locs['NO_CREADOS'])
  nombres_objs.append   (13)
  num_objetos = 1
  # Creamos el mensaje de usuario 0
  msgs_usr.append ('Texto del mensaje 0.')
  # Ponemos los mensajes de sistema predefinidos
  for mensaje in nuevos_sys:
    msgs_sys.append (mensaje)
  # Creamos la tabla de estado y la de eventos
  tablas_proceso.append (([[], []]))
  tablas_proceso.append (([[], []]))
