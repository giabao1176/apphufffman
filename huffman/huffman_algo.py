# huffman_algo.py
import collections
import heapq

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