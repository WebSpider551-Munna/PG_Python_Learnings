import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64 # To easily handle binary data in input/output

def generate_key():
    """Generates a new 256-bit (32-byte) encryption key."""
    # AES-256 requires a 32-byte key
    return AESGCM.generate_key(bit_length=256)

def encrypt_text(text, key):
    """Encrypts the given text using AES-256-GCM."""
    aesgcm = AESGCM(key)
    # GCM requires a nonce (Initialization Vector)
    # 12 bytes is recommended by NIST
    nonce = os.urandom(12)
    # Encrypt the text (encode to bytes first)
    # AESGCM handles padding and authentication tag automatically
    encrypted_data = aesgcm.encrypt(nonce, text.encode(), None) # No associated data
    # Return nonce + encrypted data, encoded for easier handling
    return base64.b64encode(nonce + encrypted_data)

def decrypt_text(encrypted_data_b64, key):
    """Decrypts the given AES-256-GCM encrypted text."""
    try:
        # Decode from base64
        encrypted_data_with_nonce = base64.b64decode(encrypted_data_b64)

        # Extract nonce (first 12 bytes)
        nonce = encrypted_data_with_nonce[:12]
        # Extract actual encrypted data (rest of the bytes)
        encrypted_data = encrypted_data_with_nonce[12:]

        aesgcm = AESGCM(key)
        # Decrypt and verify authentication tag
        decrypted_bytes = aesgcm.decrypt(nonce, encrypted_data, None) # No associated data
        # Decode back to string
        return decrypted_bytes.decode()
    except Exception as e:
        # Decryption can fail if key is wrong or data is tampered (invalid tag)
        print(f"Decryption error: {e}")
        raise # Re-raise the exception to signal failure

if __name__ == "__main__":
    while True:
        print("\nChoose an option:")
        print("1. Encrypt (AES-256-GCM)")
        print("2. Decrypt (AES-256-GCM)")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            text = input("Enter the text to encrypt: ")
            key = generate_key()
            encrypted_text_b64 = encrypt_text(text, key)
            print("Encrypted text (Base64):", encrypted_text_b64.decode())
            # Encode key in base64 for easier copy/paste
            print("Encryption key (Base64):", base64.b64encode(key).decode())
        elif choice == '2':
            encrypted_text_b64_str = input("Enter the encrypted text (Base64): ")
            key_b64_str = input("Enter the encryption key (Base64): ")

            try:
                # Decode key from base64
                key = base64.b64decode(key_b64_str)
                # Pass the base64 string directly to decrypt function
                decrypted_text = decrypt_text(encrypted_text_b64_str.encode(), key)
                print("Decrypted text:", decrypted_text)
            except Exception as e:
                # Error message is printed within decrypt_text
                print("Decryption failed. Ensure the key and encrypted text are correct.")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
