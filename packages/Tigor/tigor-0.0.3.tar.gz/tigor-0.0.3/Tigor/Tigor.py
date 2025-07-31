#def unic_coder(text, x=0):
import pickle
def to_binary(data):
    # Сериализуем данные в байты
    bytes_data = pickle.dumps(data)
    # Преобразуем каждый байт в 8-битную строку
    binary_str = ''.join(format(byte, '08b') for byte in bytes_data)
    return binary_str
def from_binary(binary_str):
    # Разбиваем строку на байты (по 8 символов)
    byte_list = [
        int(binary_str[i:i+8], 2)
        for i in range(0, len(binary_str), 8)
    ]
    # Преобразуем байты обратно в данные
    bytes_data = bytes(byte_list)
    return pickle.loads(bytes_data)