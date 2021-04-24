# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funci�n sustituta de print, compatible con Python 2.X y 3.X
# Copyright (C) 2010 Jos� Manuel Ferrer Ortiz
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

# La versi�n de Python ser� al menos la 2.0 (es la versi�n que introdujo la
# tupla version_info del m�dulo sys)

from sys import version_info


# Con try... except SyntaxError hacemos que el c�digo pueda ser visto correcto
# por el analizador sint�ctico independientemente de la versi�n de Python

if version_info[0] < 3:
  # La versi�n de Python es 2.X
  if version_info[1] < 6:
    # La versi�n de Python es menor que la 2.6
    try:
      from prn_2 import prn
    except SyntaxError:
      pass
  else:
    # La versi�n de Python es mayor que la 2.5
    try:
      from prn_26 import prn
    except SyntaxError:
      pass
else:
  # La versi�n de Python es 3.X
  try:
    from prn_3 import prn
  except SyntaxError:
    pass
