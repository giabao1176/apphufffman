# ui_widgets.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, 
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QTextCursor
from PyQt5.QtCore import Qt

# Import từ các file khác
from config import COLOR_BUTTON_ACTIVE, COLOR_HIGHLIGHT
from tree_graphics import HuffmanTreeView

# --------------- Widget hiển thị dữ liệu dạng Bảng/Text ---------------

class VisualizationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VisualizationWidget")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter) # Căn giữa theo yêu cầu
        
        self.step_title = QLabel("Trực quan hóa Cây Huffman")
        self.step_title.setObjectName("Header")
        self.step_title.setAlignment(Qt.AlignCenter) # Căn giữa tiêu đề
        self.layout.addWidget(self.step_title)
        
        self.huffman_tree_view = HuffmanTreeView()
        self.huffman_tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.huffman_tree_view)
        
        self.data_display = QTextEdit()
        self.data_display.setObjectName("DataDisplay")
        self.data_display.setReadOnly(True)
        self.data_display.setMaximumHeight(350)
        self.data_display.setFont(QFont("Consolas", 10))
        # Không cần căn giữa content bằng align center mà dùng QTextCursor để căn giữa text bên trong.
        self.layout.addWidget(self.data_display)
        self.data_display.hide()
        
        # Thêm các nút điều hướng và lưu file vào đây
        self.step_nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("< Bước trước")
        self.next_button = QPushButton("Bước tiếp theo >")
        self.save_button = QPushButton("Lưu file kết quả")
        
        self.step_nav_layout.addWidget(self.prev_button)
        self.step_nav_layout.addWidget(self.next_button)
        self.step_nav_layout.addWidget(self.save_button)
        self.layout.addLayout(self.step_nav_layout)


    def update_visualization(self, step_title, step_data, huffman_tree_root, metrics=None):
        self.step_title.setText(step_title)
        self.huffman_tree_view.set_tree(None)
        self.data_display.show()
        
        content = ""
        
        # Thiết lập QTextEdit căn giữa theo yêu cầu
        cursor = self.data_display.textCursor()
        cursor.select(QTextCursor.Document)
        format = cursor.blockFormat()
        format.setAlignment(Qt.AlignCenter)
        cursor.setBlockFormat(format)
        
        if "Bảng tần suất" in step_title:
            self.huffman_tree_view.hide()
            content += "----------------------\n"
            content += "  Ký tự | Tần suất\n"
            content += "----------------------\n"
            for char, freq in sorted(step_data):
                char_display = " " if char == ' ' else char
                content += f"'{char_display:^5}' | {freq:^8}\n"
            content += "----------------------"
            
        elif "Xây dựng cây" in step_title or "Tái tạo cây" in step_title:
            self.huffman_tree_view.show()
            self.huffman_tree_view.set_tree(huffman_tree_root)
            self.data_display.hide()
            return
            
        elif "Tạo bảng mã" in step_title:
            self.huffman_tree_view.hide()
            content += "--------------------------------------\n"
            content += "  Ký tự | Mã Huffman\n"
            content += "--------------------------------------\n"
            for char, code in step_data.items():
                char_display = " " if char == ' ' else char
                # Xử lý ký tự đặc biệt như xuống dòng
                if char_display == '\n': char_display = r'\n' 
                content += f"'{char_display:^5}' | {code}\n"
            content += "--------------------------------------"
            
        elif "Văn bản đã mã hóa" in step_title:
            self.huffman_tree_view.hide()
            if metrics:
                content += "---------------------\n"
                content += f"Thời gian nén: {metrics['time']:.4f}s\n"
                content += f"Kích thước gốc: {metrics['original_size']} bits\n"
                content += f"Kích thước nén: {metrics['compressed_size']} bits\n"
                if metrics['compressed_size'] > 0:
                    ratio = metrics['original_size'] / metrics['compressed_size']
                    content += f"Tỷ lệ nén: {ratio:.2f}x\n"
                else:
                    content += "Tỷ lệ nén: N/A\n"
                content += "---------------------\n\n"
            
            content += "Dữ liệu đã mã hóa (Bitstream):\n"
            encoded_text = step_data
            # Hiển thị 80 bit mỗi dòng
            for i in range(0, len(encoded_text), 80):
                content += encoded_text[i:i+80] + "\n"
        
        elif "Giải mã" in step_title: # Bước cuối cùng của giải mã
            self.huffman_tree_view.hide()
            if metrics:
                content += "---------------------\n"
                content += f"Thời gian giải mã: {metrics['time']:.4f}s\n"
                content += "---------------------\n\n"
            content += "Văn bản gốc đã giải mã:\n"
            content += step_data

        self.data_display.setText(content)
        self.data_display.verticalScrollBar().setValue(0)

# --------------- Lớp Thanh Tiêu đề Tùy chỉnh (MỚI) ---------------
class CustomTitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("TitleBar")
        self.setFixedHeight(40) # Đặt chiều cao cho thanh tiêu đề
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 0, 0) # Padding trái 10, trên dưới 0
        self.layout.setSpacing(10)
        
        # 1. Logo và Tên ứng dụng
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png") # Thay bằng tên file logo của bạn
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        
        app_title = QLabel("Huffman Visualizer")
        app_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self.layout.addWidget(logo_label)
        self.layout.addWidget(app_title)
        
        self.layout.addStretch(1) # Đẩy các nút sang phải

        # 2. Các nút điều khiển cửa sổ
        self.minimize_button = self._create_control_button("—", self.parent.showMinimized)
        self.maximize_button = self._create_control_button("⬜", self.toggle_maximize)
        self.close_button = self._create_control_button("✕", self.parent.close, "CloseButton")
        
        self.layout.addWidget(self.minimize_button)
        self.layout.addWidget(self.maximize_button)
        self.layout.addWidget(self.close_button)

        # 3. Kéo thả cửa sổ (Drag functionality)
        self._drag_pos = None

    def _create_control_button(self, text, slot, obj_name="ControlButton"):
        btn = QPushButton(text)
        btn.setObjectName(obj_name)
        # Đặt kích thước nhỏ hơn cho nút để phù hợp với thanh 40px
        btn.setFixedSize(40, 40)
        btn.clicked.connect(slot)
        return btn

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_button.setText("⬜")
        else:
            self.parent.showMaximized()
            self.maximize_button.setText("❐") # Ký tự Restore Down
            
    # Xử lý kéo thả (cho phép di chuyển cửa sổ khi không có thanh tiêu đề)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.parent.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.parent.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None