from dataclasses import dataclass
import pwd as password_database
import grp as group_database


type User = password_database.struct_passwd
type Group = group_database.struct_group


class UserNotFoundError(Exception):
    pass


class GroupNotFoundError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


class AccountMissingUserError(Exception):
    pass


class AccountMissingGroupError(Exception):
    pass


@dataclass(frozen=True)
class Account:
    user: User
    group: Group


def get_user(username: str) -> User:
    try:
        return password_database.getpwnam(username)
    except KeyError as error:
        raise UserNotFoundError from error


def get_group(groupname: str) -> Group:
    try:
        group_entry = group_database.getgrnam(groupname)
    except KeyError as error:
        raise GroupNotFoundError from error

    return group_entry


def get_account(username: str) -> Account:
    user_entry: User | None = None
    user_error: UserNotFoundError | None = None
    try:
        user_entry = get_user(username)
    except UserNotFoundError as error:
        user_error = error

    group_entry: Group | None = None
    group_error: GroupNotFoundError | None = None
    try:
        group_entry = get_group(username)
    except GroupNotFoundError as error:
        group_error = error

    if user_error is not None and group_error is not None:
        raise AccountNotFoundError from ExceptionGroup("", (user_error, group_error))

    if user_error is not None:
        raise AccountMissingUserError from user_error

    if group_error is not None:
        raise AccountMissingGroupError from group_error

    assert user_entry is not None
    assert group_entry is not None

    return Account(user_entry, group_entry)
