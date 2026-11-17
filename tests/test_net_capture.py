"""Protocol framing and state transitions of the offline capture proxy."""
import io
import threading
import unittest

from tools import net_capture


class VarIntTests(unittest.TestCase):
    def test_a_five_byte_varint_decodes_and_a_sixth_byte_is_refused(self):
        self.assertEqual(net_capture.read_varint(b"\xff\xff\xff\xff\x0f", 0), (-1, 5))
        with self.assertRaisesRegex(ValueError, "varint too long"):
            net_capture.read_varint(b"\x80\x80\x80\x80\x80\x01", 0)


class StateTests(unittest.TestCase):
    def test_play_start_configuration_reenters_configuration(self):
        session = net_capture.Session(1, io.StringIO(), {}, threading.Lock(), full=False)
        session.state["clientbound"] = session.state["serverbound"] = "play"
        session.transition("clientbound", "start_configuration", b"")
        self.assertEqual(session.state, {"clientbound": "configuration", "serverbound": "configuration"})
