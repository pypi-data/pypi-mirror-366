# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/19 18:50
from collections import namedtuple

FontStatusParameter = namedtuple('FontStatus', ['notUsed', 'modifying', 'calculatingID',
                                                'readyForUse', 'inUse', 'permanent', 'modifyReq', 'readyForUseReq',
                                                'notUsedReq', 'unmanagedReq', 'unmanaged'])
FontStatus = FontStatusParameter(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

MessageMemoryTypeParameter = namedtuple('MessageMemoryType', ['other', 'permanent', 'changeable',
                                                              'volatile', 'currentBuffer', 'schedule', 'blank'])

MessageMemoryType = MessageMemoryTypeParameter(1, 2, 3, 4, 5, 6, 7)

MessageStatusParameter = namedtuple('MessageStatus', ['notUsed', 'modifying', 'validating',
                                                      'valid', 'error', 'modifyReq', 'validateReq', 'notUsedReq'])
MessageStatus = MessageStatusParameter(1, 2, 3, 4, 5, 6, 7, 8)

ShortErrorStatusParameter = namedtuple('ShortErrorStatus', ['reserved', 'communications_error',
                                                            'power_error', 'attached_device_error', 'lamp_error',
                                                            'pixel_error', 'photocell_error',
                                                            'message_error', 'controller_error', 'temperature_warning',
                                                            'climate_control_system_error',
                                                            'critical_temperature_error', 'drum_sign_rotor_error',
                                                            'door_open_error', 'humidity_warning'
                                                            ])

DMSMemoryMgmtParameter = namedtuple('DmsMemoryMgmt', ['other', 'normal',
                                                      'clearChangeableMessages', 'clearVolatileMessages'])

DmsMemoryMgmt = DMSMemoryMgmtParameter(1, 2, 3, 4)

DMSControlModeParameter = namedtuple('DmsControlMode', ['other', 'local',
                                                        'external', 'central', 'centralOverride', 'simulation'])

DmsControlMode = DMSControlModeParameter(1, 2, 3, 4, 5, 6)

GraphicStatusParameter = namedtuple('GraphicStatus', ['notUsed', 'modifying',
                                                      'calculatingID', 'readyForUse', 'inUse',
                                                      'permanent', 'modifyReq', 'readyForUseReq', 'notUsedReq'])

GraphicStatus = GraphicStatusParameter(1, 2, 3, 4, 5, 6, 7, 8, 9)

GraphicTypeParameter = namedtuple('GraphicType', ['monochrome1bit', 'monochrome8bit',
                                                  'colorClassic', 'color24bit'])

GraphicType = GraphicTypeParameter(1, 2, 3, 4)

DefaultLineJustificationParameter = namedtuple('defaultJustificationLine', ['other', 'left', 'center',
                                                                            'right', 'full'])
DefaultLineJustification = DefaultLineJustificationParameter(1, 2, 3, 4, 5)

DefaultPageJustificationParameter = namedtuple('defaultJustificationPage', ['other', 'top', 'middle',
                                                                            'bottom'])
DefaultPageJustification = DefaultPageJustificationParameter(1, 2, 3, 4)

DefaultCharacterParameter = namedtuple('defaultCharacterSet', ['other', 'eightBit'])
DefaultCharacter = DefaultCharacterParameter(1, 2)
