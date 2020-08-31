# -*- coding: utf-8 -*-
#Falcon file list object
#Copyright (C) 2019-2020 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import os
import wx
import win32api
import win32file
import pywintypes
import constants
import misc
import browsableObjects
import globalVars
import errorCodes
from win32com.shell import shell, shellcon

from simpleDialog import *

from .fileListBase import *
from .constants import *

class FileList(FileListBase):
	"""ファイルとフォルダの一覧を扱うリスト。"""
	def __init__(self):
		super().__init__()
		self.supportedSorts=[SORT_TYPE_BASENAME,SORT_TYPE_FILESIZE,SORT_TYPE_MODDATE,SORT_TYPE_ATTRIBUTES,SORT_TYPE_TYPESTRING]
		self.columns={
			_("ファイル名"):wx.LIST_FORMAT_LEFT,
			_("サイズ"):wx.LIST_FORMAT_RIGHT,
			_("更新"):wx.LIST_FORMAT_LEFT,
			_("属性"):wx.LIST_FORMAT_LEFT,
			_("種類"):wx.LIST_FORMAT_LEFT
		}
		self.files=[]
		self.folders=[]
		self.lists=[self.folders,self.files]

	def Update(self):
		return self.Initialize(self.rootDirectory,True)

	def Initialize(self,dir,silent=False):
		"""ディレクトリからファイル情報を取得し、リストを初期化する。入力は絶対パスでなければならない。情報が取得できなかった場合、errorCodes.OK以外が返る。silentがTrueなら読み上げは行われない。"""
		self.ClearCache()
		if isinstance(dir,list):#パラメータがリストなら、browsableObjects のリストとして処理刷る(ファイルリストを取得しないでコピーする)
			self._copyFromList(dir)
			return errorCodes.OK
		#end copy
		self.files.clear()
		self.folders.clear()
		dir=dir.rstrip("\\")
		dir_spl=dir.split("\\")
		level=len(dir_spl)
		if not silent:
			r=[]
			if globalVars.app.config['on_list_moved']['read_directory_level']=='True': r.append("%s%d " % (dir[0],level))
			if globalVars.app.config['on_list_moved']['read_directory_name']=='True': r.append(dir_spl[level-1])
			if len(r)>0: globalVars.app.say("".join(r))
		#end read
		self.rootDirectory=dir
		self.log.debug("Getting file list for %s..." % self.rootDirectory)
		t=misc.Timer()
		try:
			lst=win32api.FindFiles(dir+"\\*")
		except pywintypes.error as err:
			self.log.error("Cannot open the directory! {0}".format(err))
			if err.winerror==5:
				return errorCodes.ACCESS_DENIED
			dialog(_("エラー"), _("フォルダを開くことができませんでした(%(error)s)") % {"error": str(err)})
			return errorCodes.FATAL
		#end except
		if "\\" in self.rootDirectory:		#ルート以外では余計な.と..がが一番上に入っている
			del lst[0:2]
		if len(lst)==0:
			self.log.debug("Blank folder.")
			return errorCodes.OK
		#end 空のフォルダだったらさっさと帰る
		for elem in lst:
			fullpath=dir+"\\"+elem[8]
			shfileinfo=self.GetShellInfo(fullpath)
			if os.path.isfile(fullpath):
				f=browsableObjects.File()
				f.Initialize(dir,elem[8],fullpath,(elem[4]<<32)+elem[5], elem[3], elem[0], shfileinfo[4],elem[1],elem[9],shfileinfo[0])
				self.files.append(f)
			else:
				f=browsableObjects.Folder()
				f.Initialize(dir,elem[8],fullpath,-1,elem[3], elem[0], shfileinfo[4],elem[1],elem[9],shfileinfo[0])
				self.folders.append(f)
			#end どっちについかするか？
		#end 追加ループ
		self.log.debug("File list created in %f seconds." % t.elapsed)
		self.log.debug(str(len(self.folders))+" directories and "+str(len(self.files))+" files found.")
		if self.sortCursor!=0 or self.sortDescending!=0:
			self.log.debug("Triggering sorting")
			self.ApplySort()
		#end ソートが必要ならソート
		return errorCodes.OK

	def _copyFromList(self,lst):
		self.log.debug("Copying from file list...")
		for elem in lst:
			if isinstance(elem,browsableObjects.File):
				self.files.append(elem)
			elif isinstance(elem,browsableObjects.Folder):
				self.folders.append(elem)
			#end ファイルかフォルダか
		#end for
	#end _copyFromList

	def GetTopFileIndex(self):
		"""先頭ファイルのインデックス番号を返す。"""
		if len(self.files)>0:
			return len(self.folders)
		else:
			return -1

	def GetFolderFileNumber(self):
		return len(self.folders), len(self.files)
