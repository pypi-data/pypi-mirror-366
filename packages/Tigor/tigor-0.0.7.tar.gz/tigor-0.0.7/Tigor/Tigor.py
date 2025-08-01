#def unic_coder(text, x=0):
import pickle
def morse_coder(text, lang="ru"):
    morse_dict_en = {
        'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',
        'E': '.',      'F': '..-.',   'G': '--.',    'H': '....',
        'I': '..',     'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',
        'Q': '--.-',   'R': '.-.',    'S': '...',    'T': '-',
        'U': '..-',    'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        '0': '-----',  '1': '.----',  '2': '..---',  '3': '...--',
        '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',
        '8': '---..',  '9': '----.',
        '.': '......',  ',': '.-.-.-',  '?': '..--..',  '!': '--..--',
        ' ': '/'  
    }
    morse_dict_ru = {
        'А': '.-',      'Б': '-...',    'В': '.--',     'Г': '--.',
        'Д': '-..',     'Е': '.',       'Ё': '.',       'Ж': '...-',
        'З': '--..',    'И': '..',      'Й': '.---',    'К': '-.-',
        'Л': '.-..',    'М': '--',      'Н': '-.',      'О': '---',
        'П': '.--.',    'Р': '.-.',     'С': '...',     'Т': '-',
        'У': '..-',     'Ф': '..-.',    'Х': '....',    'Ц': '-.-.',
        'Ч': '---.',    'Ш': '----',    'Щ': '--.-',    'Ъ': '--.--',
        'Ы': '-.--',    'Ь': '-..-',    'Э': '..-..',   'Ю': '..--',
        'Я': '.-.-',
        '1': '.----',   '2': '..---',   '3': '...--',   '4': '....-', 
        '5': '.....',   '6': '-....',   '7': '--...',   '8': '---..', 
        '9': '----.',   '0': '-----',
        '.': '......',  ',': '.-.-.-',  '?': '..--..',  '!': '--..--',
        ' ': '/'
    }
    def ru_encryption():
        vh = ""
        for char in text:
            vh = vh+str(morse_dict_ru[char.upper()])+" "
        return vh
    def en_encryption():
        for char in text:
            vh = vh+str(morse_dict_en[char.upper()])+" "
        return vh
    vh = ""
    if lang == 'ru':
        vh = ru_encryption()
    elif lang == 'en':
        vh = en_encryption()
    else:
        raise "The language was specified incorrectly, change the 'lang' parameter."
    return vh
def morse_decoder(text, lang="ru"):
    morse_dict_en = {
        'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',
        'E': '.',      'F': '..-.',   'G': '--.',    'H': '....',
        'I': '..',     'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',
        'Q': '--.-',   'R': '.-.',    'S': '...',    'T': '-',
        'U': '..-',    'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        '0': '-----',  '1': '.----',  '2': '..---',  '3': '...--',
        '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',
        '8': '---..',  '9': '----.',
        '.': '......',  ',': '.-.-.-',  '?': '..--..',  '!': '--..--',
        ' ': '/'  
    }
    morse_dict_ru = {
        'А': '.-',      'Б': '-...',    'В': '.--',     'Г': '--.',
        'Д': '-..',     'Е': '.',       'Ё': '.',       'Ж': '...-',
        'З': '--..',    'И': '..',      'Й': '.---',    'К': '-.-',
        'Л': '.-..',    'М': '--',      'Н': '-.',      'О': '---',
        'П': '.--.',    'Р': '.-.',     'С': '...',     'Т': '-',
        'У': '..-',     'Ф': '..-.',    'Х': '....',    'Ц': '-.-.',
        'Ч': '---.',    'Ш': '----',    'Щ': '--.-',    'Ъ': '--.--',
        'Ы': '-.--',    'Ь': '-..-',    'Э': '..-..',   'Ю': '..--',
        'Я': '.-.-',
        '1': '.----',   '2': '..---',   '3': '...--',   '4': '....-', 
        '5': '.....',   '6': '-....',   '7': '--...',   '8': '---..', 
        '9': '----.',   '0': '-----',
        '.': '......',  ',': '.-.-.-',  '?': '..--..',  '!': '--..--',
        ' ': '/'
    }
    morse_to_en = {v: k for k, v in morse_dict_en.items()}
    morse_to_ru = {v: k for k, v in morse_dict_ru.items()}
    def ru_decryption():
        nonlocal text
        text = text.split(' ')
        for char in text:
            vh = vh+str(morse_to_ru[char].lower())+" "
    def en_decryption():
        nonlocal text
        text = text.split(' ')
        for char in text:
            vh = vh+str(morse_to_en[char].lower())+" "
    if lang == 'ru':
        vh = ru_decryption()
    elif lang == 'en':
        vh = en_decryption()
    else:
        raise "The language was specified incorrectly, change the 'lang' parameter."
    return vh
def to_binary(data):
    '''Эта функция превращает любой тип данных в двоичный код'''
    # Сериализуем данные в байты
    bytes_data = pickle.dumps(data)
    # Преобразуем каждый байт в 8-битную строку
    binary_str = ''.join(format(byte, '08b') for byte in bytes_data)
    return binary_str
def from_binary(data):
    '''Эта функция превращает любой двузначный код в данные'''
    # Разбиваем строку на байты (по 8 символов)
    byte_list = [
        int(data[i:i+8], 2)
        for i in range(0, len(data), 8)
    ]
    # Преобразуем байты обратно в данные
    bytes_data = bytes(byte_list)
    return pickle.loads(bytes_data)
def unical_coder(data, max_more_bit=12, type_coder=0):
    data = to_binary(data)
    data = list(data)
    if type_coder > 0:
        raise "It's only ready now type_coder 0"

    def method1(wh):
        for i in range(0, len(wh), 2):
            wh[i] = str(1 - int(wh[i]))
        return wh

    def method2(wh):
        # Сохраняем сумму битов до инверсии
        le = sum(map(int, wh))
        step = 3 + le % 3
        for i in range(0, len(wh), step):
            wh[i] = str(1 - int(wh[i]))
        # Сохраняем исходную сумму битов в служебных битах
        le_bin = bin(le)[2:]
        le_bin = list(le_bin)
        if len(le_bin) < max_more_bit:
            le_bin = ["0"] * (max_more_bit - len(le_bin)) + le_bin
        for i in le_bin:
            wh.append(i)
        return wh

    if type_coder == 0:
        data = method1(data)
        data = method2(data)
    data = "".join(data)
    return data

def unical_decoder(data, max_more_bit=12, type_coder=0):
    def method1(wh):
        for i in range(0, len(wh), 2):
            wh[i] = str(1 - int(wh[i]))
        return wh

    def method2(wh):
        # Извлекаем служебные биты
        le_bits = wh[-max_more_bit:]
        wh = wh[:-max_more_bit]
        le = int("".join(le_bits), 2)
        step = 3 + le % 3
        for i in range(0, len(wh), step):
            wh[i] = str(1 - int(wh[i]))
        return wh

    if type_coder == 0:
        data = list(data)
        data = method2(data)
        data = method1(data)
    data = "".join(data)
    try:
        data = from_binary(data)
    except Exception as e:
        raise "Decoder Error"
    return data