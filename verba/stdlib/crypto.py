import hashlib
import secrets
import base64

def crypto_hash(text, alg="sha256"):
    try:
        h = hashlib.new(alg)
        h.update(str(text).encode("utf-8"))
        return h.hexdigest()
    except Exception:
        # Fallback to sha256 if alg is invalid
        return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

def crypto_token(n=32):
    return secrets.token_hex(int(n))

def crypto_encrypt(text, key):
    # Simple XOR + B64 (Educational only, provided because stdlib lacks AES)
    res = []
    key = str(key)
    if not key: return str(text)
    for i, c in enumerate(str(text)):
        res.append(chr(ord(c) ^ ord(key[i % len(key)])))
    return base64.b64encode("".join(res).encode("utf-8")).decode("utf-8")

def crypto_decrypt(text, key):
    try:
        decoded = base64.b64decode(str(text)).decode("utf-8")
        res = []
        key = str(key)
        for i, c in enumerate(decoded):
            res.append(chr(ord(c) ^ ord(key[i % len(key)])))
        return "".join(res)
    except Exception:
        return ""

FUNCTIONS = {
    "hash": (crypto_hash, ["text", "alg"]),
    "generate_token": (crypto_token, ["n"]),
    "encrypt": (crypto_encrypt, ["text", "key"]),
    "decrypt": (crypto_decrypt, ["text", "key"]),
}
