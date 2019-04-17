﻿# -*- coding: utf-8 -*-
#Falcon key map management
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Note: All comments except these top lines will be written in Japanese. 
import configparser
import logging
import os

import defaultKeymap
import errorCodes

code2str={0x01:"LBUTTON", 0x02:"RBUTTON", 0x03:"CANCEL", 0x04:"MBUTTON", 0x05:"XBUTTON1", 0x06:"XBUTTON2", 0x08:"BACK", 0x09:"TAB", 0x0C:"CLEAR", 0x0D:"RETURN", 0x0E:"SHIFT", 0x11:"CONTROL", 0x12:"MENU", 0x13:"PAUSE", 0x14:"CAPITAL", 0x15:"KANA", 0x17:"JUNJA", 0x18:"FINAL", 0x19:"KANJI", 0x1B:"ESCAPE", 0x1C:"CONVERT", 0x1D:"NONCONVERT", 0x1E:"ACCEPT", 0x1F:"MODECHANGE", 0x20:"SPACE", 0x21:"PRIOR", 0x22:"NEXT", 0x23:"END", 0x24:"HOME", 0x25:"LEFT", 0x26:"UP", 0x27:"RIGHT", 0x28:"DOWN", 0x29:"SELECT", 0x2A:"PRINT", 0x2B:"EXECUTE", 0x2C:"SNAPSHOT", 0x2D:"INSERT", 0x2E:"DELETE", 0x2F:"HELP", 0x30:"0", 0x31:"1", 0x32:"2", 0x33:"3", 0x34:"4", 0x35:"5", 0x36:"6", 0x37:"7", 0x38:"8", 0x39:"9", 0x41:"A", 0x42:"B", 0x43:"C", 0x44:"D", 0x45:"E", 0x46:"F", 0x47:"G", 0x48:"H", 0x49:"I", 0x4A:"J", 0x4B:"K", 0x4C:"L", 0x4D:"M", 0x4E:"N", 0x4F:"O", 0x50:"P", 0x51:"Q", 0x52:"R", 0x53:"S", 0x54:"T", 0x55:"U", 0x56:"V", 0x57:"W", 0x58:"X", 0x59:"Y", 0x5A:"Z", 0x5B:"LWIN", 0x5C:"RWIN", 0x5D:"APPS", 0x5F:"SLEEP", 0x60:"NUMPAD0", 0x61:"NUMPAD1", 0x62:"NUMPAD2", 0x63:"NUMPAD3", 0x64:"NUMPAD4", 0x65:"NUMPAD5", 0x66:"NUMPAD6", 0x67:"NUMPAD7", 0x68:"NUMPAD8", 0x69:"NUMPAD9", 0x6A:"MULTIPLY", 0x6B:"ADD", 0x6C:"SEPARATOR", 0x6D:"SUBTRACT", 0x6E:"DECIMAL", 0x6F:"DIVIDE", 0x70:"F1", 0x71:"F2", 0x72:"F3", 0x73:"F4", 0x74:"F5", 0x75:"F6", 0x76:"F7", 0x77:"F8", 0x78:"F9", 0x79:"F10", 0x7A:"F11", 0x7B:"F12", 0x7C:"F13", 0x7D:"F14", 0x7E:"F15", 0x7F:"F16", 0x80:"F17", 0x81:"F18", 0x82:"F19", 0x83:"F20", 0x84:"F21", 0x85:"F22", 0x86:"F23", 0x87:"F24", 0x90:"NUMLOCK", 0x91:"SCROLL", 0xA0:"LSHIFT", 0xA1:"RSHIFT", 0xA2:"LCONTROL", 0xA3:"RCONTROL", 0xA4:"LMENU", 0xA5:"RMENU", 0xA6:"BROWSER_BACK", 0xA7:"BROWSER_FORWARD", 0xA8:"BROWSER_REFRESH", 0xA9:"BROWSER_STOP", 0xAA:"BROWSER_SEARCH", 0xAB:"BROWSER_FAVORITES", 0xAC:"BROWSER_HOME", 0xAD:"VOLUME_MUTE", 0xAE:"VOLUME_DOWN", 0xAF:"VOLUME_UP", 0xB0:"MEDIA_NEXT_TRACK", 0xB1:"MEDIA_PREV_TRACK", 0xB2:"MEDIA_STOP", 0xB3:"MEDIA_PLAY_PAUSE", 0xB4:"LAUNCH_MAIL", 0xB5:"LAUNCH_MEDIA_SELECT", 0xB6:"LAUNCH_APP1", 0xB7:"LAUNCH_APP2", 0xBA:"OEM_1", 0xBB:"OEM_PLUS", 0xBC:"OEM_COMMA", 0xBD:"OEM_MINUS", 0xBE:"OEM_PERIOD", 0xBF:"OEM_2", 0xC0:"OEM_3", 0xDB:"OEM_4", 0xDC:"OEM_5", 0xDD:"OEM_6", 0xDE:"OEM_7", 0xDF:"OEM_8", 0xE1:"OEM_AX", 0xE2:"OEM_102", 0xE3:"ICO_HELP", 0xE4:"ICO_00", 0xE5:"PROCESSKEY", 0xE6:"ICO_CLEAR", 0xE7:"PACKET", 0xE9:"OEM_RESET", 0xEA:"OEM_JUMP", 0xEB:"OEM_PA1", 0xEC:"OEM_PA2", 0xED:"OEM_PA3", 0xEE:"OEM_WSCTRL", 0xEF:"OEM_CUSEL", 0xF0:"OEM_ATTN", 0xF1:"OEM_FINISH", 0xF2:"OEM_COPY", 0xF3:"OEM_AUTO", 0xF4:"OEM_ENLW", 0xF5:"OEM_BACKTAB", 0xF6:"ATTN", 0xF7:"CRSEL", 0xF8:"EXSEL", 0xF9:"EREOF", 0xFA:"PLAY", 0xFB:"ZOOM", 0xFC:"NONAME", 0xFD:"PA1", 0xFE:"OEM_CLEAR"}

class KeymapHandler():
	"""キーマップは、wxから実際のキーイベントを受け取って、それをコマンド文字列に変換します。"""
	def __init__(self):
		self.log=logging.getLogger("falcon.keymapHandler")

	def __del__(self):
		pass

	def Initialize(self, filename):
		"""キーマップ情報を初期かします。デフォルトキーマップを適用してから、指定されたファイルを読もうと試みます。ファイルが見つからなかった場合は、FILE_NOT_FOUND を返します。ファイルがパースできなかった場合は、PARSING_FAILED を返します。いずれの場合も、デフォルトキーマップは適用されています。"""
		self.map=configparser.ConfigParser(defaultKeymap.defaultKeymap)
		if not os.path.exists(filename):
			self.log.warning("Cannot find %s" % filename)
			return errorCodes.FILE_NOT_FOUND
		ret=self.map.read(filename)
		ret= errorCodes.OK if len(ret)>0 else errorCodes.PARSING_FAILED
		if ret==errorCodes.PARSING_FAILED:
			self.log.warning("Cannot parse %s" % filename)

	def GenerateCommand(self,code,ctrl,shift):
		"""キー情報から、コマンド名を帰します。ctrl / shift は、対応するキーが推されているかどうかを保持しています。"""
		cmd=""
		if ctrl: cmd+="CTRL+"
		if shift: cmd+="SHIFT+"
		cmd+=code2str[code]
		return self.map["keymap"][cmd] if self.map.has_option("keymap",cmd) else None

