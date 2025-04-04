from PyQt5.QtWidgets import QFileDialog

class FileSelector:
    @staticmethod
    def get_files():
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            None, "Select one or more files", "", "Text Files (*.txt)"
        )
        return file_paths if file_paths else []
