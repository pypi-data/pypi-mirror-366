"""
Copyright © 2025 Pentabyteman
"""
# src/pykrait/__main__.py

import sys
from PySide6.QtWidgets import QApplication
from pykrait.gui.fileselection import FileSelectionWindow
from pykrait.gui.mainwindow import MainWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.file_selection = FileSelectionWindow()
        self.file_selection.analysis_complete.connect(self.on_analysis_complete)
        self.file_selection.show()

        # Keep references to windows
        self.main_window = None

    def on_analysis_complete(self, results):
        # Called when analysis is done in FileSelectionWindow
        # Hide file selection window
        self.file_selection.close()
        # Launch main window, keep reference
        self.main_window = MainWindow(
            frames=results["frames"],
            mask=results["masks"],
            mean_intensities=results["mean_intensities"],
            analysis_output=results["analysis_output"],
            analysis_params=results["analysis_parameters"]
        )
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())

# In __main__.py
if __name__ == "__main__":
    controller = AppController()
    controller.run()
