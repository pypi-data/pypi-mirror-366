from bitcrypt import BitCrypt

def test_tampering_detection():
    bit = BitCrypt()
    original = bit.encrypt(b"Sensitive Data")
    tampered = bytearray(original)
    tampered[25] ^= 0x01  # Simulate bit flipping
    try:
        bit.decrypt(bytes(tampered))
        print("Test failed: Tampering was not detected.")
    except ValueError:
        print("Test passed: Tampering detected and blocked.")

if __name__ == "__main__":
    test_tampering_detection()