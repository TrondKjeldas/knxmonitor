import _eibclient
import types


    #EIBD client library
    #Copyright (C) 2006 Tony Przygienda, Z2 GmbH

    #This program is free software; you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation; either version 2 of the License, or
    #(at your option) any later version.

    #In addition to the permissions in the GNU General Public License,
    #you may link the compiled version of this file into combinations
    #with other programs, and distribute those combinations without any
    #restriction coming from the use of this file. (The General Public
    #License restrictions do apply in other respects; for example, they
    #cover modification of the file, and distribution when not linked into
    #a combine executable.)

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program; if not, write to the Free Software
    #Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


__all__ = [ 'readaddr', 'readgaddr', 'group2string', 'individual2string' ]

def readaddr(addr):
    if addr.find(".") != -1:
	(a,b,c) = addr.split(".")
	return ((int(a) & 0x0f) << 12) | ((int(b) & 0x0f) << 8) | ((int(c) & 0xff))
    return int(addr,16) & 0xffff

def readgaddr(addr):
    if addr.count("/") == 2:
	(a,b,c) = addr.split("/")
	return ((int(a) & 0x1f) << 11) | ((int(b) & 0x07) << 8) | ((int(c) & 0xff))
    elif addr.count("/") == 1:
	(a,b) = addr.split("/")
	return ((int(a) & 0x1f) << 11) | ((int(b) & 0x7FF))
    return int(addr,16) & 0xffff

def group2string(addr):
    return ("%d/%d/%d" % ((addr >> 11) & 0x1f, (addr >> 8) & 0x07, (addr) & 0xff))

def individual2string(addr):
    return ("%d.%d.%d" % ((addr >> 12) & 0x0f, (addr >> 8) & 0x0f, (addr) & 0xff))