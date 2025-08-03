import os
import hashlib
import base64
import secrets

# Constants
DEFAULT_KEY_SIZE_BITS = 1028
DEFAULT_BLOCK_SIZE = 64     # 512-bit
DEFAULT_NUM_ROUNDS = 64
SECURE_NUM_ROUNDS = 128
SECURE_OUTPUT_SIZE = 5048   # bytes

# --- Padding Utilities (PKCS7-style) ---
def pad(data, block_size):
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)

def unpad(data, block_size):
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid padding.")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding.")
    return data[:-pad_len]

# --- Key Generation ---
def generate_lana1028_key(bits=DEFAULT_KEY_SIZE_BITS):
    bytes_required = (bits + 7) // 8
    return secrets.token_bytes(bytes_required)

# --- Key Expansion ---
def key_expansion(master_key, num_rounds=64, block_size=128):
    if isinstance(master_key, str):
        master_key = master_key.encode('utf-8')  # convert str to bytes
    
    expanded_keys = []
    for i in range(num_rounds):
        round_key = hashlib.sha512(master_key + i.to_bytes(4, 'big')).digest()
        expanded_keys.append(round_key)
    return expanded_keys


# --- Substitution and Permutation ---
def s_box(data):
    return bytes((b ^ 0xA5) for b in data)

def p_box(data):
    return data[::-1]

# --- Encryption ---
def lana1028_encrypt(plaintext: str, key: bytes, secure_mode=False) -> str:
    if not isinstance(plaintext, bytes):
        plaintext = plaintext.encode()

    block_size = DEFAULT_BLOCK_SIZE
    num_rounds = SECURE_NUM_ROUNDS if secure_mode else DEFAULT_NUM_ROUNDS

    plaintext = pad(plaintext, block_size)
    iv = secrets.token_bytes(block_size)
    expanded_keys = key_expansion(key, num_rounds, block_size)

    ciphertext = bytearray(iv + plaintext)
    for round_num in range(num_rounds):
        round_key = expanded_keys[round_num]
        ciphertext = bytearray([ciphertext[i] ^ round_key[i % block_size] for i in range(len(ciphertext))])
        ciphertext = s_box(ciphertext)
        ciphertext = p_box(ciphertext)

    encoded = base64.b64encode(ciphertext)

    # Ensure secure_mode ciphertext is exactly 5048 bytes
    if secure_mode:
        while len(encoded) < SECURE_OUTPUT_SIZE:
            encoded += base64.b64encode(secrets.token_bytes(1))
        encoded = encoded[:SECURE_OUTPUT_SIZE]

    return encoded.decode()

# --- Decryption ---
def lana1028_decrypt(encoded_ciphertext: str, key: bytes, secure_mode=False) -> str:
    block_size = DEFAULT_BLOCK_SIZE
    num_rounds = SECURE_NUM_ROUNDS if secure_mode else DEFAULT_NUM_ROUNDS

    raw_cipher = base64.b64decode(encoded_ciphertext)
    expanded_keys = key_expansion(key, num_rounds, block_size)

    data = bytearray(raw_cipher)
    for round_num in reversed(range(num_rounds)):
        round_key = expanded_keys[round_num]
        data = p_box(data)
        data = s_box(data)
        data = bytearray([data[i] ^ round_key[i % block_size] for i in range(len(data))])

    iv = data[:block_size]
    plaintext_padded = data[block_size:]
    return unpad(plaintext_padded, block_size).decode(errors="ignore")

# --- Example Usage ---
if __name__ == "__main__":
    key = generate_lana1028_key()
    message = "Secret message for encryption"

    print("[Original Message]:", message)

    encrypted = lana1028_encrypt(message, key, secure_mode=False)
    print("[Encrypted]:", encrypted)
    print("[Encrypted Size]:", len(encrypted.encode()), "bytes")

    decrypted = lana1028_decrypt(encrypted, key, secure_mode=False)
    print("[Decrypted]:", decrypted)
