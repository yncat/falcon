﻿# -*- coding: utf-8 -*-
#Falcon tab base object
#Copyright (C) 2019-2020 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

"""
タブは、必ずリストビューです。カラムの数と名前と、それに対応するリストの要素がタブを構成します。たとえば、ファイル一覧では「ファイル名」や「サイズ」などがカラムになり、その情報がリストに格納されています。ファイル操作の状況を示すタブの場合は、「進行率」や「状態」などがカラムの名前として想定されています。リスト上でエンターを押すことで、アクションを実行できます。ファイルビューではファイルやフォルダを開き、ファイル操作では問い合わせに応答することができます。
"""

import wx
import errorCodes
import globalVars
import misc

class FalconTabBase(object):
	"""全てのタブに共通する基本クラス。"""
	def __init__(self):
		self.task=None
		self.colums=[]#タブに表示されるカラムの一覧。外からは読み取りのみ。
		self.listObject=None#リストの中身を保持している listObjects のうちのどれかのオブジェクト・インスタンス
		self.type=None
		self.isRenaming=False
		globalVars.app.config.add_section(self.__class__.__name__)
		self.environment={}		#このタブ特有の環境変数
		self.markedPlace=None	#マークフォルダ

	def InstallListCtrl(self,creator):
		"""指定された親パネルの子供として、このタブ専用のリストコントロールを生成する。"""
		self.hListCtrl=creator.ListCtrl(1,wx.EXPAND,style=wx.LC_REPORT|wx.LC_EDIT_LABELS)
		creator.GetPanel().Layout()

		self.hListCtrl.Bind(wx.EVT_LIST_COL_CLICK,self.col_click)
		self.hListCtrl.Bind(wx.EVT_LIST_COL_END_DRAG,self.col_resize)
		self.hListCtrl.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT,self.OnLabelEditStart)
		self.hListCtrl.Bind(wx.EVT_LIST_END_LABEL_EDIT,self.OnLabelEditEnd)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.EnterItem)
		self.hListCtrl.Bind(wx.EVT_KEY_DOWN,self.KeyDown)
		self.hListCtrl.Bind(wx.EVT_LIST_BEGIN_DRAG,self.BeginDrag)

	def GetListColumns(self):
		return self.columns

	def GetItems(self):
		"""タブのリストの中身を取得する。"""
		return self.listObject.GetItems() if self.listObject is not None else []

	def GetFocusedItem(self):
		"""現在フォーカスが当たっているアイテムのインデックス番号を取得する。"""
		return self.hListCtrl.GetFocusedItem()

	def GetFocusedElement(self):
		"""現在フォーカスが当たっているアイテムをbrowsableObjectsで返す"""
		if self.GetFocusedItem()<0:
			return None
		return self.listObject.GetElement(self.GetFocusedItem())

	# 選択されているアイテムが１つ以上存在するか否か
	def IsItemSelected(self):
		return self.hListCtrl.GetSelectedItemCount()>0

	def GetSelectedItemCount(self):
		return self.hListCtrl.GetSelectedItemCount()

	def GetSelectedItems(self,index_mode=False):
		"""選択中のアイテムを、 ListObject で帰す。index_mode が true の場合、 リスト上での index のリストを返す。"""
		next=self.hListCtrl.GetFirstSelected()
		if next==-1: return None
		lst=[]
		while(True):
			if index_mode:
				lst.append(next)
			else:
				lst.append(self.listObject.GetElement(next))
			next=self.hListCtrl.GetNextSelected(next)
			if next==-1: break
		#end while
		#リストを作る
		if index_mode: return lst
		r=type(self.listObject)()
		r.Initialize(lst)
		return r
		#end GetSelectedItems

	def GetListCtrl(self):
		return self.hListCtrl

	def SetListColumns(self,lst):
		"""リストコントロールにカラムを設定する。"""
		col=lst.GetColumns()
		self.hListCtrl.DeleteAllColumns()
		i=0
		for elem,format in col.items():
			self.hListCtrl.InsertColumn(i,elem,format=format,width=wx.LIST_AUTOSIZE)
			i+=1
		#end カラムを作る
		#カラム幅を設定
		for i in range(0,len(col)):
			w=globalVars.app.config[lst.__class__.__name__]["column_width_"+str(i)]
			w=100 if w=="" else int(w)
			self.hListCtrl.SetColumnWidth(i,w)
		#end カラム幅を設定
#end SetListColumns

	def UpdateListContent(self,content):
		"""リストコントロールの中身を更新する。カラム設定は含まない。"""
		self.log.debug("Updating list control...")
		self._cancelBackgroundTasks()
		t=misc.Timer()
		for elem in content:
			self.hListCtrl.Append(elem)
		#end 追加
		self.log.debug("List control updated in %f seconds." % t.elapsed)

	def TriggerAction(self, action,admin=False):
		"""タブの指定要素に対してアクションを実行する。成功した場合は、errorCodes.OK を返し、失敗した場合は、その他のエラーコードを返す。admin=True で、管理者として実行する。"""
		return errorCodes.NOT_SUPPORTED#基底クラスではなにも許可しない

	def EnterItem(self,event):
		"""アイテムの上でエンターを押したときに実行される。本当はビューのショートカットキーにしたかったんだけど、エンターの入力だけはこっちでとらないとできなかった。"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね

	def MarkSet():
		"""現在開いている場所をマークする"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね

	def KeyDown(self,event):
		"""キーが押されたらここにくる。SpaceがEnterと同一視されるので対策する。"""
		if not event.GetKeyCode()==32:
			event.Skip()
		else:
			self.OnSpaceKey()

	def OnSpaceKey(self):
		"""Spaceキーが押されたらこれが呼ばれる。"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね

	def BeginDrag(self,event):
		"""ドラッグ操作が開始された"""
		return errorCodes.NOT_SUPPORTED#オーバーライドしてね
