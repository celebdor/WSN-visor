"""
This file is part of WSN-visor.

WSN-visor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

WSN-visor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with WSN-visor.  If not, see <http://www.gnu.org/licenses/>.
"""
import random

def AirForceBlue():
    return (0.36, 0.54, 0.66)

def Alizarin():
    return (0.89, 0.15, 0.21)

def Amber():
    return (1.0, 0.75, 0.00)

def AppleGreen():
    return (0.55, 0.71, 0.00)

def ArmyGreen():
    return (0.29, 0.33, 0.13)

def Asparagus():
    return (0.53, 0.66, 0.42)

def Banana():
    return (1.00, 0.82, 0.16)

def BlueViolet():
    return (0.54, 0.17, 0.89)

def Burgundy():
    return (0.50, 0.00, 0.13)

def Bubblegum():
    return (0.99, 0.76, 0.80)

def Byzantine():
    return (0.74, 0.20, 0.64)

def Camel():
    return (0.76, 0.40, 0.62)

def CarrotOrange():
    return (0.93, 0.57, 0.13)

def InchWorm():
    return (0.70, 0.93, 0.36)

def Olive():
    return (0.50, 0.50, 0.00)

def White():
    return (1.00, 1.00, 1.00)

def randColor():
    r = random.randint( 0, 0xFFFFFF )
    return (((r>>16)&0xFF)*1.0/255, ((r>>8)&0xFF)*1.0/255, (r&0xFF)*1.0/255 )

