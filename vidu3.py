import sys
import time
import json
import os
import collections
import heapq
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog, QGraphicsScene,
    QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem, QLineEdit
)
from PyQt5.QtGui import QFont, QColor, QBrush, QPen, QPainter, QPixmap, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QSize

# --------------- Cấu hình chung và màu sắc Dark Theme ---------------
PANEL_W = 450
WINDOW_W, WINDOW_H = 1400, 800

# Màu sắc (Đã điều chỉnh theo yêu cầu mới)
COLOR_BG = "#1e1e1e" # Nền chung
COLOR_UI_BG = "#2a2a2a" # Nền Sidebar/Panel
COLOR_BUTTON_BG = "#3e3e4a"
COLOR_BUTTON_HOVER = "#50505a"
COLOR_BUTTON_ACTIVE = "#9b59b6" # MÀU TÍM NỔI BẬT cho nút CHẠY
COLOR_TEXT = "#f0f0f0"
COLOR_INPUT_BOX_BG = "#333333"
COLOR_NODE = "#bbbbbb"
COLOR_BRANCH = "#90c0ff" # Xanh dương nhạt cho đường nối cây
COLOR_HIGHLIGHT = "#9b59b6" # Màu vàng cho tiêu đề/mã bit
COLOR_PURPLE_BORDER = "#9b59b6" # Màu tím cho viền panel và nút chạy

# Qt Style Sheet (QSS) cho giao diện Dark Theme
QSS = f"""
    QWidget {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT};
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}
    /* Title Bar tùy chỉnh */
    QFrame#TitleBar {{
        background-color: {COLOR_BG};
        border-bottom: 2px solid {COLOR_PURPLE_BORDER}; /* Đường kẻ tím */
        padding: 0 0; /* Padding được kiểm soát bởi layout bên trong */
        font-size: 10pt;
    }}
    /* Các nút điều khiển cửa sổ */
    QPushButton#ControlButton {{
        background-color: transparent;
        border: none;
        color: {COLOR_TEXT};
        font-weight: bold;
        font-size: 14pt;
        width: 40px;
        height: 40px;
    }}
    QPushButton#ControlButton:hover {{
        background-color: #333333;
    }}
    QPushButton#CloseButton:hover {{
        background-color: #e81123; /* Màu đỏ cho nút đóng */
        color: white;
    }}
    /* Thanh bên (Sidebar) */
    QFrame#Sidebar {{
        background-color: {COLOR_UI_BG};
        border-right: 1px solid #3a3a3a;
        /* Padding đã chuyển vào layout để kiểm soát tốt hơn */
    }}
    /* Khung chức năng (Compress/Decompress Panels) */
    QFrame#FunctionPanel {{
        background-color: {COLOR_UI_BG};
        border: 2px solid {COLOR_UI_BG};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }}
    /* Hiệu ứng viền tím khi được chọn */
    QFrame#FunctionPanel.active {{
        border: 2px solid {COLOR_PURPLE_BORDER};
    }}
    /* Nút chọn chức năng (Compress/Decompress) */
    QPushButton#FunctionButton {{
        background-color: {COLOR_BUTTON_BG};
        border: none;
        border-radius: 10px;
        padding: 15px 10px;
        font-weight: 600;
        font-size: 14pt;
        margin: 5px;
    }}
    QPushButton#FunctionButton:hover {{
        background-color: {COLOR_BUTTON_HOVER};
    }}
    QPushButton#FunctionButton:checked {{
        background-color: {COLOR_UI_BG};
        color: {COLOR_HIGHLIGHT};
    }}
    /* Nút chạy nổi bật (Màu tím) */
    QPushButton#RunButton {{
        background-color: {COLOR_BUTTON_ACTIVE}; /* MÀU TÍM */
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
        color: #f0f0f0; /* Chữ trắng */
    }}
    QPushButton#RunButton:hover {{
        background-color: #a769c3;
    }}
    /* Vùng nhập liệu */
    QTextEdit, QLineEdit {{
        background-color: {COLOR_INPUT_BOX_BG};
        border: 1px solid #555555;
        padding: 8px;
        border-radius: 5px;
    }}
    /* Tiêu đề lớn */
    QLabel#Header {{
        font-size: 16pt;
        font-weight: bold;
        color: {COLOR_BUTTON_ACTIVE};
        margin-bottom: 10px;
    }}
    /* Tiêu đề bước */
    QLabel#StepTitle {{
        font-size: 14pt;
        font-weight: bold;
        color: {COLOR_HIGHLIGHT};
        margin-top: 15px;
    }}
    /* Vùng vẽ cây và hiển thị bước (Viền tím) */
    QWidget#VisualizationWidget {{
        border: 2px solid {COLOR_PURPLE_BORDER};
        border-radius: 10px;
        background-color: {COLOR_UI_BG};
        margin: 10px;
        padding: 10px;
    }}
    QGraphicsView {{
        border: none;
        background-color: {COLOR_UI_BG};
    }}
    /* Vùng hiển thị dữ liệu bên phải */
    QTextEdit#DataDisplay {{
        background-color: {COLOR_UI_BG};
        border: 1px solid #444444;
        color: white; /* Đảm bảo màu chữ là trắng */
    }}
"""

