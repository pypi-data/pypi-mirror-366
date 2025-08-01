#  simple_carla/tests/plugin_dialog.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
from PyQt5.QtWidgets import QMainWindow
from simple_carla.plugin_dialog import CarlaPluginDialog

class TestWindow(QMainWindow):

	def __init__(self, options):
		super().__init__()
		self.options = options

	def showEvent(self, event):
		QTimer.singleShot(0, self.show_dialog)

	def show_dialog(self):
		self.plugin_def = CarlaPluginDialog(self).exec_dialog()
		if self.plugin_def is not None:
			if self.options.plugin_def:
				pprint({ k:self.plugin_def[k] for k in ['name', 'build', 'type', 'filename', 'label', 'uniqueId'] })
			else:
				pprint(self.plugin_def)
		self.close()



if __name__ == "__main__":
	import argparse, logging, sys
	from PyQt5.QtWidgets import QApplication
	from PyQt5.QtCore import QTimer
	from pprint import pprint
	p = argparse.ArgumentParser()
	p.epilog = """
	Write your help text!
	"""
	p.add_argument("--plugin-def", "-d", action="store_true", help="Spit out a plugin definition to use when coding plugins.")
	p.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(levelname)-8s %(message)s"
	)
	app = QApplication([])
	window = TestWindow(options)
	window.show()
	app.exec()


#  end simple_carla/tests/plugin_dialog.py
