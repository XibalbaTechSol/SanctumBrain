import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SanctumCrypto:
    """
    Handles ECDH Key Exchange and AES-GCM Encryption for the A2A protocol.
    """
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        self.shared_key = None

    def get_public_bytes(self) -> bytes:
        from cryptography.hazmat.primitives.asymmetric import ec
        public_numbers = self.public_key.public_numbers()
        x = public_numbers.x.to_bytes(32, byteorder='big')
        y = public_numbers.y.to_bytes(32, byteorder='big')
        return x + y

    def derive_shared_key(self, peer_public_bytes: bytes):
        from cryptography.hazmat.primitives.asymmetric import ec
        
        # Check if it's raw 64-byte P256 key (X + Y)
        if len(peer_public_bytes) == 64:
            x = peer_public_bytes[:32]
            y = peer_public_bytes[32:]
            peer_public_key = ec.EllipticCurvePublicNumbers(
                int.from_bytes(x, 'big'),
                int.from_bytes(y, 'big'),
                ec.SECP256R1()
            ).public_key()
        else:
            from cryptography.hazmat.primitives import serialization
            peer_public_key = serialization.load_der_public_key(peer_public_bytes)
        
        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)
        
        # Derive a symmetric key using HKDF
        self.shared_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"sanctum-a2a-handshake",
        ).derive(shared_secret)

    def encrypt(self, data: bytes) -> tuple[bytes, bytes, bytes]:
        """Encrypts data using AES-GCM."""
        if not self.shared_key:
            raise ValueError("Shared key not established")
        
        aesgcm = AESGCM(self.shared_key)
        nonce = os.urandom(12)
        # AESGCM.encrypt returns ciphertext + tag
        ciphertext_with_tag = aesgcm.encrypt(nonce, data, None)
        
        # Separate tag (last 16 bytes)
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        return ciphertext, nonce, tag

    def decrypt(self, ciphertext: bytes, nonce: bytes, tag: bytes) -> bytes:
        """Decrypts data using AES-GCM."""
        if not self.shared_key:
            raise ValueError("Shared key not established")
        
        aesgcm = AESGCM(self.shared_key)
        return aesgcm.decrypt(nonce, ciphertext + tag, None)

# Example Usage
if __name__ == "__main__":
    # Server side
    server = SanctumCrypto()
    # Client side (simulated)
    client = SanctumCrypto()
    
    # Exchange
    server.derive_shared_key(client.get_public_bytes())
    client.derive_shared_key(server.get_public_bytes())
    
    # Test encryption
    secret_msg = b"Hello from the Sentinel"
    c, n, t = client.encrypt(secret_msg)
    decrypted = server.decrypt(c, n, t)
    
    assert secret_msg == decrypted
    print("Encryption/Decryption successful!")