# --------------- Thuật toán Huffman (Tái sử dụng) ---------------
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq
    def __repr__(self, prefix=''):
        result = f"{prefix}Node({self.char}, {self.freq})\n"
        if self.left:
            result += self.left.__repr__(prefix + 'L-')
        if self.right:
            result += self.right.__repr__(prefix + 'R-')
        return result

def get_tree_height(node):
    if node is None:
        return 0
    return 1 + max(get_tree_height(node.left), get_tree_height(node.right))

def calculate_frequency(text):
    return collections.Counter(text)

def build_huffman_tree(frequency):
    if not frequency: return None
    min_heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(min_heap)
    
    while len(min_heap) > 1:
        left = heapq.heappop(min_heap)
        right = heapq.heappop(min_heap)
        merged_freq = left.freq + right.freq
        merged_node = Node(None, merged_freq)
        merged_node.left = left
        merged_node.right = right
        heapq.heappush(min_heap, merged_node)
    
    return min_heap[0]

def generate_huffman_codes(node, current_code="", huffman_codes=None):
    if huffman_codes is None:
        huffman_codes = {}
    if node is None:
        return huffman_codes
    
    if node.char is not None:
        # Trường hợp chỉ có 1 ký tự duy nhất
        if not current_code and node.left is None and node.right is None:
            huffman_codes[node.char] = "0"
        else:
            huffman_codes[node.char] = current_code
        return huffman_codes
    
    generate_huffman_codes(node.left, current_code + "0", huffman_codes)
    generate_huffman_codes(node.right, current_code + "1", huffman_codes)
    return huffman_codes

def encode_text(text, huffman_codes):
    encoded_text = "".join([huffman_codes[char] for char in text])
    return encoded_text

def huffman_compress(text):
    frequency = calculate_frequency(text)
    if not frequency:
        return "", {}, None
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes_map = generate_huffman_codes(huffman_tree)
    encoded_text = encode_text(text, huffman_codes_map)
    return encoded_text, huffman_codes_map, huffman_tree

def reconstruct_huffman_tree_from_codes(huffman_codes):
    """Tái tạo cây Huffman từ bảng mã (dùng cho giải mã)"""
    root = Node(None, -1)
    if not huffman_codes:
        return None
        
    for char, code in huffman_codes.items():
        # Xử lý trường hợp chỉ có 1 ký tự, mã là "0"
        if code == "0" and len(huffman_codes) == 1:
            root.char = char
            return root
            
        current = root
        for bit in code:
            if bit == '0':
                if current.left is None:
                    # Tần suất tạm thời là -1, không quan trọng cho giải mã
                    current.left = Node(None, -1) 
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(None, -1)
                current = current.right
        current.char = char
    return root

