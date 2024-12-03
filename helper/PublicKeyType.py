SCRIPT_CLASS_PUB_KEY = 'pubkey'
SCRIPT_CLASS_PUB_KEY_ECDSA = 'pubkeyecdsa'
SCRIPT_CLASS_SCRIPT_HASH = 'scripthash'
SCRIPT_CLASS_NON_STANDARD = 'nonstandard'


# Get the public_key_type for a public key.
# The types are PubKey, PubKeyECDSA, ScriptHash and NonStandard
def get_public_key_type(public_key):
    if public_key is None:
        return None
    public_key_bytes = bytes.fromhex(public_key)
    if is_pay_to_pubkey(public_key_bytes):
        return SCRIPT_CLASS_PUB_KEY
    if is_pay_to_pubkey_ecdsa(public_key_bytes):
        return SCRIPT_CLASS_PUB_KEY_ECDSA
    if is_pay_to_script_hash(public_key_bytes):
        return SCRIPT_CLASS_SCRIPT_HASH
    return SCRIPT_CLASS_NON_STANDARD


def is_pay_to_pubkey(public_key_bytes):
    if len(public_key_bytes) == 34 and \
            public_key_bytes[0] == 0x20 and \
            public_key_bytes[33] == 0xac:
        return True
    return False


def is_pay_to_pubkey_ecdsa(public_key_bytes):
    if len(public_key_bytes) == 35 and \
            public_key_bytes[0] == 0x21 and \
            public_key_bytes[34] == 0xab:
        return True
    return False


def is_pay_to_script_hash(public_key_bytes):
    if len(public_key_bytes) == 35 and \
            public_key_bytes[0] == 0xaa and \
            public_key_bytes[1] == 0x20 and \
            public_key_bytes[34] == 0x87:
        return True
    return False
