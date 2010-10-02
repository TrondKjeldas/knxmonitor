"""EIBclient module.

   Allows to connect to eibd from bcusdk.

"""


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



__all__ = [ 'EIB_INVALID_REQUEST', 'EIB_CONNECTION_INUSE', 'EIB_PROCESSING_ERROR', 'EIB_CLOSED', 'EIB_OPEN_BUSMONITOR', 'EIB_OPEN_BUSMONITOR_TEXT', 'EIB_OPEN_VBUSMONITOR', 'EIB_OPEN_VBUSMONITOR_TEXT', 'EIB_BUSMONITOR_PACKET', 'EIB_OPEN_T_CONNECTION', 'EIB_OPEN_T_INDIVIDUAL', 'EIB_OPEN_T_GROUP', 'EIB_OPEN_T_BROADCAST', 'EIB_OPEN_T_TPDU', 'EIB_APDU_PACKET', 'EIB_OPEN_GROUPCON', 'EIB_GROUP_PACKET', 'EIB_PROG_MODE', 'EIB_MASK_VERSION', 'EIB_M_INDIVIDUAL_ADDRESS_READ', 'EIB_M_INDIVIDUAL_ADDRESS_WRITE', 'EIB_ERROR_ADDR_EXISTS', 'EIB_ERROR_MORE_DEVICE', 'EIB_ERROR_TIMEOUT', 'EIB_MC_CONNECTION', 'EIB_MC_READ', 'EIB_MC_WRITE', 'EIB_MC_PROP_READ', 'EIB_MC_PROP_WRITE', 'EIB_MC_PEI_TYPE', 'EIB_MC_ADC_READ', 'EIB_MC_AUTHORIZE', 'EIB_MC_KEY_WRITE', 'EIB_MC_MASK_VERSION', 'EIB_MC_PROG_MODE', 'EIB_MC_PROP_DESC', 'EIB_MC_PROP_SCAN', 'EIB_LOAD_IMAGE', 'EIBSocketURL', 'EIBSocketLocal', 'EIBSocketRemote', 'EIBClose', 'EIBOpenBusmonitor', 'EIBOpenBusmonitorText', 'EIBOpenVBusmonitor', 'EIBOpenVBusmonitorText', 'EIBOpenT_Connection', 'EIBOpenT_Individual', 'EIBOpenT_Group', 'EIBOpenT_Broadcast', 'EIBOpenT_TPDU', 'EIBSendAPDU', 'EIBGetAPDU', 'EIBGetAPDU_Src', 'EIBSendTPDU', 'EIBOpen_GroupSocket', 'EIBSendGroup', 'EIBGetGroup_Src', 'EIB_M_ReadIndividualAddresses', 'EIB_M_Progmode_On', 'EIB_M_Progmode_Off', 'EIB_M_Progmode_Toggle', 'EIB_M_Progmode_Status', 'EIB_M_GetMaskVersion', 'EIB_M_WriteIndividualAddress', 'EIB_MC_Connect', 'EIB_MC_Read', 'EIB_MC_Write', 'EIB_MC_Progmode_On', 'EIB_MC_Progmode_Off', 'EIB_MC_Progmode_Toggle', 'EIB_MC_Progmode_Status', 'EIB_MC_GetMaskVersion', 'EIB_MC_PropertyRead', 'EIB_MC_PropertyWrite', 'EIB_MC_PropertyDesc', 'EIB_MC_PropertyScan', 'EIB_MC_GetPEIType', 'EIB_MC_ReadADC', 'EIB_MC_Authorize', 'EIB_MC_SetKey', 'EIB_LoadImage', 'EIBGetBusmonitorPacket' ]


