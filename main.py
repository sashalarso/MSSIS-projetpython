import sys
import binascii
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QFileDialog, QLineEdit,QTableWidget,QTableWidgetItem
from PySide6.QtCore import QTimer
from PIL import Image
from PIL.ExifTags import TAGS
import json

class HexEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        # Créez un minuteur pour la conversion différée
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1000 ms (1 seconde)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.delayedConversion)

        # Stocke la position de défilement
        self.scroll_position = 0

    def initUI(self):
        self.setWindowTitle('Hex Editor')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL for HTTP request")
        layout.addWidget(self.url_input)

        self.load_button = QPushButton("Load File/Request", self)
        self.load_button.clicked.connect(self.loadFileOrRequest)
        
        layout.addWidget(self.load_button)

        self.hex_edit = QPlainTextEdit(self)
        self.hex_edit.setPlaceholderText("Hexadecimal")
        layout.addWidget(self.hex_edit)

        self.file_content = QPlainTextEdit(self)
        self.file_content.setPlaceholderText("File Content")
        layout.addWidget(self.file_content)

        self.headers_table = QTableWidget(self)
        self.headers_table.setColumnCount(2)
        self.headers_table.setHorizontalHeaderLabels(['Header', 'Value'])
        layout.addWidget(self.headers_table)

        self.exif_table = QTableWidget(self)
        self.exif_table.setColumnCount(2)
        self.exif_table.setHorizontalHeaderLabels(['Tag', 'Value'])
        layout.addWidget(self.exif_table)

        save_button = QPushButton("Save File", self)
        save_button.clicked.connect(self.saveFile)
        layout.addWidget(save_button)

        export_button = QPushButton("Export EXIF as JSON", self)
        export_button.clicked.connect(self.exportExifAsJSON)
        layout.addWidget(export_button)

        self.binary_data = b''
        self.pending_hex_conversion = False
        self.exif_data=None

        self.hex_edit.textChanged.connect(self.delayedConversion)
        self.file_content.textChanged.connect(self.delayedConversionText)

    def loadFileOrRequest(self):
        user_input = self.url_input.text()
        if user_input.startswith("http://") or user_input.startswith("https://"):
            response = requests.get(user_input)
            if response.status_code == 200:
                self.binary_data = response.content
                try:
                    self.hex_edit.setPlainText(binascii.hexlify(self.binary_data).decode("utf-8"))
                except UnicodeDecodeError:
                    pass
                self.file_content.setPlainText(response.text)
                self.displayHttpHeaders(response)
                # Restaure la position de défilement
                self.file_content.verticalScrollBar().setValue(self.scroll_position)
        else:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt);;Image Files (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)

            if file_name:
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    # Chargement de l'image locale
                    image = Image.open(file_name)
                    print(image)
                    with open(file_name, "rb") as file:
                        self.binary_data = file.read()
                        
                    # Affichage de l'hexadécimal
                    #self.hex_edit.setPlainText(binascii.hexlify(self.binary_data).decode("utf-8"))
                    print(self.getExifData(image))
                    # Affichage des données EXIF
                    self.displayExifData(image)
                else:
                    with open(file_name, "rb") as file:
                        self.binary_data = file.read()
                        self.hex_edit.setPlainText(binascii.hexlify(self.binary_data).decode("utf-8"))
                        self.file_content.setPlainText(self.binary_data.decode("utf-8"))
                    # Restaure la position de défilement
                    self.file_content.verticalScrollBar().setValue(self.scroll_position)
                    # Efface le tableau des en-têtes
                    self.clearHttpHeaders()

    def saveFile(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)")
        if file_name:
            with open(file_name, "wb") as file:
                file.write(self.binary_data)
    def getExifData(self, image):
        exif_data = None
        if image and hasattr(image, '_getexif'):
            exif_info = image._getexif()
            if exif_info:
                exif_data = {}
                
                for tag, value in exif_info.items():
                    tag_name = TAGS.get(tag, tag)
                    exif_data[tag_name]=value

        return exif_data

    def delayedConversion(self):
        if not self.pending_hex_conversion:
            self.pending_hex_conversion = True
            # Sauvegarde la position de défilement
            self.scroll_position = self.file_content.verticalScrollBar().value()
            hex_text = self.hex_edit.toPlainText()
            try:
                binary_data = binascii.unhexlify(hex_text)
                self.binary_data = binary_data
                self.file_content.setPlainText(binary_data.decode("utf-8"))
            except binascii.Error:
                pass
            finally:
                self.pending_hex_conversion = False
    def displayExifData(self, image):
        self.exif_data = self.getExifData(image)
        i=0
        if self.exif_data:
            self.exif_table.setRowCount(len(self.exif_data))
            for (tag, value) in self.exif_data.items():
                self.exif_table.setItem(i, 0, QTableWidgetItem(tag))
                self.exif_table.setItem(i, 1, QTableWidgetItem(str(value)))
                i+=1
        else:
            self.exif_table.setRowCount(0)
    def delayedConversionText(self):
        if not self.pending_hex_conversion:
            self.pending_hex_conversion = True
            self.scroll_position = self.file_content.verticalScrollBar().value()
            text_data = self.file_content.toPlainText()
            self.hex_edit.setPlainText(binascii.hexlify(text_data.encode("utf-8")).decode("utf-8"))
            self.binary_data = text_data.encode("utf-8")
            self.pending_hex_conversion = False
    def exportExifAsJSON(self):
        if self.exif_data:
            exif_json = {}
            for tag, value in self.exif_data.items():
                exif_json[str(tag)] = str(value)
            print(exif_json)
            json_str = json.dumps(exif_json, indent=4)
            file_name, _ = QFileDialog.getSaveFileName(self, "Save EXIF as JSON", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, "w") as file:
                    file.write(json_str)

    def displayHttpHeaders(self, response):
        self.headers_table.setRowCount(len(response.headers))
        for i, (header, value) in enumerate(response.headers.items()):
            self.headers_table.setItem(i, 0, QTableWidgetItem(header))
            self.headers_table.setItem(i, 1, QTableWidgetItem(value))

    def clearHttpHeaders(self):
        self.headers_table.setRowCount(0)

def main():
    app = QApplication(sys.argv)
    editor = HexEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
