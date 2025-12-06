# config.py
# --------------- Cấu hình chung và màu sắc Dark Theme ---------------
PANEL_W = 450
WINDOW_W, WINDOW_H = 1400, 800

# Màu sắc
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