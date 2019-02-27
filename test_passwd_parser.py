import io
import unittest
import passwd_parser as parser


class TestPasswdParser(unittest.TestCase):
    def test_validate_group(self):
        # entries with incorrect number of fields should cause failure
        with self.assertRaises(parser.FileFormatError):
            parser.validate_group_format("operator:x:37::".split(":"), 26, set())

        with self.assertRaises(parser.FileFormatError):
            parser.validate_group_format("::::".split(":"), 1, set())

        with self.assertRaises(parser.FileFormatError):
            parser.validate_group_format("".split(":"), 1, set())

        # entries with duplicate groups should cause failure
        with self.assertRaises(parser.FileFormatError):
            parser.validate_group_format("whoopsie:x:112:".split(":"), 1, {"whoopsie"})

        # valid entries should not raise an exception
        try:
            parser.validate_group_format("scanner:x:118:saned".split(":"), 1, set())
        except parser.FileFormatError:
            self.fail("FileFormatException unexpectedly raised for correct input.")

    def test_validate_passwd(self):
        # entries with incorrect number of fields should cause failure
        with self.assertRaises(parser.FileFormatError):
            parser.validate_passwd_format("www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin:".split(":"), 13, set())

        with self.assertRaises(parser.FileFormatError):
            parser.validate_passwd_format("".split(":"), 1, set())

        # entries with duplicate users should cause failure
        with self.assertRaises(parser.FileFormatError):
            parser.validate_passwd_format("whoopsie:x:112:117::/nonexistent:/bin/false".split(":"), 1, {"whoopsie"})

        # valid entries should not raise an exception
        try:
            parser.validate_passwd_format("whoopsie:x:112:117::/nonexistent:/bin/false".split(":"), 1, set())
        except parser.FileFormatError:
            self.fail("FileFormatException unexpectedly raised for correct input.")

    def test_parse_group_file(self):
        mock_group_file = io.StringIO(
            "whoopsie:x:117:\n" +
            "scanner:x:118:saned\n" +
            "saned:x:119:\n" +
            "pulse:x:120:saned,www-data\n" +
            "pulse-access:x:121:\n" +
            "avahi:x:122:\n" +
            "colord:x:123:")

        mock_parse = {
            "saned": ["scanner", "pulse"],
            "www-data": ["pulse"]
        }

        self.assertEqual(mock_parse, parser.parse_group_file(mock_group_file))

    def test_parse_passwd_file(self):
        mock_passwd_file = io.StringIO("whoopsie:x:112:117::/nonexistent:/bin/false\n" +
                                       "kernoops:x:113:65534:Kernel Oops Tracking Daemon,,,:/:/usr/sbin/nologin\n" +
                                       "saned:x:114:119::/var/lib/saned:/usr/sbin/nologin\n" +
                                       "pulse:x:115:120:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin\n" +
                                       "avahi:x:116:122:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin\n" +
                                       "colord:x:117:123:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin")

        mock_user2groups = {
            "saned": ["scanner", "pulse"],
            "www-data": ["pulse"]
        }

        mock_parse = {
            "whoopsie": {
                "uid": "112",
                "full_name": "",
                "groups": []
            },

            "kernoops": {
                "uid": "113",
                "full_name": "Kernel Oops Tracking Daemon",
                "groups": []
            },

            "saned": {
                "uid": "114",
                "full_name": "",
                "groups": ["scanner", "pulse"]
            },

            "pulse": {
                "uid": "115",
                "full_name": "PulseAudio daemon",
                "groups": []
            },

            "avahi": {
                "uid": "116",
                "full_name": "Avahi mDNS daemon",
                "groups": []
            },

            "colord": {
                "uid": "117",
                "full_name": "colord colour management daemon",
                "groups": []
            },
        }

        self.assertEqual(mock_parse, parser.parse_passwd_file(mock_passwd_file, mock_user2groups))


if __name__ == '__main__':
    unittest.main()
