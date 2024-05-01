IS_TESTNET = os.getenv('TESTNET', 'false').lower() == 'true'
REGEX_KASPA_ADDRESS = "^kaspa\:[a-z0-9]{61,63}$" if not IS_TESTNET else "^kaspatest\:[a-z0-9]{61,63}$"

# address constants
ADDRESS_PREFIX = "kaspatest" if IS_TESTNET else "kaspa"
ADDRESS_EXAMPLE = "kaspatest:qpqz2vxj23kvh0m73ta2jjn2u4cv4tlufqns2eap8mxyyt0rvrxy6ejkful67" if IS_TESTNET \
    else "kaspa:qqkqkzjvr7zwxxmjxjkmxxdwju9kjs6e9u82uh59z07vgaks6gg62v8707g73"
