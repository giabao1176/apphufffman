import sys
import os
import json
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFrame, QFileDialog, QMessageBox, QSpacerItem, QLineEdit
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

# Import từ các file đã chia nhỏ (Đảm bảo các file này nằm cùng thư mục)
from config import QSS, WINDOW_W, WINDOW_H, PANEL_W
from ui_widgets import CustomTitleBar, VisualizationWidget
from huffman_algo import (
    huffman_compress, decode_text, calculate_frequency, 
    reconstruct_huffman_tree_from_codes
)

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
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10) 
        self.sidebar_layout.setSpacing(10)

        # 1. Logo area 
        logo_area = QFrame()
        logo_layout = QHBoxLayout(logo_area)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        self.logo_label = QLabel()
        try:
            # Xử lý đường dẫn ảnh logo
            base_dir = os.path.dirname(os.path.abspath(__file__))
            image_paths = [
                os.path.join(base_dir, "logo2.png"), 
                "logo.png", 
                "image_7ef1ec.png"
            ]
            
            logo_pixmap = QPixmap()
            for path in image_paths:
                temp_pixmap = QPixmap(path)
                if not temp_pixmap.isNull():
                    logo_pixmap = temp_pixmap
                    break
            
            if not logo_pixmap.isNull():
                desired_width = PANEL_W - 20
                self.logo_label.setPixmap(
                    logo_pixmap.scaled(
                        desired_width, 
                        250, 
                        Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                    )
                )
                logo_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
            else:
                logo_layout.addWidget(QLabel("HUFFMAN VISUALIZER"), alignment=Qt.AlignCenter)
        except Exception:
            logo_layout.addWidget(QLabel("HUFFMAN VISUALIZER"), alignment=Qt.AlignCenter)

        self.sidebar_layout.addWidget(logo_area)
        
        # 2. Function Buttons (Tabs)
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
        
        # Xóa class 'active' cũ
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
            
        # Cập nhật style để hiển thị viền (re-polish)
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
            step = self.step_list[self.current_step_index]
            # Sửa: Giải nén dictionary từ step_list cho đúng định dạng
            # Định dạng step_list trong run_compress_algo đang là tuple hoặc dict, cần đồng nhất
            # Ở đoạn code bạn gửi, bạn dùng list of tuples: ("Title", data). 
            # Nhưng ở hàm run_compress_algo bên dưới, tôi sẽ điều chỉnh để khớp.
            
            if isinstance(step, dict): # Nếu step là dict (như code gốc)
                title = step["title"]
                data = step["data"]
                tree = step.get("tree")
                metrics = step.get("metrics")
            else: # Nếu step là tuple (như code bạn mới thêm)
                 title = step[0]
                 data = step[1]
                 tree = self.huffman_tree_root # Mặc định dùng cây hiện tại nếu không chỉ định
                 metrics = self.metrics

            self.viz_widget.update_visualization(title, data, tree, metrics)
            
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
        
        # Tạo danh sách các bước (Sử dụng Dictionary để tương thích với VizWidget)
        freq_map = calculate_frequency(input_text)
        self.step_list = []
        self.step_list.append({
            "title": "Bước 1: Bảng tần suất ký tự", 
            "data": sorted(freq_map.items()),
            "tree": None
        })
        self.step_list.append({
            "title": "Bước 2: Xây dựng cây Huffman", 
            "data": None,
            "tree": tree
        })
        self.step_list.append({
            "title": "Bước 3: Tạo bảng mã Huffman", 
            "data": codes,
            "tree": tree
        })
        self.step_list.append({
            "title": "Bước 4: Văn bản đã mã hóa & Metrics", 
            "data": encoded,
            "tree": None,
            "metrics": self.metrics
        })

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
            
            self.step_list = []
            self.step_list.append({
                "title": "Bước 1: Tái tạo cây Huffman từ bảng mã",
                "data": None,
                "tree": reconstructed_tree
            })
            self.step_list.append({
                "title": "Bước 2: Giải mã thành công",
                "data": decoded_text,
                "tree": None,
                "metrics": self.metrics
            })

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