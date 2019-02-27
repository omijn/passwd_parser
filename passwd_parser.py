import argparse
import json
import sys


class PasswdFieldEnum(object):
    USERNAME = 0
    UID = 2
    GECOS = 4
    TOTAL_FIELDS = 7


class GroupFieldEnum(object):
    GROUPNAME = 0
    USERS = 3
    TOTAL_FIELDS = 4


class FileFormatError(Exception):
    pass


def validate_passwd_format(user_data, line_num, users_encountered):
    if len(user_data) != PasswdFieldEnum.TOTAL_FIELDS:
        raise FileFormatError(
            "Couldn't parse line {} of '{}': expected {} values but found {}".format(line_num,
                                                                                     passwd_path,
                                                                                     PasswdFieldEnum.TOTAL_FIELDS,
                                                                                     len(user_data)))

    if user_data[PasswdFieldEnum.USERNAME] in users_encountered:
        raise FileFormatError(
            "Couldn't parse line {} of '{}': duplicate user '{}' found".format(line_num,
                                                                               passwd_path,
                                                                               user_data[PasswdFieldEnum.USERNAME]))


def validate_group_format(group_data, line_num, groups_encountered):
    if len(group_data) != GroupFieldEnum.TOTAL_FIELDS:
        raise FileFormatError(
            "Couldn't parse line {} of '{}': expected {} values but found {}".format(line_num,
                                                                                     passwd_path,
                                                                                     GroupFieldEnum.TOTAL_FIELDS,
                                                                                     len(group_data)))

    if group_data[GroupFieldEnum.GROUPNAME] in groups_encountered:
        raise FileFormatError(
            "Couldn't parse line {} of '{}': duplicate group '{}' found".format(line_num,
                                                                                group_path,
                                                                                group_data[GroupFieldEnum.GROUPNAME]))


def parse_passwd_file(passwd_file, user2groups):
    """
    Create a dictionary that contains all the user information we need

    :param passwd_file: path (string) to the passwd file
    :param user2groups: a dictionary that maps usernames to groups
    :return: a dictionary containing user and group information
    """

    parsed_data = {}
    users_encountered = set()

    with passwd_file:
        for index, user_data in enumerate(passwd_file.read().splitlines()):
            user_data = user_data.split(":")
            try:
                validate_passwd_format(user_data, index + 1, users_encountered)
            except Exception as e:
                sys.exit(str(e))

            username = user_data[PasswdFieldEnum.USERNAME]
            users_encountered.add(username)
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


def parse_group_file(group_file):
    """
    Create a mapping from users to groups

    :param group_file: path (string) to the group file
    :return: a dictionary with usernames as keys and lists of groups as values
    """

    user2groups = {}
    groups_encountered = set()

    with group_file:
        for index, group_data in enumerate(group_file.read().splitlines()):
            group_data = group_data.split(":")
            try:
                validate_group_format(group_data, index + 1, groups_encountered)
            except Exception as e:
                sys.exit(str(e))

            group_name = group_data[GroupFieldEnum.GROUPNAME]
            groups_encountered.add(group_name)
            users = group_data[GroupFieldEnum.USERS]
            if users == '':
                continue
            for user in users.split(","):
                if user not in user2groups:
                    user2groups[user] = []

                user2groups[user].append(group_name)

    return user2groups


parser = argparse.ArgumentParser(
    description='Parse the passwd and group files and combine the data into a single JSON output.')
parser.add_argument("-p", "--passwd", default='/etc/passwd',
                    help='Path to the passwd file. Defaults to /etc/passwd if not provided.')
parser.add_argument("-g", "--group", default='/etc/group',
                    help='Path to the group file. Defaults to /etc/group if not provided.')
parser.add_argument("-s", "--sorted", action='store_true', help='Sort keys of the JSON string alphabetically')
parser.add_argument("-c", "--compact", action='store_true',
                    help='Print the JSON string in a compact form. The default setting is to pretty-print the JSON.')
args = parser.parse_args()

passwd_path = args.passwd
group_path = args.group

try:
    passwd_file = open(passwd_path)
    group_file = open(group_path)
except Exception as e:
    sys.exit(str(e))

user2groups = parse_group_file(group_file)
parsed_data = parse_passwd_file(passwd_file, user2groups)
parsed_json = json.dumps(parsed_data, indent=None if args.compact else 4, sort_keys=args.sorted)

print(parsed_json)
