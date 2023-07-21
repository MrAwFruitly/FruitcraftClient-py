import base64
import urllib.parse
from typing import (
    Any,
    List,
)

import hashlib

_DEFAULT_KEY = '\u0061\u006c\u0069\u0031\u0033\u0034\u0033\u0066\u0061\u0072\u0061\u007a\u0031\u0030\u0035\u0035\u0061\u006e\u0074\u006c\u0065\u0072\u0032\u0038\u0038\u0062\u0061\u0073\u0065\u0064'

def xor_encrypt(message: str, key: str = None):
    if not key:
        key = _DEFAULT_KEY
    
    message_bytes = message.encode('utf-8')
    key_bytes = key.encode('utf-8')
    output_bytes = bytearray()

    for i in range(len(message_bytes)):
        output_byte = message_bytes[i] ^ key_bytes[i % len(key_bytes)]
        output_bytes.append(output_byte)

    output_str = output_bytes.decode('utf-8')
    encoded = base64.standard_b64encode(output_str.encode('utf-8')).decode('utf-8')
    encoded_escaped = urllib.parse.quote(encoded)

    return encoded_escaped

def xor_decrypt(encrypted: str, key: str = None):
    if not key:
        key = _DEFAULT_KEY
        
    try:
        tmp_b = urllib.parse.unquote(encrypted)
        encrypted = tmp_b
    except Exception as err:
        print("Error unescaping:", err)

    pure_value = encrypted.strip()
    if (pure_value.startswith("{") and pure_value.endswith("}")) or (pure_value.startswith("<") and pure_value.endswith(">")):
        print("Skipping XOR Decrypt:", pure_value)
        # no need to decrypt
        return encrypted

    encrypted_bytes = base64.b64decode(encrypted)
    key_bytes = key.encode('utf-8')

    decrypted_bytes = bytearray(len(encrypted_bytes))

    for i in range(len(encrypted_bytes)):
        decrypted_bytes[i] = encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)]

    decrypted = decrypted_bytes.decode('utf-8')
    return decrypted


def xor_decrypt_with_query_unescape(encrypted: str, key: str):
    if not key:
        key = _DEFAULT_KEY
    
    try:
        tmp_b = urllib.parse.unquote(encrypted.strip().replace("edata=", ""))
        encrypted = tmp_b
    except Exception as err:
        print("Error unescaping:", err)

    pure_value = encrypted.strip()
    if (pure_value.startswith("{") and pure_value.endswith("}")) or (pure_value.startswith("<") and pure_value.endswith(">")):
        print("Skipping XOR Decrypt:", pure_value)
        # no need to decrypt
        return encrypted

    encrypted_bytes = base64.b64decode(encrypted)
    key_bytes = key.encode('utf-8')

    decrypted_bytes = bytearray(len(encrypted_bytes))

    for i in range(len(encrypted_bytes)):
        decrypted_bytes[i] = encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)]

    decrypted = decrypted_bytes.decode('utf-8')
    return decrypted

def choose_strongest_atk(amount: int, *args) -> List[int]:
    if not isinstance(args, list):
        args = list(args)
    
    args = args.copy()
    args.sort(key=lambda x: getattr(x, "power", 0), reverse=True)
    print(args)
    
    return args[:amount]

def choose_strongest_atk_ids(amount: int, *args) -> List[int]:
    if not isinstance(args, list):
        args = list(args)
    
    args = args.copy()
    args.sort(key=lambda x: getattr(x, "power", 0), reverse=True)
    print(args)
    
    all_ids: List[int] = []
    for current in args[:amount]:
        current_id = getattr(current, "id", 0)
        if not current_id:
            continue
        
        all_ids.append(current_id)
    
    return all_ids

def choose_strongest_atk_id(*args) -> int:
    cards = choose_strongest_atk_ids(1, *args)
    if len(cards) == 0:
        return 0
    
    return cards[0]



def hash_q_string(value: str) -> str:
    if isinstance(value, int):
        value = str(value)
    
    # Create an MD5 hash object
    hash_obj = hashlib.md5()

    # Convert the string to bytes and update the hash object
    hash_obj.update(value.encode())

    # Get the hash value in bytes
    hashed_bytes = hash_obj.digest()

    # Convert the hash value to a hexadecimal string
    hex_string = hashed_bytes.hex()

    # Return the hexadecimal string
    return hex_string

