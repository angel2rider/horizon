"""Pure-Python tests for tools/datafix_worlds.py's byte-buffer VarInt decoder.

No server, network, JVM or Mojang data is needed: only the socket-less
``Bot.read_varint`` helper is exercised.
"""
import os
import tempfile
import unittest

# datafix_worlds resolves its writable root at import time; keep it off any real
# player data by pointing it at a scratch directory before importing the module.
os.environ.setdefault('HORIZON_DATAFIX_ROOT', tempfile.mkdtemp(prefix='horizon-u02-'))

from tools import datafix_worlds  # noqa: E402


def read_varint(raw_hex):
    """Decode a hex byte string with a Bot that has no socket, only a buffer."""
    bot = datafix_worlds.Bot.__new__(datafix_worlds.Bot)
    bot.buffer = bytearray(bytes.fromhex(raw_hex))
    return bot.read_varint()


class BotReadVarint(unittest.TestCase):
    def test_canonical_encodings_decode_identically(self):
        cases = {
            '00': 0,
            '01': 1,
            '7f': 127,
            '8001': 128,
            'ffffffff07': 2147483647,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(read_varint(raw), expected)

    def test_overlong_varint_raises(self):
        # Five 0x80 continuation bytes then 0x01: a sixth group must be refused,
        # as vanilla VarInt.read does, instead of decoding to 2**35.
        with self.assertRaisesRegex(ValueError, 'VarInt too big'):
            read_varint('808080808001')


if __name__ == '__main__':
    unittest.main()
