import unittest
import serial

# ~  print serial.VERSION

# on which port should the tests be performed:
PORT = "loop://"


class Test_Read_Until(unittest.TestCase):
    """Test read_until function"""

    def setUp(self):
        self.ser = serial.serial_for_url(PORT, timeout=1)
        self.msg = serial.to_bytes([0x46, 0x4F, 0x4F])

    def tearDown(self):
        self.ser.close()

    def test_read_until_using_single_delimiter(self):
        delimiter = b"\r"
        msg = self.msg + delimiter
        self.ser.write(msg)
        self.assertEqual(self.ser.read_until(delimiter), msg)

    def test_read_until_using_multiple_delimiters(self):
        delimiters = (b"\r", b"\a")
        msg = self.msg + delimiters[0] + delimiters[-1]

        self.ser.write(msg)
        self.assertEqual(self.ser.read_until(delimiters), self.msg + delimiters[0])

        self.ser.write(msg[::-1])
        self.assertEqual(self.ser.read_until(delimiters), delimiters[-1])
