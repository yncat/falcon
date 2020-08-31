# -*- coding: utf-8 -*-
#Falcon FileList Base Function
#Copyright (C) 2019-2020 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import os
import win32file

import constants

from .base import FalconListBase
from .constants import *
from win32com.shell import shell, shellcon

class FileListBase(FalconListBase):
	def __init__(self):
		super().__init__()
		self.ClearCache()

	def ClearCache(self):
		self.imageCache={}			#拡張子->ImageIDのキャッシュ
		self.typeStringCache={}		#拡張子->typeStringのキャッシュ

	def GetAttributeCheckState(self):
		"""このリストに入っているファイルを1個ずつとって、対応するファイルの属性値を取得していく。各属性に対して、リスト内の全てのファイルが持っていれば ATTRIB_FULL_CHECKED を帰す。一部のファイルが持っていれば、 ATTRIB_HALF_CHECKED を帰す。どのファイルも持っていなければ、 ATTRIB_NOT_CHECKED を帰す。このデータを、リストにして帰す。"""
		found=[0,0,0,0]#各属性を見つけた個数
		ret=[constants.NOT_CHECKED, constants.NOT_CHECKED, constants.NOT_CHECKED, constants.NOT_CHECKED]#帰す値
		for elem in self:
			attrib=elem.attributes
			if attrib&win32file.FILE_ATTRIBUTE_READONLY:
				found[READONLY]+=1
				ret[READONLY]=constants.HALF_CHECKED
			#end readonly
			if attrib&win32file.FILE_ATTRIBUTE_HIDDEN:
				found[HIDDEN]+=1
				ret[HIDDEN]=constants.HALF_CHECKED
			#end hidden
			if attrib&win32file.FILE_ATTRIBUTE_SYSTEM:
				found[SYSTEM]+=1
				ret[SYSTEM]=constants.HALF_CHECKED
			#end system
			if attrib&win32file.FILE_ATTRIBUTE_ARCHIVE:
				found[ARCHIVE]+=1
				ret[ARCHIVE]=constants.HALF_CHECKED
			#end system
		#end for
		l=len(self)
		if found[READONLY]==l: ret[READONLY]=constants.FULL_CHECKED
		if found[HIDDEN]==l: ret[HIDDEN]=constants.FULL_CHECKED
		if found[SYSTEM]==l: ret[SYSTEM]=constants.FULL_CHECKED
		if found[ARCHIVE]==l: ret[ARCHIVE]=constants.FULL_CHECKED
		return ret

	def GetShellInfo(self,fullpath):
		"""
			Cacheを活用し、効率的に画像とファイルタイプを収集する
		"""
		if os.path.isfile(fullpath):
			ext=os.path.splitext(fullpath)[1]
		else:
			ext="/folder/"
		if ext=="":
			ret, shfileinfo=shell.SHGetFileInfo(fullpath,0,shellcon.SHGFI_ICON | shellcon.SHGFI_TYPENAME)
			return shfileinfo
		elif ext in self.typeStringCache:
			return (self.imageCache[ext],None,None,None,self.typeStringCache[ext])
		else:
			ret, shfileinfo=shell.SHGetFileInfo(fullpath,0,shellcon.SHGFI_ICON | shellcon.SHGFI_TYPENAME)
			self.typeStringCache[ext]=shfileinfo[4]
			self.imageCache[ext]=shfileinfo[0]
			return shfileinfo
