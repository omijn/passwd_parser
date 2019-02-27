import argparse
import json
import os


class PasswdFieldEnum(object):
    USERNAME = 0
    UID = 2
    GECOS = 4


class GroupFieldEnum(object):
    GROUPNAME = 0
    USERS = 3


class FileFormatError(Exception):
    pass


# FileNotFoundError and PermissionError aren't available in Python 2, so define them
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    PermissionError
except NameError:
    PermissionError = IOError


def verify_file_readable(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError("File '{}' not found.".format(filepath))
    if not os.access(filepath, os.R_OK):
        raise PermissionError("Insufficient read permissions for file '{}'".format(filepath))


def validate_passwd_format(user_data, line_num):
    if len(user_data) != 7:
        raise FileFormatError(
            "There was an error parsing line {} of the passwd file '{}'.".format(line_num, passwd_path))


def validate_group_format(group_data, line_num):
    if len(group_data) != 4:
        raise FileFormatError("There was an error parsing line {} of the group file '{}'.".format(line_num, group_path))


def parse_passwd_file(passwd_path, user2groups):
    """
    Create a dictionary that contains all the user information we need

    :param passwd_path: path (string) to the passwd file
    :param user2groups: a dictionary that maps usernames to groups
    :return: a dictionary containing user and group information
    """

    parsed_data = {}

    with open(passwd_path) as passwd_file:
        for index, user_data in enumerate(passwd_file.read().splitlines()):
            user_data = user_data.split(":")
            validate_passwd_format(user_data, index + 1)

            username = user_data[PasswdFieldEnum.USERNAME]
            uid = user_data[PasswdFieldEnum.UID]
            gecos = user_data[PasswdFieldEnum.GECOS]
            fullname = gecos.split(",")[0]
            groups = user2groups[username] if username in user2groups else []

            parsed_data[username] = {
                "uid": uid,
                "full_name": fullname,
                "groups": groups
            }

    return parsed_data


def parse_group_file(group_path):
    """
    Create a mapping from users to groups

    :param group_path: path (string) to the group file
    :return: a dictionary with usernames as keys and lists of groups as values
    """

    user2groups = {}

    with open(group_path) as group_file:
        for index, group_data in enumerate(group_file.read().splitlines()):
            group_data = group_data.split(":")
            validate_group_format(group_data, index + 1)

            users = group_data[GroupFieldEnum.USERS]
            if users == '':
                continue
            for user in users.split(","):
                if user not in user2groups:
                    user2groups[user] = []
                else:
                    user2groups[user].append(group_data[GroupFieldEnum.GROUPNAME])

    return user2groups


parser = argparse.ArgumentParser(description='Parse the passwd and group files and combine the data into a single JSON output.')
parser.add_argument("-p", "--passwd", default='/etc/passwd', help='Path to the passwd file. Defaults to /etc/passwd if not provided.')
parser.add_argument("-g", "--group", default='/etc/group', help='Path to the group file. Defaults to /etc/group if not provided.')
parser.add_argument("-s", "--sorted", action='store_true', help='Sort keys of the JSON string alphabetically')
parser.add_argument("-c", "--compact", action='store_true', help='Print the JSON string in a compact form. The default setting is to pretty-print the JSON.')
args = parser.parse_args()

passwd_path = args.passwd
group_path = args.group

verify_file_readable(passwd_path)
verify_file_readable(group_path)

user2groups = parse_group_file(group_path)
parsed_data = parse_passwd_file(passwd_path, user2groups)
parsed_json = json.dumps(parsed_data, indent=None if args.compact else 4, sort_keys=args.sorted)

print(parsed_json)