def decode_text(encoded_text, huffman_tree):
    """Giải mã chuỗi bit bằng cây Huffman"""
    decoded_text = ""
    current_node = huffman_tree
    
    if not huffman_tree:
        raise ValueError("Cây Huffman rỗng hoặc không hợp lệ.")
    
    # Trường hợp chỉ có 1 ký tự (cây chỉ có gốc)
    if current_node.char is not None and not encoded_text:
        return ""
    if current_node.char is not None and len(encoded_text) > 0 and current_node.left is None and current_node.right is None:
        # Giả sử mã là "0" cho trường hợp 1 ký tự duy nhất
        if encoded_text == "0" * len(encoded_text):
            return current_node.char * len(encoded_text)
        else:
            raise ValueError("Lỗi giải mã: Cây 1 nút nhưng chuỗi bit không khớp.")

    for bit in encoded_text:
        if current_node is None:
            raise ValueError("Lỗi giải mã: Chuỗi bit không hợp lệ (lạc khỏi cây).")
            
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
            
        if current_node and current_node.char is not None:
            decoded_text += current_node.char
            current_node = huffman_tree # Quay lại gốc
            
    if current_node and current_node != huffman_tree and current_node.char is None:
        raise ValueError("Lỗi giải mã: Chuỗi bit không hợp lệ hoặc bị cắt cụt (dừng lại ở nút trung gian).")
        
    return decoded_text

# --------------- QGraphicsView cho Tree Visualization ---------------

class HuffmanTreeScene(QGraphicsScene):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.node_radius = 25
        self.node_font = QFont("Arial", 10, QFont.Bold)
        self.code_font = QFont("Arial", 12)
        self.set_tree(root)

    def set_tree(self, root):
        self.clear()
        self.root = root
        if self.root:
            self.draw_tree_recursive(self.root, 0, 0, 0, 0)
            self.setSceneRect(self.itemsBoundingRect())
            
    def draw_node(self, node, x, y):
        ellipse = QGraphicsEllipseItem(QRectF(-self.node_radius, -self.node_radius, 
                                             self.node_radius * 2, self.node_radius * 2))
        ellipse.setBrush(QBrush(QColor(COLOR_NODE)))
        ellipse.setPen(QPen(QColor(COLOR_BRANCH), 2))
        ellipse.setPos(x, y)
        self.addItem(ellipse)
        
        node_text = f"{node.freq}"
        if node.freq == -1: # Trường hợp nút tái tạo (Giải mã)
            node_text = "N/A"
            
        if node.char is not None:
            char_display = " " if node.char == ' ' else node.char
            char_label = f"'{char_display}'"
            if len(char_display) > 1: # Xử lý ký tự đặc biệt
                char_label = f"'{repr(char_display)}'"
            
            node_text = f"{char_label}\n{node_text}"
            
        text = QGraphicsTextItem(node_text)
        text.setFont(self.node_font)
        text.setDefaultTextColor(QColor(COLOR_BG))
        
        text_rect = text.boundingRect()
        text.setPos(x - text_rect.width() / 2, y - text_rect.height() / 2)
        self.addItem(text)
        return QPointF(x, y)

    def draw_tree_recursive(self, node, x, y, x_offset, level):
        pos = self.draw_node(node, x, y)
        new_y_offset = 80
        
        if level == 0:
            tree_height = get_tree_height(node)
            if tree_height > 1:
                x_offset = 120 * (2**(tree_height - 2)) 
            else:
                x_offset = 0
            
        new_x_offset = x_offset / 2.0
        
        if node.left:
            child_x = x - new_x_offset
            child_y = y + new_y_offset
            child_pos = self.draw_tree_recursive(node.left, child_x, child_y, new_x_offset, level + 1)
            if child_pos:
                self.draw_branch(pos, child_pos, "0")

        if node.right:
            child_x = x + new_x_offset
            child_y = y + new_y_offset
            child_pos = self.draw_tree_recursive(node.right, child_x, child_y, new_x_offset, level + 1)
            if child_pos:
                self.draw_branch(pos, child_pos, "1")
        
        return pos

    def draw_branch(self, start_pos, end_pos, code):
        line = self.addLine(start_pos.x(), start_pos.y() + self.node_radius, 
                            end_pos.x(), end_pos.y() - self.node_radius, 
                            QPen(QColor(COLOR_BRANCH), 2))
        
        mid_x = (start_pos.x() + end_pos.x()) / 2
        mid_y = (start_pos.y() + end_pos.y()) / 2
        
        text = QGraphicsTextItem(code)
        text.setFont(self.code_font)
        text.setDefaultTextColor(QColor(COLOR_HIGHLIGHT))
        
        text_rect = text.boundingRect()
        offset_x = -text_rect.width() if code == "0" else 0
        text.setPos(mid_x + offset_x, mid_y - text_rect.height() / 2)
        self.addItem(text)

