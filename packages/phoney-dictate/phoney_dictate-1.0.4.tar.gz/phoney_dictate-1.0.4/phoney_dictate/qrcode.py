#  phoney_dictate/qrcode.py
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
from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QSizePolicy
from PyQt5.QtSvg import QSvgWidget

from qrcodegen import QrCode

class QRCodeDialog(QDialog):
	"""
	Shows the host url encoded as a qrcode.
	"""

	def __init__(self, parent, url):
		super().__init__(parent)
		qrcode = QrCode.encode_text(url, QrCode.Ecc.MEDIUM)
		size = qrcode.get_size()
		parts = [ f"M{x + 4},{y + 4}h1v1h-1z" \
			for y in range(size) \
			for x in range(size)
			if qrcode.get_module(x, y) ]
		svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {size + 8} {size + 8}" stroke="none">
	<rect width="100%" height="100%" fill="#FFFFFF"/>
	<path d="{" ".join(parts)}" fill="#000000"/>
</svg>
"""
		widget = QSvgWidget(self)
		widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		widget.renderer().load(bytearray(svg.encode('utf-8')))
		lo = QVBoxLayout()
		lo.addWidget(widget)
		self.setLayout(lo)
		size = QApplication.instance().primaryScreen().size()
		size = min(620, size.height(), size.width())
		self.resize(size, size)

if __name__ == '__main__':
	app = QApplication([])
	dialog = QRCodeDialog(None, 'https://github.com/nayuki/QR-Code-generator/blob/master/python/qrcodegen-demo.py')
	dialog.exec_()


#  end phoney_dictate/qrcode.py
