# tree_graphics.py
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QFont, QColor, QBrush, QPen, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF

# Import từ các file khác
from config import COLOR_NODE, COLOR_BRANCH, COLOR_BG, COLOR_HIGHLIGHT
from huffman_algo import get_tree_height

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
        text.setPos(mid_x, mid_y - text_rect.height() / 2)
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