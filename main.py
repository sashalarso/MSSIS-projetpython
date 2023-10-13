import sys
import binascii
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPlainTextEdit, QTextEdit, QPushButton,QFileDialog

class HexEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hex Editor')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.hex_edit = QPlainTextEdit(self)
        self.hex_edit.setPlaceholderText("Hexadecimal")
        self.hex_edit.textChanged.connect(self.updateFileContent)
        layout.addWidget(self.hex_edit)

        self.file_content = QTextEdit(self)
        self.file_content.setPlaceholderText("File Content")
        layout.addWidget(self.file_content)

        load_button = QPushButton("Load File", self)
        load_button.clicked.connect(self.loadFile)
        layout.addWidget(load_button)

    def loadFile(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_name:
            with open(file_name, "rb") as file:
                content = file.read()
                self.hex_edit.setPlainText(binascii.hexlify(content).decode("utf-8"))
                self.file_content.setPlainText(content.decode("utf-8"))

    def updateFileContent(self):
        hex_text = self.hex_edit.toPlainText()
        try:
            binary_data = binascii.unhexlify(hex_text)
            self.file_content.setPlainText(binary_data.decode("utf-8"))
        except binascii.Error:
            pass

def main():
    app = QApplication(sys.argv)
    editor = HexEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
