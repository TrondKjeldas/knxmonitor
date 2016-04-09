# 
#   EIBD client library
#   Copyright (C) 2005-2010 Martin Koegler <mkoegler@auto.tuwien.ac.at>
# 
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
# 
#   In addition to the permissions in the GNU General Public License, 
#   you may link the compiled version of this file into combinations
#   with other programs, and distribute those combinations without any 
#   restriction coming from the use of this file. (The General Public 
#   License restrictions do apply in other respects; for example, they 
#   cover modification of the file, and distribution when not linked into 
#   a combine executable.)
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 

import errno;
import socket;

class EIBBuffer:
  def __init__(self, buf = []):
    self.buffer = buf

class EIBAddr:
  def __init__(self, value = 0):
    self.data = value

class EIBInt8:
  def __init__(self, value = 0):
    self.data = value

class EIBInt16:
  def __init__(self, value = 0):
    self.data = value

class EIBConnection:
  def __init__(self):
    self.data = []
    self.readlen = 0
    self.datalen = 0
    self.fd = None
    self.errno = 0
    self.__complete = None

  def EIBSocketLocal(self, path):
    if self.fd != None:
      self.errno = errno.EUSERS
      return -1
    fd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    fd.connect(path)
    self.data = []
    self.readlen = 0
    self.fd = fd
    return 0

  def EIBSocketRemote(self, host, port = 6720):
    if self.fd != None:
      self.errno = errno.EUSERS
      return -1
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd.connect((host, port))
    self.data = []
    self.readlen = 0
    self.fd = fd
    return 0

  def EIBSocketURL(self, url):
    if url[0:6] == 'local:':
      return self.EIBSocketLocal(url[6:])
    if url[0:3] == 'ip:':
      parts=url.split(':')
      if (len(parts) == 2):
        parts.append(6720)
      return self.EIBSocketRemote(parts[1], int(parts[2]))
    self.errno = errno.EINVAL
    return -1

  def EIBComplete(self):
    if self.__complete == None:
      self.errno = errno.EINVAL
      return -1
    return self.__complete()

  def EIBClose(self):
    if self.fd == None:
      self.errno = errno.EINVAL
      return -1
    self.fd.close()
    self.fd = None

  def EIBClose_sync(self):
    self.EIBReset()
    return self.EIBClose()

  def __EIB_SendRequest(self, data):
    if self.fd == None:
      self.errno = errno.ECONNRESET
      return -1
    if len(data) < 2 or len(data) > 0xffff:
      self.errno = errno.EINVAL
      return -1
    data = [ (len(data)>>8)&0xff, (len(data))&0xff ] + data
    result = ''
    for i in data:
      result += chr(i)
    self.fd.send(result)
    return 0

  def EIB_Poll_FD(self):
    if self.fd == None:
      self.errno = errno.EINVAL
      return -1
    return self.fd

  def EIB_Poll_Complete(self):
    if self.__EIB_CheckRequest(False) == -1:
      return -1
    if self.readlen < 2 or (self.readlen >= 2 and self.readlen < self.datalen + 2):
      return 0
    return 1

  def __EIB_GetRequest(self):
     while True:
      if self.__EIB_CheckRequest(True) == -1:
        return -1
      if self.readlen >= 2 and self.readlen >= self.datalen + 2:
        self.readlen = 0
        return 0

  def __EIB_CheckRequest(self, block):
    if self.fd == None:
      self.errno = errno.ECONNRESET
      return -1
    if self.readlen == 0:
      self.head = []
      self.data = []
    if self.readlen < 2:
      self.fd.setblocking(block)
      result = self.fd.recv (2-self.readlen)
      for a in result:
        self.head.append(ord(a))
      self.readlen += len(result)
    if self.readlen < 2:
      return 0
    self.datalen = (self.head[0] << 8) | self.head[1]
    if self.readlen < self.datalen + 2:
      self.fd.setblocking(block)
      result = self.fd.recv (self.datalen + 2 -self.readlen)
      for a in result:
        self.data.append(ord(a))
      self.readlen += len(result)
    return 0      

  def __EIBGetAPDU_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 37 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIBGetAPDU_async(self, buf):
    ibuf = [0] * 2;
    self.buf = buf
    self.__complete = self.__EIBGetAPDU_Complete;
    return 0


  def EIBGetAPDU(self, buf):
    if self.EIBGetAPDU_async (buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBGetAPDU_Src_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 37 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    if self.ptr5 != None:
      self.ptr5.data = (((self.data[2])<<8)|(self.data[2+1]))
    self.buf.buffer = self.data[4:]
    return len(self.buf.buffer)


  def EIBGetAPDU_Src_async(self, buf, src):
    ibuf = [0] * 2;
    self.buf = buf
    self.ptr5 = src
    self.__complete = self.__EIBGetAPDU_Src_Complete;
    return 0


  def EIBGetAPDU_Src(self, buf, src):
    if self.EIBGetAPDU_Src_async (buf, src) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBGetBusmonitorPacket_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 20 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIBGetBusmonitorPacket_async(self, buf):
    ibuf = [0] * 2;
    self.buf = buf
    self.__complete = self.__EIBGetBusmonitorPacket_Complete;
    return 0


  def EIBGetBusmonitorPacket(self, buf):
    if self.EIBGetBusmonitorPacket_async (buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBGetGroup_Src_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 39 or len(self.data) < 6:
      self.errno = errno.ECONNRESET
      return -1
    if self.ptr5 != None:
      self.ptr5.data = (((self.data[2])<<8)|(self.data[2+1]))
    if self.ptr6 != None:
      self.ptr6.data = (((self.data[4])<<8)|(self.data[4+1]))
    self.buf.buffer = self.data[6:]
    return len(self.buf.buffer)


  def EIBGetGroup_Src_async(self, buf, src, dest):
    ibuf = [0] * 2;
    self.buf = buf
    self.ptr5 = src
    self.ptr6 = dest
    self.__complete = self.__EIBGetGroup_Src_Complete;
    return 0


  def EIBGetGroup_Src(self, buf, src, dest):
    if self.EIBGetGroup_Src_async (buf, src, dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBGetTPDU_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 37 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    if self.ptr5 != None:
      self.ptr5.data = (((self.data[2])<<8)|(self.data[2+1]))
    self.buf.buffer = self.data[4:]
    return len(self.buf.buffer)


  def EIBGetTPDU_async(self, buf, src):
    ibuf = [0] * 2;
    self.buf = buf
    self.ptr5 = src
    self.__complete = self.__EIBGetTPDU_Complete;
    return 0


  def EIBGetTPDU(self, buf, src):
    if self.EIBGetTPDU_async (buf, src) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_Cache_Clear_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 114 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_Cache_Clear_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 114
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_Cache_Clear_Complete;
    return 0


  def EIB_Cache_Clear(self):
    if self.EIB_Cache_Clear_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_Cache_Disable_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 113 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_Cache_Disable_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 113
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_Cache_Disable_Complete;
    return 0


  def EIB_Cache_Disable(self):
    if self.EIB_Cache_Disable_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_Cache_Enable_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 1:
      self.errno = errno.EBUSY
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 112 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_Cache_Enable_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 112
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_Cache_Enable_Complete;
    return 0


  def EIB_Cache_Enable(self):
    if self.EIB_Cache_Enable_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_Cache_Read_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 117 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    if (((self.data[4])<<8)|(self.data[4+1])) == 0:
      self.errno = errno.ENODEV
      return -1
    if len(self.data) <= 6:
      self.errno = errno.ENOENT
      return -1
    if self.ptr5 != None:
      self.ptr5.data = (((self.data[2])<<8)|(self.data[2+1]))
    self.buf.buffer = self.data[6:]
    return len(self.buf.buffer)


  def EIB_Cache_Read_async(self, dst, src, buf):
    ibuf = [0] * 4;
    self.buf = buf
    self.ptr5 = src
    ibuf[2] = ((dst>>8)&0xff)
    ibuf[3] = ((dst)&0xff)
    ibuf[0] = 0
    ibuf[1] = 117
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_Cache_Read_Complete;
    return 0


  def EIB_Cache_Read(self, dst, src, buf):
    if self.EIB_Cache_Read_async (dst, src, buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_Cache_Read_Sync_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 116 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    if (((self.data[4])<<8)|(self.data[4+1])) == 0:
      self.errno = errno.ENODEV
      return -1
    if len(self.data) <= 6:
      self.errno = errno.ENOENT
      return -1
    if self.ptr5 != None:
      self.ptr5.data = (((self.data[2])<<8)|(self.data[2+1]))
    self.buf.buffer = self.data[6:]
    return len(self.buf.buffer)


  def EIB_Cache_Read_Sync_async(self, dst, src, buf, age):
    ibuf = [0] * 6;
    self.buf = buf
    self.ptr5 = src
    ibuf[2] = ((dst>>8)&0xff)
    ibuf[3] = ((dst)&0xff)
    ibuf[4] = ((age>>8)&0xff)
    ibuf[5] = ((age)&0xff)
    ibuf[0] = 0
    ibuf[1] = 116
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_Cache_Read_Sync_Complete;
    return 0


  def EIB_Cache_Read_Sync(self, dst, src, buf, age):
    if self.EIB_Cache_Read_Sync_async (dst, src, buf, age) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_Cache_Remove_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 115 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_Cache_Remove_async(self, dest):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[0] = 0
    ibuf[1] = 115
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_Cache_Remove_Complete;
    return 0


  def EIB_Cache_Remove(self, dest):
    if self.EIB_Cache_Remove_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_LoadImage_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 99 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    return (((self.data[2])<<8)|(self.data[2+1]))


  def EIB_LoadImage_async(self, image):
    ibuf = [0] * 2;
    if len(image) < 0:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(image)
    ibuf += image
    ibuf[0] = 0
    ibuf[1] = 99
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_LoadImage_Complete;
    return 0


  def EIB_LoadImage(self, image):
    if self.EIB_LoadImage_async (image) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Authorize_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 87 or len(self.data) < 3:
      self.errno = errno.ECONNRESET
      return -1
    return self.data[2]


  def EIB_MC_Authorize_async(self, key):
    ibuf = [0] * 6;
    if len(key) != 4:
      self.errno = errno.EINVAL
      return -1
    ibuf[2:6] = key
    ibuf[0] = 0
    ibuf[1] = 87
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Authorize_Complete;
    return 0


  def EIB_MC_Authorize(self, key):
    if self.EIB_MC_Authorize_async (key) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Connect_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 80 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_Connect_async(self, dest):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[0] = 0
    ibuf[1] = 80
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Connect_Complete;
    return 0


  def EIB_MC_Connect(self, dest):
    if self.EIB_MC_Connect_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Individual_Open_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 73 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_Individual_Open_async(self, dest):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[0] = 0
    ibuf[1] = 73
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Individual_Open_Complete;
    return 0


  def EIB_MC_Individual_Open(self, dest):
    if self.EIB_MC_Individual_Open_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_GetMaskVersion_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 89 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    return (((self.data[2])<<8)|(self.data[2+1]))


  def EIB_MC_GetMaskVersion_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 89
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_GetMaskVersion_Complete;
    return 0


  def EIB_MC_GetMaskVersion(self):
    if self.EIB_MC_GetMaskVersion_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_GetPEIType_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 85 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    return (((self.data[2])<<8)|(self.data[2+1]))


  def EIB_MC_GetPEIType_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 85
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_GetPEIType_Complete;
    return 0


  def EIB_MC_GetPEIType(self):
    if self.EIB_MC_GetPEIType_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Progmode_Off_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 96 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_Progmode_Off_async(self):
    ibuf = [0] * 3;
    ibuf[2] = ((0)&0xff)
    ibuf[0] = 0
    ibuf[1] = 96
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Progmode_Off_Complete;
    return 0


  def EIB_MC_Progmode_Off(self):
    if self.EIB_MC_Progmode_Off_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Progmode_On_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 96 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_Progmode_On_async(self):
    ibuf = [0] * 3;
    ibuf[2] = ((1)&0xff)
    ibuf[0] = 0
    ibuf[1] = 96
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Progmode_On_Complete;
    return 0


  def EIB_MC_Progmode_On(self):
    if self.EIB_MC_Progmode_On_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Progmode_Status_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 96 or len(self.data) < 3:
      self.errno = errno.ECONNRESET
      return -1
    return self.data[2]


  def EIB_MC_Progmode_Status_async(self):
    ibuf = [0] * 3;
    ibuf[2] = ((3)&0xff)
    ibuf[0] = 0
    ibuf[1] = 96
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Progmode_Status_Complete;
    return 0


  def EIB_MC_Progmode_Status(self):
    if self.EIB_MC_Progmode_Status_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Progmode_Toggle_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 96 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_Progmode_Toggle_async(self):
    ibuf = [0] * 3;
    ibuf[2] = ((2)&0xff)
    ibuf[0] = 0
    ibuf[1] = 96
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Progmode_Toggle_Complete;
    return 0


  def EIB_MC_Progmode_Toggle(self):
    if self.EIB_MC_Progmode_Toggle_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_PropertyDesc_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 97 or len(self.data) < 6:
      self.errno = errno.ECONNRESET
      return -1
    if self.ptr2 != None:
      self.ptr2.data = self.data[2]
    if self.ptr4 != None:
      self.ptr4.data = (((self.data[3])<<8)|(self.data[3+1]))
    if self.ptr3 != None:
      self.ptr3.data = self.data[5]
    return 0


  def EIB_MC_PropertyDesc_async(self, obj, propertyno, proptype, max_nr_of_elem, access):
    ibuf = [0] * 4;
    self.ptr2 = proptype
    self.ptr4 = max_nr_of_elem
    self.ptr3 = access
    ibuf[2] = ((obj)&0xff)
    ibuf[3] = ((propertyno)&0xff)
    ibuf[0] = 0
    ibuf[1] = 97
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_PropertyDesc_Complete;
    return 0


  def EIB_MC_PropertyDesc(self, obj, propertyno, proptype, max_nr_of_elem, access):
    if self.EIB_MC_PropertyDesc_async (obj, propertyno, proptype, max_nr_of_elem, access) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_PropertyRead_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 83 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIB_MC_PropertyRead_async(self, obj, propertyno, start, nr_of_elem, buf):
    ibuf = [0] * 7;
    self.buf = buf
    ibuf[2] = ((obj)&0xff)
    ibuf[3] = ((propertyno)&0xff)
    ibuf[4] = ((start>>8)&0xff)
    ibuf[5] = ((start)&0xff)
    ibuf[6] = ((nr_of_elem)&0xff)
    ibuf[0] = 0
    ibuf[1] = 83
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_PropertyRead_Complete;
    return 0


  def EIB_MC_PropertyRead(self, obj, propertyno, start, nr_of_elem, buf):
    if self.EIB_MC_PropertyRead_async (obj, propertyno, start, nr_of_elem, buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_PropertyScan_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 98 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIB_MC_PropertyScan_async(self, buf):
    ibuf = [0] * 2;
    self.buf = buf
    ibuf[0] = 0
    ibuf[1] = 98
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_PropertyScan_Complete;
    return 0


  def EIB_MC_PropertyScan(self, buf):
    if self.EIB_MC_PropertyScan_async (buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_PropertyWrite_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 84 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIB_MC_PropertyWrite_async(self, obj, propertyno, start, nr_of_elem, buf, res):
    ibuf = [0] * 7;
    ibuf[2] = ((obj)&0xff)
    ibuf[3] = ((propertyno)&0xff)
    ibuf[4] = ((start>>8)&0xff)
    ibuf[5] = ((start)&0xff)
    ibuf[6] = ((nr_of_elem)&0xff)
    if len(buf) < 0:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(buf)
    ibuf += buf
    self.buf = res
    ibuf[0] = 0
    ibuf[1] = 84
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_PropertyWrite_Complete;
    return 0


  def EIB_MC_PropertyWrite(self, obj, propertyno, start, nr_of_elem, buf, res):
    if self.EIB_MC_PropertyWrite_async (obj, propertyno, start, nr_of_elem, buf, res) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_ReadADC_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 86 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    if self.ptr1 != None:
      self.ptr1.data = (((self.data[2])<<8)|(self.data[2+1]))
    return 0


  def EIB_MC_ReadADC_async(self, channel, count, val):
    ibuf = [0] * 4;
    self.ptr1 = val
    ibuf[2] = ((channel)&0xff)
    ibuf[3] = ((count)&0xff)
    ibuf[0] = 0
    ibuf[1] = 86
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_ReadADC_Complete;
    return 0


  def EIB_MC_ReadADC(self, channel, count, val):
    if self.EIB_MC_ReadADC_async (channel, count, val) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Read_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 81 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIB_MC_Read_async(self, addr, buf_len, buf):
    ibuf = [0] * 6;
    self.buf = buf
    ibuf[2] = ((addr>>8)&0xff)
    ibuf[3] = ((addr)&0xff)
    ibuf[4] = ((buf_len>>8)&0xff)
    ibuf[5] = ((buf_len)&0xff)
    ibuf[0] = 0
    ibuf[1] = 81
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Read_Complete;
    return 0


  def EIB_MC_Read(self, addr, buf_len, buf):
    if self.EIB_MC_Read_async (addr, buf_len, buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Restart_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 90 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_Restart_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 90
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Restart_Complete;
    return 0


  def EIB_MC_Restart(self):
    if self.EIB_MC_Restart_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_SetKey_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 2:
      self.errno = errno.EPERM
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 88 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_MC_SetKey_async(self, key, level):
    ibuf = [0] * 7;
    if len(key) != 4:
      self.errno = errno.EINVAL
      return -1
    ibuf[2:6] = key
    ibuf[6] = ((level)&0xff)
    ibuf[0] = 0
    ibuf[1] = 88
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_SetKey_Complete;
    return 0


  def EIB_MC_SetKey(self, key, level):
    if self.EIB_MC_SetKey_async (key, level) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Write_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 68:
      self.errno = errno.EIO
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 82 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return self.sendlen


  def EIB_MC_Write_async(self, addr, buf):
    ibuf = [0] * 6;
    ibuf[2] = ((addr>>8)&0xff)
    ibuf[3] = ((addr)&0xff)
    ibuf[4] = (((len(buf))>>8)&0xff)
    ibuf[5] = (((len(buf)))&0xff)
    if len(buf) < 0:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(buf)
    ibuf += buf
    ibuf[0] = 0
    ibuf[1] = 82
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Write_Complete;
    return 0


  def EIB_MC_Write(self, addr, buf):
    if self.EIB_MC_Write_async (addr, buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_MC_Write_Plain_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 91 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return self.sendlen


  def EIB_MC_Write_Plain_async(self, addr, buf):
    ibuf = [0] * 6;
    ibuf[2] = ((addr>>8)&0xff)
    ibuf[3] = ((addr)&0xff)
    ibuf[4] = (((len(buf))>>8)&0xff)
    ibuf[5] = (((len(buf)))&0xff)
    if len(buf) < 0:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(buf)
    ibuf += buf
    ibuf[0] = 0
    ibuf[1] = 91
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_MC_Write_Plain_Complete;
    return 0


  def EIB_MC_Write_Plain(self, addr, buf):
    if self.EIB_MC_Write_Plain_async (addr, buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_GetMaskVersion_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 49 or len(self.data) < 4:
      self.errno = errno.ECONNRESET
      return -1
    return (((self.data[2])<<8)|(self.data[2+1]))


  def EIB_M_GetMaskVersion_async(self, dest):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[0] = 0
    ibuf[1] = 49
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_GetMaskVersion_Complete;
    return 0


  def EIB_M_GetMaskVersion(self, dest):
    if self.EIB_M_GetMaskVersion_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_Progmode_Off_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 48 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_M_Progmode_Off_async(self, dest):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[4] = ((0)&0xff)
    ibuf[0] = 0
    ibuf[1] = 48
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_Progmode_Off_Complete;
    return 0


  def EIB_M_Progmode_Off(self, dest):
    if self.EIB_M_Progmode_Off_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_Progmode_On_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 48 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_M_Progmode_On_async(self, dest):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[4] = ((1)&0xff)
    ibuf[0] = 0
    ibuf[1] = 48
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_Progmode_On_Complete;
    return 0


  def EIB_M_Progmode_On(self, dest):
    if self.EIB_M_Progmode_On_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_Progmode_Status_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 48 or len(self.data) < 3:
      self.errno = errno.ECONNRESET
      return -1
    return self.data[2]


  def EIB_M_Progmode_Status_async(self, dest):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[4] = ((3)&0xff)
    ibuf[0] = 0
    ibuf[1] = 48
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_Progmode_Status_Complete;
    return 0


  def EIB_M_Progmode_Status(self, dest):
    if self.EIB_M_Progmode_Status_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_Progmode_Toggle_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 48 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_M_Progmode_Toggle_async(self, dest):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[4] = ((2)&0xff)
    ibuf[0] = 0
    ibuf[1] = 48
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_Progmode_Toggle_Complete;
    return 0


  def EIB_M_Progmode_Toggle(self, dest):
    if self.EIB_M_Progmode_Toggle_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_ReadIndividualAddresses_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 50 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    self.buf.buffer = self.data[2:]
    return len(self.buf.buffer)


  def EIB_M_ReadIndividualAddresses_async(self, buf):
    ibuf = [0] * 2;
    self.buf = buf
    ibuf[0] = 0
    ibuf[1] = 50
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_ReadIndividualAddresses_Complete;
    return 0


  def EIB_M_ReadIndividualAddresses(self, buf):
    if self.EIB_M_ReadIndividualAddresses_async (buf) == -1:
      return -1
    return self.EIBComplete ()

  def __EIB_M_WriteIndividualAddress_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 65:
      self.errno = errno.EADDRINUSE
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 67:
      self.errno = errno.ETIMEDOUT
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 66:
      self.errno = errno.EADDRNOTAVAIL
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 64 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIB_M_WriteIndividualAddress_async(self, dest):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[0] = 0
    ibuf[1] = 64
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIB_M_WriteIndividualAddress_Complete;
    return 0


  def EIB_M_WriteIndividualAddress(self, dest):
    if self.EIB_M_WriteIndividualAddress_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenBusmonitor_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 1:
      self.errno = errno.EBUSY
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 16 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenBusmonitor_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 16
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenBusmonitor_Complete;
    return 0


  def EIBOpenBusmonitor(self):
    if self.EIBOpenBusmonitor_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenBusmonitorText_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 1:
      self.errno = errno.EBUSY
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 17 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenBusmonitorText_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 17
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenBusmonitorText_Complete;
    return 0


  def EIBOpenBusmonitorText(self):
    if self.EIBOpenBusmonitorText_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpen_GroupSocket_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 38 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpen_GroupSocket_async(self, write_only):
    ibuf = [0] * 5;
    if write_only != 0:
      ibuf[4] = 0xff
    else:
      ibuf[4] = 0x00
    ibuf[0] = 0
    ibuf[1] = 38
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpen_GroupSocket_Complete;
    return 0


  def EIBOpen_GroupSocket(self, write_only):
    if self.EIBOpen_GroupSocket_async (write_only) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenT_Broadcast_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 35 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenT_Broadcast_async(self, write_only):
    ibuf = [0] * 5;
    if write_only != 0:
      ibuf[4] = 0xff
    else:
      ibuf[4] = 0x00
    ibuf[0] = 0
    ibuf[1] = 35
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenT_Broadcast_Complete;
    return 0


  def EIBOpenT_Broadcast(self, write_only):
    if self.EIBOpenT_Broadcast_async (write_only) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenT_Connection_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 32 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenT_Connection_async(self, dest):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    ibuf[0] = 0
    ibuf[1] = 32
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenT_Connection_Complete;
    return 0


  def EIBOpenT_Connection(self, dest):
    if self.EIBOpenT_Connection_async (dest) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenT_Group_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 34 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenT_Group_async(self, dest, write_only):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    if write_only != 0:
      ibuf[4] = 0xff
    else:
      ibuf[4] = 0x00
    ibuf[0] = 0
    ibuf[1] = 34
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenT_Group_Complete;
    return 0


  def EIBOpenT_Group(self, dest, write_only):
    if self.EIBOpenT_Group_async (dest, write_only) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenT_Individual_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 33 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenT_Individual_async(self, dest, write_only):
    ibuf = [0] * 5;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    if write_only != 0:
      ibuf[4] = 0xff
    else:
      ibuf[4] = 0x00
    ibuf[0] = 0
    ibuf[1] = 33
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenT_Individual_Complete;
    return 0


  def EIBOpenT_Individual(self, dest, write_only):
    if self.EIBOpenT_Individual_async (dest, write_only) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenT_TPDU_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 36 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenT_TPDU_async(self, src):
    ibuf = [0] * 5;
    ibuf[2] = ((src>>8)&0xff)
    ibuf[3] = ((src)&0xff)
    ibuf[0] = 0
    ibuf[1] = 36
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenT_TPDU_Complete;
    return 0


  def EIBOpenT_TPDU(self, src):
    if self.EIBOpenT_TPDU_async (src) == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenVBusmonitor_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 1:
      self.errno = errno.EBUSY
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 18 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenVBusmonitor_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 18
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenVBusmonitor_Complete;
    return 0


  def EIBOpenVBusmonitor(self):
    if self.EIBOpenVBusmonitor_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIBOpenVBusmonitorText_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 1:
      self.errno = errno.EBUSY
      return -1
    if (((self.data[0])<<8)|(self.data[0+1])) != 19 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBOpenVBusmonitorText_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 19
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBOpenVBusmonitorText_Complete;
    return 0


  def EIBOpenVBusmonitorText(self):
    if self.EIBOpenVBusmonitorText_async () == -1:
      return -1
    return self.EIBComplete ()

  def __EIBReset_Complete(self):
    self.__complete = None;
    if self.__EIB_GetRequest() == -1:
      return -1;
    if (((self.data[0])<<8)|(self.data[0+1])) != 4 or len(self.data) < 2:
      self.errno = errno.ECONNRESET
      return -1
    return 0


  def EIBReset_async(self):
    ibuf = [0] * 2;
    ibuf[0] = 0
    ibuf[1] = 4
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    self.__complete = self.__EIBReset_Complete;
    return 0


  def EIBReset(self):
    if self.EIBReset_async () == -1:
      return -1
    return self.EIBComplete ()

  def EIBSendAPDU(self, data):
    ibuf = [0] * 2;
    if len(data) < 2:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(data)
    ibuf += data
    ibuf[0] = 0
    ibuf[1] = 37
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    return self.sendlen


  def EIBSendGroup(self, dest, data):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    if len(data) < 2:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(data)
    ibuf += data
    ibuf[0] = 0
    ibuf[1] = 39
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    return self.sendlen


  def EIBSendTPDU(self, dest, data):
    ibuf = [0] * 4;
    ibuf[2] = ((dest>>8)&0xff)
    ibuf[3] = ((dest)&0xff)
    if len(data) < 2:
      self.errno = errno.EINVAL
      return -1
    self.sendlen = len(data)
    ibuf += data
    ibuf[0] = 0
    ibuf[1] = 37
    if self.__EIB_SendRequest(ibuf) == -1:
      return -1;
    return self.sendlen


IMG_UNKNOWN_ERROR = 0
IMG_UNRECOG_FORMAT = 1
IMG_INVALID_FORMAT = 2
IMG_NO_BCUTYPE = 3
IMG_UNKNOWN_BCUTYPE = 4
IMG_NO_CODE = 5
IMG_NO_SIZE = 6
IMG_LODATA_OVERFLOW = 7
IMG_HIDATA_OVERFLOW = 8
IMG_TEXT_OVERFLOW = 9
IMG_NO_ADDRESS = 10
IMG_WRONG_SIZE = 11
IMG_IMAGE_LOADABLE = 12
IMG_NO_DEVICE_CONNECTION = 13
IMG_MASK_READ_FAILED = 14
IMG_WRONG_MASK_VERSION = 15
IMG_CLEAR_ERROR = 16
IMG_RESET_ADDR_TAB = 17
IMG_LOAD_HEADER = 18
IMG_LOAD_MAIN = 19
IMG_ZERO_RAM = 20
IMG_FINALIZE_ADDR_TAB = 21
IMG_PREPARE_RUN = 22
IMG_RESTART = 23
IMG_LOADED = 24
IMG_NO_START = 25
IMG_WRONG_ADDRTAB = 26
IMG_ADDRTAB_OVERFLOW = 27
IMG_OVERLAP_ASSOCTAB = 28
IMG_OVERLAP_TEXT = 29
IMG_NEGATIV_TEXT_SIZE = 30
IMG_OVERLAP_PARAM = 31
IMG_OVERLAP_EEPROM = 32
IMG_OBJTAB_OVERFLOW = 33
IMG_WRONG_LOADCTL = 34
IMG_UNLOAD_ADDR = 35
IMG_UNLOAD_ASSOC = 36
IMG_UNLOAD_PROG = 37
IMG_LOAD_ADDR = 38
IMG_WRITE_ADDR = 39
IMG_SET_ADDR = 40
IMG_FINISH_ADDR = 41
IMG_LOAD_ASSOC = 42
IMG_WRITE_ASSOC = 43
IMG_SET_ASSOC = 44
IMG_FINISH_ASSOC = 45
IMG_LOAD_PROG = 46
IMG_ALLOC_LORAM = 47
IMG_ALLOC_HIRAM = 48
IMG_ALLOC_INIT = 49
IMG_ALLOC_RO = 50
IMG_ALLOC_EEPROM = 51
IMG_ALLOC_PARAM = 52
IMG_SET_PROG = 53
IMG_SET_TASK_PTR = 54
IMG_SET_OBJ = 55
IMG_SET_TASK2 = 56
IMG_FINISH_PROC = 57
IMG_WRONG_CHECKLIM = 58
IMG_INVALID_KEY = 59
IMG_AUTHORIZATION_FAILED = 60
IMG_KEY_WRITE = 61


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

