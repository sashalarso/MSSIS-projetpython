import sys
import binascii
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QFileDialog

class HexEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hex Editor')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.hex_edit = QPlainTextEdit(self)
        self.hex_edit.setPlaceholderText("Hexadecimal")
        layout.addWidget(self.hex_edit)

        self.file_content = QPlainTextEdit(self)
        self.file_content.setPlaceholderText("File Content")
        layout.addWidget(self.file_content)

        load_button = QPushButton("Load File", self)
        load_button.clicked.connect(self.loadFile)
        layout.addWidget(load_button)

        refresh_button = QPushButton("Refresh", self)
        refresh_button.clicked.connect(self.refreshContent)
        layout.addWidget(refresh_button)

        save_button = QPushButton("Save File", self)
        save_button.clicked.connect(self.saveFile)
        layout.addWidget(save_button)

        self.binary_data = b''

    def loadFile(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_name:
            with open(file_name, "rb") as file:
                self.binary_data = file.read()
                self.hex_edit.setPlainText(binascii.hexlify(self.binary_data).decode("utf-8"))
                self.file_content.setPlainText(self.binary_data.decode("utf-8"))

    def refreshContent(self):
        hex_text = self.hex_edit.toPlainText()
        try:
            binary_data = binascii.unhexlify(hex_text)
            self.binary_data = binary_data
            self.file_content.setPlainText(binary_data.decode("utf-8"))
        except binascii.Error:
            pass

    def saveFile(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)")
        if file_name:
            with open(file_name, "wb") as file:
                file.write(self.binary_data)

def main():
    app = QApplication(sys.argv)
    editor = HexEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

