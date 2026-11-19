import unittest
from error_codes_network import (
    parity_bit, build_table, ones_sum, xor_divide,
    hamming_encode, hamming_syndrome, hamming_data,
)


class TestParity(unittest.TestCase):
    def test_even_parity(self):
        self.assertEqual(parity_bit("1011001"), "0")
        self.assertEqual(parity_bit("1011000"), "1")

    def test_2d_table(self):
        table = build_table(["1001", "1101", "1111"])
        self.assertEqual(table, ["10010", "11011", "11110", "10111"])


class TestChecksum(unittest.TestCase):
    def test_sum_with_carry(self):
        self.assertEqual(ones_sum(["10110011", "01101001"], 8), 0b00011101)

    def test_receiver_gets_all_ones(self):
        checksum = format(255 - ones_sum(["10110011", "01101001"], 8), "08b")
        self.assertEqual(checksum, "11100010")
        self.assertEqual(ones_sum(["10110011", "01101001", checksum], 8), 255)


class TestCRC(unittest.TestCase):
    def test_remainder(self):
        self.assertEqual(xor_divide("1101011011" + "0000", "10011"), "1110")

    def test_valid_frame_has_zero_remainder(self):
        self.assertEqual(xor_divide("11010110111110", "10011"), "0000")

    def test_single_bit_error_detected(self):
        self.assertNotEqual(xor_divide("11010110101110", "10011"), "0000")


class TestHamming(unittest.TestCase):
    def test_encode_7_4(self):
        self.assertEqual(hamming_encode("1011"), "0110011")

    def test_no_error(self):
        self.assertEqual(hamming_syndrome("0110011"), 0)

    def test_every_single_bit_error_is_located(self):
        code = "0110011"
        for pos in range(1, 8):
            bad = code[:pos - 1] + ("1" if code[pos - 1] == "0" else "0") + code[pos:]
            self.assertEqual(hamming_syndrome(bad), pos)

    def test_extract_data(self):
        self.assertEqual(hamming_data("0110011"), "1011")


if __name__ == "__main__":
    unittest.main()
