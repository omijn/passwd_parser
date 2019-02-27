import unittest
import passwd_parser as parser


class TestPasswdParser(unittest.TestCase):
    def test_validate_group(self):
        with self.assertRaises(parser.FileFormatError):
            parser.validate_group_format("operator:x:37::".split(), 26)
            parser.validate_group_format("::::".split(), 1)
            parser.validate_passwd_format("", 1)

    def test_validate_passwd(self):
        with self.assertRaises(parser.FileFormatError):
            parser.validate_passwd_format("www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin:", 13)
            parser.validate_passwd_format("", 1)


if __name__ == '__main__':
    unittest.main()
