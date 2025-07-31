#  qt_extras/qt_extras/menu_button.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Pushbutton with an integrated drop-down menu.
"""
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint, QVariant
from PyQt5.QtWidgets import QMenu, QPushButton


class QtMenuButton(QPushButton):

	sig_item_selected = pyqtSignal(str, QVariant)

	def __init__(self, parent, fill_callback=None, constrain_width = False):
		"""
		fill_callback should return a list of tuples,
		containing text and data. It will be called when
		the menu button is clicked.
		Skips if fill_callback is None:
		"""
		super().__init__(parent)
		self.fill_callback = fill_callback
		self.constrain_width = constrain_width
		self.menu = QMenu(self)
		self.setObjectName('menu_btn')
		self.menu.setObjectName('pb_menu')
		self.clicked.connect(self.click_event)
		self.__current_data = None

	def clear(self):
		self.menu.clear()

	def addItem(self, item_text, item_data):
		action = self.menu.addAction(item_text)
		action.setData(item_data)

	def addItems(self, items):
		"""
		items must be a list of tuples containing (text, data)
		"""
		for item in items:
			action = self.menu.addAction(item[0])
			action.setData(item[1])

	def __iter__(self):
		"""
		Generator returns tuples of (text, data) for each menu item.
		"""
		for action in self.menu.actions():
			yield (action.text(), action.data())

	def __len__(self):
		return len(self.menu.actions())

	def setFont(self, font):
		super().setFont(font)
		self.menu.setFont(self.font())

	def setPointSize(self, size):
		font = self.font()
		font.setPointSize(size)
		self.setFont(font)

	@pyqtSlot()
	def click_event(self):
		self._do_fill()
		point = self.mapToGlobal(QPoint(0, self.height()))
		if self.constrain_width:
			self.menu.setFixedWidth(self.width())
		else:
			self.menu.setMinimumWidth(self.width())
		action = self.menu.exec(point)
		if not action is None:
			self.setText(action.text())
			self.__current_data = action.data()
			self.sig_item_selected.emit(action.text(), action.data())

	def data(self):
		return self.__current_data

	def data_label(self, data):
		for action in self.menu.actions():
			if action.data() is data:
				return action.text()

	def select_text(self, text):
		self._do_fill()
		if text != self.text():
			for action in self.menu.actions():
				if action.text() == text:
					self.setText(text)
					self.__current_data = action.data()
					self.sig_item_selected.emit(action.text(), action.data())
					return
			raise IndexError()

	def select_data(self, data):
		self._do_fill()
		if data != self.__current_data:
			for action in self.menu.actions():
				if action.data() is data:
					self.setText(action.text())
					self.__current_data = data
					self.sig_item_selected.emit(action.text(), action.data())
					return
			raise IndexError()

	def _do_fill(self):
		if self.fill_callback is not None:
			self.menu.clear()
			for tup in self.fill_callback():
				self.addItem(*tup)

#  end qt_extras/qt_extras/menu_button.py