class HuffmanTreeView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = HuffmanTreeScene(None, self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
    def set_tree(self, root):
        self.scene.set_tree(root)
        if self.scene.itemsBoundingRect().width() > 0:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

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
            content += "  Ký tự | Tần suất\n"
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
            content += "  Ký tự | Mã Huffman\n"
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

# --------------- Lớp chính của Ứng dụng ---------------

class HuffmanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # LOẠI BỎ THANH TIÊU ĐỀ HỆ THỐNG (TRAN VIỀN)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.setWindowTitle("Trực quan hóa thuật toán nén Huffman")
        self.setGeometry(100, 100, WINDOW_W, WINDOW_H)
        self.setStyleSheet(QSS)
        
        self.file_path = ""
        self.step_list = []
        self.current_step_index = -1
        self.huffman_codes = {}
        self.huffman_tree_root = None
        self.metrics = {}
        self.compress_input_mode = "direct"
        self.decompress_input_mode = "direct"
        self.encoded_data_for_decompress = ""

        # Thiết lập Layout chính
        main_container = QWidget()
        main_vertical_layout = QVBoxLayout(main_container)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)
        
        # Thêm Title Bar Tùy chỉnh vào trên cùng
        self.title_bar = CustomTitleBar(self)
        main_vertical_layout.addWidget(self.title_bar)

        # Thiết lập Content Area (Sidebar + Visualization)
        self.content_area = QWidget()
        self.main_layout = QHBoxLayout(self.content_area)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        main_vertical_layout.addWidget(self.content_area)
        self.setCentralWidget(main_container)

        self._setup_sidebar()
        self._setup_visualization_area()
        self.show_panel("compress")
        
    def _setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(PANEL_W)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        # SỬA: Điều chỉnh margin và spacing để tạo khoảng cách và đẩy các phần tử xuống
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10) 
        self.sidebar_layout.setSpacing(10)

        # 1. Logo area 
        logo_area = QFrame()
        logo_layout = QHBoxLayout(logo_area)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        self.logo_label = QLabel()
        try:
            # ********** SỬA LỖI ĐƯỜNG DẪN VÀ THỨ TỰ ƯU TIÊN **********
            # Lấy đường dẫn tuyệt đối của thư mục chứa file code (an toàn nhất)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Ưu tiên logo.png với đường dẫn tuyệt đối, sau đó là các file backup
            image_paths = [
                os.path.join(base_dir, "logo2.png"), # 1. Ưu tiên: logo.png (Đường dẫn tuyệt đối)
                "logo.png", # 2. Dự phòng: logo.png (Đường dẫn tương đối)
                "image_7ef1ec.png", 
                "image_69d9c2.png", 
                "image_69d9a2.png"
            ]
            
            logo_pixmap = QPixmap()
            for path in image_paths:
                temp_pixmap = QPixmap(path)
                if not temp_pixmap.isNull():
                    logo_pixmap = temp_pixmap
                    break
            # **********************************************************
            
            if not logo_pixmap.isNull():
                # KÍCH THƯỚC: IgnoreAspectRatio để kéo dài ảnh
                desired_width = PANEL_W - 20
                self.logo_label.setPixmap(
                    logo_pixmap.scaled(
                        desired_width, 
                        250, # Chiều cao tối đa 250
                        Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                    )
                )
                logo_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
            else:
                logo_layout.addWidget(QLabel("Logo (Không tìm thấy file ảnh)"), alignment=Qt.AlignCenter)
        except Exception:
            logo_layout.addWidget(QLabel("Logo (Lỗi tải ảnh)"), alignment=Qt.AlignCenter)

        self.sidebar_layout.addWidget(logo_area)
        
        # 2. Function Buttons (as tabs)
        self.button_frame = QFrame()
        self.button_frame_layout = QHBoxLayout(self.button_frame)
        self.button_frame_layout.setContentsMargins(15, 0, 15, 0)
        self.compress_button = QPushButton("Nén")
        self.compress_button.setObjectName("FunctionButton")
        self.compress_button.setCheckable(True)
        self.compress_button.clicked.connect(lambda: self.show_panel("compress"))
        
        self.decompress_button = QPushButton("Giải mã")
        self.decompress_button.setObjectName("FunctionButton")
        self.decompress_button.setCheckable(True)
        self.decompress_button.clicked.connect(lambda: self.show_panel("decompress"))
        
        self.button_frame_layout.addWidget(self.compress_button)
        self.button_frame_layout.addWidget(self.decompress_button)
        self.sidebar_layout.addWidget(self.button_frame)
        
        # 3. Content panels
        self.stack_widget = QWidget()
        self.stack_layout = QVBoxLayout(self.stack_widget)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        self.stack_layout.setSpacing(0)
        
        self.compress_panel = self._create_compress_panel()
        self.decompress_panel = self._create_decompress_panel()

        self.stack_layout.addWidget(self.compress_panel)
        self.stack_layout.addWidget(self.decompress_panel)
        
        self.sidebar_layout.addWidget(self.stack_widget)
        self.sidebar_layout.addStretch(1)
        self.main_layout.addWidget(self.sidebar)

    def _create_compress_panel(self):
        panel = QFrame()
        panel.setObjectName("FunctionPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # Mode Selection
        mode_label = QLabel("Chọn chế độ đầu vào:")
        mode_layout = QHBoxLayout()
        self.direct_input_btn_c = QPushButton("Nhập trực tiếp")
        self.file_input_btn_c = QPushButton("Chọn file")
        self.direct_input_btn_c.setCheckable(True)
        self.file_input_btn_c.setCheckable(True)
        
        self.direct_input_btn_c.clicked.connect(lambda: self.set_input_mode("compress", "direct"))
        self.file_input_btn_c.clicked.connect(lambda: self.set_input_mode("compress", "file"))
        
        mode_layout.addWidget(self.direct_input_btn_c)
        mode_layout.addWidget(self.file_input_btn_c)
        layout.addWidget(mode_label)
        layout.addLayout(mode_layout)

        # Input Box
        layout.addWidget(QLabel("Dữ liệu đầu vào:"))
        self.input_box_compress = QTextEdit()
        self.input_box_compress.setPlaceholderText("Nhập văn bản cần nén ở đây...")
        self.input_box_compress.setMaximumHeight(100)
        layout.addWidget(self.input_box_compress)
        
        # Output Box
        layout.addWidget(QLabel("Kết quả (Mã bit):"))
        self.output_box_compress = QTextEdit()
        self.output_box_compress.setReadOnly(True)
        self.output_box_compress.setMaximumHeight(60)
        layout.addWidget(self.output_box_compress)
        
        # Run Button
        self.run_button_compress = QPushButton("CHẠY NÉN ALGORITHM")
        self.run_button_compress.setObjectName("RunButton")
        self.run_button_compress.clicked.connect(self.run_compress_algo)
        layout.addWidget(self.run_button_compress)
        
        layout.addStretch(1)
        return panel

    def _create_decompress_panel(self):
        panel = QFrame()
        panel.setObjectName("FunctionPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # Mode Selection
        mode_label = QLabel("Chọn chế độ đầu vào:")
        mode_layout = QHBoxLayout()
        self.direct_input_btn_d = QPushButton("Nhập trực tiếp")
        self.file_input_btn_d = QPushButton("Chọn file")
        self.direct_input_btn_d.setCheckable(True)
        self.file_input_btn_d.setCheckable(True)
        
        self.direct_input_btn_d.clicked.connect(lambda: self.set_input_mode("decompress", "direct"))
        self.file_input_btn_d.clicked.connect(lambda: self.set_input_mode("decompress", "file"))
        
        mode_layout.addWidget(self.direct_input_btn_d)
        mode_layout.addWidget(self.file_input_btn_d)
        layout.addWidget(mode_label)
        layout.addLayout(mode_layout)

        # Input Box
        layout.addWidget(QLabel("Dữ liệu đã mã hóa (Bitstream):"))
        self.input_box_decompress = QTextEdit()
        self.input_box_decompress.setPlaceholderText("Nhập chuỗi bit '0'/'1' cần giải mã ở đây...")
        self.input_box_decompress.setMaximumHeight(100)
        layout.addWidget(self.input_box_decompress)
        
        # Output Box
        layout.addWidget(QLabel("Văn bản gốc:"))
        self.output_box_decompress = QTextEdit()
        self.output_box_decompress.setReadOnly(True)
        self.output_box_decompress.setMaximumHeight(100)
        layout.addWidget(self.output_box_decompress)
        
        # Run Button
        self.run_button_decompress = QPushButton("CHẠY GIẢI MÃ")
        self.run_button_decompress.setObjectName("RunButton")
        self.run_button_decompress.clicked.connect(self.run_decompress_algo)
        layout.addWidget(self.run_button_decompress)
        
        layout.addStretch(1)
        return panel

    def _setup_visualization_area(self):
        self.viz_widget = VisualizationWidget()
        self.main_layout.addWidget(self.viz_widget)
        
        # Kết nối các tín hiệu nút bấm từ VisualizationWidget
        self.viz_widget.prev_button.clicked.connect(self.prev_step)
        self.viz_widget.next_button.clicked.connect(self.next_step)
        self.viz_widget.save_button.clicked.connect(self.save_encoded_data)
        
    # --- State Management & UI Updates ---
    
    def show_panel(self, panel_name):
        self.compress_panel.hide()
        self.decompress_panel.hide()
        self.compress_button.setChecked(False)
        self.decompress_button.setChecked(False)
        
        # Xóa class 'active'
        self.compress_panel.setProperty("class", "")
        self.decompress_panel.setProperty("class", "")
        
        if panel_name == "compress":
            self.compress_panel.show()
            self.compress_button.setChecked(True)
            self.compress_panel.setProperty("class", "active")
        elif panel_name == "decompress":
            self.decompress_panel.show()
            self.decompress_button.setChecked(True)
            self.decompress_panel.setProperty("class", "active")
            
        self.style().polish(self.compress_panel)
        self.style().polish(self.decompress_panel)
        
        self.reset_state(panel_name) # Truyền tên panel để cập nhật nội dung

    def reset_state(self, panel_name="compress"):
        self.step_list = []
        self.current_step_index = -1
        # Giữ lại self.huffman_codes nếu đang ở chế độ giải mã trực tiếp
        # self.huffman_codes = {}
        # self.huffman_tree_root = None
        # self.metrics = {}
        # self.encoded_data_for_decompress = ""
        
        if panel_name == "compress":
            self.viz_widget.step_title.setText("Trực quan hóa thuật toán nén Huffman")
            self.viz_widget.data_display.setText("Nhấn 'CHẠY NÉN ALGORITHM' để bắt đầu.")
        else: # decompress
            self.viz_widget.step_title.setText("Trực quan hóa thuật toán giải mã Huffman")
            self.viz_widget.data_display.setText("Nhấn 'CHẠY GIẢI MÃ' để bắt đầu (cần bảng mã từ quá trình nén hoặc file JSON).")
            
        self.viz_widget.huffman_tree_view.set_tree(None)
        
        self.viz_widget.prev_button.setEnabled(False)
        self.viz_widget.next_button.setEnabled(False)
        self.viz_widget.save_button.setEnabled(False)
        self.output_box_compress.clear()
        self.output_box_decompress.clear()
        
        self.update_ui_mode()

    def update_ui_mode(self):
        self.direct_input_btn_c.setChecked(self.compress_input_mode == "direct")
        self.file_input_btn_c.setChecked(self.compress_input_mode == "file")
        self.input_box_compress.setReadOnly(self.compress_input_mode == "file")
        
        self.direct_input_btn_d.setChecked(self.decompress_input_mode == "direct")
        self.file_input_btn_d.setChecked(self.decompress_input_mode == "file")
        self.input_box_decompress.setReadOnly(self.decompress_input_mode == "file")
        
        if self.compress_panel.isVisible():
            if self.compress_input_mode == "file":
                self.input_box_compress.setText(f"File: {self.file_path.split('/')[-1] if self.file_path else 'Chưa chọn file'}")
            else:
                self.input_box_compress.setPlaceholderText("Nhập văn bản cần nén ở đây...")
                if "File:" in self.input_box_compress.toPlainText() and self.compress_input_mode == "direct": 
                    self.input_box_compress.clear()
        elif self.decompress_panel.isVisible():
            if self.decompress_input_mode == "file":
                self.input_box_decompress.setText(f"File: {self.file_path.split('/')[-1] if self.file_path else 'Chưa chọn file'}")
            else:
                self.input_box_decompress.setPlaceholderText("Nhập chuỗi bit '0'/'1' cần giải mã ở đây...")
                if "File:" in self.input_box_decompress.toPlainText() and self.decompress_input_mode == "direct": 
                    self.input_box_decompress.clear()

    def set_input_mode(self, tab, mode):
        # Đảm bảo reset trạng thái file khi chuyển mode
        old_file_path = self.file_path
        self.file_path = ""
        
        if tab == "compress":
            self.compress_input_mode = mode
            if mode == "file":
                self.select_file("compress")
            
        elif tab == "decompress":
            self.decompress_input_mode = mode
            if mode == "file":
                self.select_file("decompress")
        
        # Nếu người dùng hủy hộp thoại, giữ lại mode cũ
        if mode == "file" and not self.file_path:
            # Quay lại mode direct nếu hủy chọn file
            if tab == "compress": self.compress_input_mode = "direct"
            if tab == "decompress": self.decompress_input_mode = "direct"
            self.file_path = old_file_path # Giữ lại đường dẫn file cũ nếu có
            
        self.update_ui_mode()

    def select_file(self, mode):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Chọn tệp")
        if mode == "compress":
            # Nén chỉ cần file text
            dialog.setNameFilter("Text Files (*.txt);;All Files (*.*)")
        else:
            # Giải mã cần file bitstream (thường là .bin, nhưng ta lưu là .txt hoặc .bin)
            dialog.setNameFilter("Encoded Data Files (*.bin *.txt);;All Files (*.*)")
            
        if dialog.exec_():
            self.file_path = dialog.selectedFiles()[0]
        else:
            self.file_path = ""
    
    # --- Step Navigation ---
    
    def next_step(self):
        if self.current_step_index < len(self.step_list) - 1:
            self.current_step_index += 1
            self.update_step_visualization()

    def prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.update_step_visualization()

    def update_step_visualization(self):
        if self.current_step_index >= 0 and self.current_step_index < len(self.step_list):
            step_title, step_data = self.step_list[self.current_step_index]
            self.viz_widget.update_visualization(step_title, step_data, self.huffman_tree_root, self.metrics)
            
            self.viz_widget.prev_button.setEnabled(self.current_step_index > 0)
            self.viz_widget.next_button.setEnabled(self.current_step_index < len(self.step_list) - 1)
        else:
            # Điều này xảy ra khi reset
            if self.compress_panel.isVisible():
                self.reset_state("compress")
            else:
                self.reset_state("decompress")
            
    # --- Algorithm Functions ---
    
    def run_compress_algo(self):
        self.reset_state("compress")
        input_text = ""
        
        if self.compress_input_mode == "file":
            if not self.file_path or not os.path.exists(self.file_path):
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một tệp hợp lệ.")
                return
            try:
                # Đọc nội dung file text
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    input_text = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi đọc file", f"Không thể đọc file: {e}")
                return
                
        elif self.compress_input_mode == "direct":
            input_text = self.input_box_compress.toPlainText()

        if not input_text:
            QMessageBox.warning(self, "Cảnh báo", "Dữ liệu đầu vào trống.")
            return

        start_time = time.perf_counter()
        encoded, codes, tree = huffman_compress(input_text)
        end_time = time.perf_counter()
        
        # Cập nhật state chung
        self.huffman_codes = codes
        self.huffman_tree_root = tree
        self.encoded_data_for_decompress = encoded
        self.output_box_compress.setText(encoded)
        
        original_size = len(input_text.encode('utf-8')) * 8
        compressed_size = len(encoded)
        self.metrics = {
            'time': end_time - start_time,
            'original_size': original_size,
            'compressed_size': compressed_size
        }
        
        freq_map = calculate_frequency(input_text)
        self.step_list.append(("Bước 1: Bảng tần suất ký tự", sorted(freq_map.items())))
        self.step_list.append(("Bước 2: Xây dựng cây Huffman", None))
        self.step_list.append(("Bước 3: Tạo bảng mã Huffman", codes))
        self.step_list.append(("Bước 4: Văn bản đã mã hóa & Metrics", encoded))

        self.current_step_index = 0
        self.update_step_visualization()
        self.viz_widget.save_button.setEnabled(True)

    def run_decompress_algo(self):
        self.output_box_decompress.clear()
        self.reset_state("decompress")
        
        encoded_data = ""
        current_huffman_codes = {}
        
        try:
            if self.decompress_input_mode == "file":
                if not self.file_path or not os.path.exists(self.file_path):
                    QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một tệp dữ liệu đã mã hóa hợp lệ.")
                    return
                
                # 1. Load Encoded Data (Bitstream)
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    encoded_data = f.read().strip()
                
                # 2. Load Huffman Codes Map (from accompanying .json file)
                base_path = os.path.splitext(self.file_path)[0]
                codes_file_path = base_path + '.json'
                
                if not os.path.exists(codes_file_path):
                    QMessageBox.warning(self, "Lỗi", f"Không tìm thấy file bảng mã: {codes_file_path.split('/')[-1]}.")
                    return
                    
                with open(codes_file_path, 'r', encoding='utf-8') as f:
                    current_huffman_codes = json.load(f)

                if not encoded_data or not current_huffman_codes:
                    QMessageBox.warning(self, "Cảnh báo", "Dữ liệu nén hoặc bảng mã trống/không hợp lệ.")
                    return

            elif self.decompress_input_mode == "direct":
                encoded_data = self.input_box_decompress.toPlainText().strip()
                if not encoded_data:
                    QMessageBox.warning(self, "Cảnh báo", "Dữ liệu bitstream trống.")
                    return
                
                # Use codes from the last compression run
                if not self.huffman_codes:
                    QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy bảng mã Huffman. Vui lòng chạy Nén trước hoặc sử dụng chế độ File để tải bảng mã.")
                    return
                current_huffman_codes = self.huffman_codes
            
            # --- Validation ---
            if not all(c in '01' for c in encoded_data):
                QMessageBox.warning(self, "Lỗi", "Chuỗi bitstream chỉ được chứa ký tự '0' và '1'.")
                return

            # --- Decoding Process ---
            
            # Bước 1: Tái tạo cây Huffman từ bảng mã
            reconstructed_tree = reconstruct_huffman_tree_from_codes(current_huffman_codes)
            
            start_time = time.perf_counter()
            decoded_text = decode_text(encoded_data, reconstructed_tree)
            end_time = time.perf_counter()
            
            # Bước 2: Giải mã
            self.output_box_decompress.setText(decoded_text)
            
            # Cập nhật Visualization
            self.huffman_tree_root = reconstructed_tree
            self.metrics = {'time': end_time - start_time}
            
            self.step_list.append(("Bước 1: Tái tạo cây Huffman", None))
            self.step_list.append(("Bước 2: Giải mã thành công", decoded_text))

            self.current_step_index = 0
            self.update_step_visualization()

        except ValueError as ve:
            QMessageBox.critical(self, "Lỗi giải mã", str(ve))
            print(f"Decode ValueError: {ve}")
            self.reset_state("decompress")
        except FileNotFoundError as fnfe:
             QMessageBox.critical(self, "Lỗi File", f"Không tìm thấy file: {fnfe}")
             self.reset_state("decompress")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Lỗi JSON", "Không thể đọc file bảng mã (định dạng JSON không hợp lệ).")
            self.reset_state("decompress")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi chung", f"Đã xảy ra lỗi: {e}")
            print(f"General Error: {e}")
            self.reset_state("decompress")

    def save_encoded_data(self):
        """Lưu bitstream và bảng mã Huffman (.json)"""
        if not self.encoded_data_for_decompress or not self.huffman_codes:
            QMessageBox.warning(self, "Cảnh báo", "Chưa có dữ liệu nén để lưu. Vui lòng chạy nén trước.")
            return

        # Dùng QFileDialog để chọn nơi lưu
        file_path_save, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu tệp đã nén", 
            "encoded_data",
            "Binary Files (*.bin);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path_save:
            try:
                # 1. Lưu dữ liệu đã mã hóa (bitstream)
                # Lưu dưới dạng text '0' và '1'
                with open(file_path_save, 'w') as f:
                    f.write(self.encoded_data_for_decompress)
                
                # 2. Lưu bảng mã Huffman (.json)
                codes_file_path = os.path.splitext(file_path_save)[0] + '.json'
                with open(codes_file_path, 'w', encoding='utf-8') as f:
                    # Đảm bảo các key (ký tự) được lưu đúng cách
                    json.dump(self.huffman_codes, f, indent=4, ensure_ascii=False) 

                QMessageBox.information(self, "Thành công", 
                                        f"Đã lưu kết quả vào:\n- Dữ liệu nén: {file_path_save.split('/')[-1]}\n- Bảng mã: {codes_file_path.split('/')[-1]}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi lưu file", f"Không thể lưu file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HuffmanApp()
    window.show()
    sys.exit(app.exec_())