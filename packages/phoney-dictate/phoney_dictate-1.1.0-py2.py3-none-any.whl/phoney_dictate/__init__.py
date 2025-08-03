#  phoney_dictate/__init__.py
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
A voice recognition "app" which sends your cell phone's voice recognition input to your computer.
"""
import traceback, sys, os
from os.path import dirname, join
from socket import socket, AF_INET, SOCK_DGRAM
from http.server import HTTPServer, BaseHTTPRequestHandler
from PyQt5 import uic
from PyQt5.QtCore import 	Qt, pyqtSignal, pyqtSlot, QCoreApplication, QObject, QSettings, \
							QMetaObject, QRunnable, QSize, QThreadPool
from PyQt5.QtGui import 	QFont, QGuiApplication, QIcon, QPixmap, QKeySequence
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit, \
							QPushButton, QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout, \
							QWidget, QShortcut
from qt_extras import SigBlock, ShutUpQT
from phoney_dictate.qrcode import QRCodeDialog

__version__ = "1.1.0"

MINIMUM_POINT_SIZE = 9
MAXIMUM_POINT_SIZE = 32

class WorkerSignals(QObject):
	"""
	Defines the signals available from a running server thread.

	Supported signals are:

	finished
		No data

	error
		tuple (exctype, value, traceback.format_exc() )

	result
		object data returned from processing, anything

	progress
		int indicating % progress

	"""
	finished = pyqtSignal()
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	progress = pyqtSignal(int)


class RequestHandler(BaseHTTPRequestHandler):
	"""
	Defines how to handle requests to the http server.
	"""

	def do_GET(self):
		Server().show_progress(self.requestline, None, 1500)
		if self.path == '/':
			path = join(dirname(__file__), 'res', 'interface.html')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_stat_headers(path)
			with open(path, encoding='utf-8') as fh:
				self.wfile.write(fh.read().encode())
		elif self.path == '/favicon.ico':
			path = join(dirname(__file__), 'res', 'favicon.ico')
			self.send_response(200)
			self.send_header('Content-Type', 'image/vnd.microsoft.icon')
			self.send_stat_headers(path)
			with open(path, mode='rb') as fh:
				self.wfile.write(fh.read())
		else:
			self.send_response(204)	# No Content

	def send_stat_headers(self, path):
		stat = os.stat(path)
		self.send_header('Content-Length', stat.st_size)
		self.send_header('Last-Modified', self.date_time_string(stat.st_mtime))
		self.end_headers()

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		body = self.rfile.read(content_length)
		Server().show_progress(self.requestline, body.decode(), 1500)
		self.send_response(200)
		self.send_header('Content-Type', 'text/plain')
		self.end_headers()


class Server(QRunnable):
	"""
	HTTP server thread.
	"""
	__instance = None
	signals = None

	def __new__(cls):
		if cls.__instance is None:
			cls.__instance = super().__new__(cls)
		return cls.__instance

	def __init__(self):
		super().__init__()
		if self.signals is None:
			self.signals = WorkerSignals()
			self.http_server = None

	@pyqtSlot()
	def run(self):
		try:
			self.http_server = HTTPServer(('', 8585), RequestHandler)
			self.show_progress('Listening ...', None, 0)
			self.http_server.serve_forever()
			self.show_progress('Closing', None, 0)
		except Exception:
			self.err(sys.exc_info(), traceback.format_exc())
		finally:
			self.signals.finished.emit()

	def err(self, ex, tb):
		exctype, value = ex[:2]
		self.signals.error.emit((exctype, value, tb))

	def show_progress(self, stat, msg, dur):
		self.signals.result.emit({'stat': stat, 'msg': msg, 'dur': dur})

	def quit(self):
		self.http_server.shutdown()


class MainWindow(QMainWindow):
	"""
	Main window of the phoney-dictate app.
	"""

	def __init__(self):
		super().__init__(None)
		with ShutUpQT():
			uic.loadUi(join(dirname(__file__), 'res', 'main_window.ui'), self)
		settings = QSettings('ZenSoSo', 'phoney-dictate')
		if settings.contains('geometry'):
			self.restoreGeometry(settings.value('geometry'))
		if settings.contains('windowstate'):
			self.restoreState(settings.value('windowstate'))
		pixmap = QPixmap(join(dirname(__file__), 'res', 'qrcode.svg'))
		self.b_icon.setIcon(QIcon(pixmap))
		self.b_icon.clicked.connect(self.slot_show_qrcode)
		self.b_copy.clicked.connect(self.slot_copy)
		for scdef in [
			(QKeySequence.Quit, self.close),
			(QKeySequence.Copy, self.slot_copy),
			(QKeySequence.ZoomOut, self.text_box.zoomOut),
			(QKeySequence.ZoomIn, self.text_box.zoomIn)
		]:
			sc = QShortcut(scdef[0], self)
			sc.setContext(Qt.ApplicationShortcut)
			sc.activated.connect(scdef[1])
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.connect(('8.8.8.8', 7))
		self.url = f'http://{sock.getsockname()[0]}:8585'
		self.lbl_link.setText(f'<a href="{self.url}">link</a>')
		self.threadpool = QThreadPool()
		server = Server()
		server.signals.result.connect(self.show_status)
		server.signals.finished.connect(self.finished)
		server.signals.error.connect(self.server_error)
		self.threadpool.start(server)

	@pyqtSlot()
	def slot_copy(self):
		text = self.text_box.toPlainText()
		if len(text):
			QGuiApplication.clipboard().setText(text)
			self.statusbar.showMessage('Text copied to the clipboard', 2000)

	@pyqtSlot()
	def slot_show_qrcode(self):
		dlg = QRCodeDialog(self, self.url)
		dlg.exec_()

	def closeEvent(self, _):
		Server().quit()
		settings = QSettings('ZenSoSo', 'phoney-dictate')
		settings.setValue('geometry', self.saveGeometry())
		settings.setValue('windowstate', self.saveState())

	def show_status(self, obj):
		self.statusbar.showMessage(obj['stat'], obj['dur'])
		if obj['msg'] is not None:
			self.text_box.setPlainText(obj['msg'])

	def server_error(self, err):
		print(err)
		self.statusbar.showMessage(err[1])

	def finished(self):
		pass


#  end phoney_dictate/__init__.py
