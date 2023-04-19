"""User (Auth) related APIs."""

import jwt
import time
import logging
import pymongo
from be.model import error
from be.model.mongo_manager import get_user_col


def jwt_encode(user_id: str, terminal: str) -> str:
    """Tool function to encode a json to JWT.
    Encode a json string like:
    {
        "user_id": [user name],
        "terminal": [terminal code],
        "timestamp": [ts]} to a JWT
    }

    Parameters
    ----------
    user_id : str
        The "user_id" data in the user document.

    terminal : str
        The "terminal" data in the user document.

    Returns
    -------
    The encoded string.
    """
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


def jwt_decode(encoded_token: str, user_id: str) -> str:
    """Tool function to decode a JWT to a json string like:
    {
        "user_id": [user name],
        "terminal": [terminal code],
        "timestamp": [ts]} to a JWT
    }

    Parameters
    ----------
    encoded_token : str
        Token used in the jwt.

    user_id : str
        The "user_id" data in the user document.

    Returns
    -------
    The decoded string.
    """
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class UserAPI:
    """Backend APIs related to user manipulation."""

    token_lifetime: int = 3600  # 3600 second

    def __check_token(self, user_id, db_token, token) -> bool:
        """Check whether the token is matched in the database.

        Parameters
        ----------
        user_id : str
            The "user_id" data in the user document.

        db_token : str
            The token from the database.

        token : str
            The token waiting to be valided.

        Returns
        -------
        ret : bool
            Whether the token is valid.
        """
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str) -> (int, str):
        """User register.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            get_user_col().insert_one(
                {
                    "_id": user_id,
                    "password": password,
                    "balance": 0,
                    "token": token,
                    "terminal": terminal,
                }
            )
        except pymongo.errors.DuplicateKeyError as e:
            return error.error_exist_user_id(user_id)
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        """Check token (public API).

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        token : str
            The token to be checked.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_authorization_fail()
            db_token = cursor["token"]
            if not self.__check_token(user_id, db_token, token):
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        """Check password for an account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password to be checked.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_authorization_fail()
            if password != cursor["password"]:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        """Account login.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        terminal : str
            Terminal code of the account.

        Returns
        -------
        (code : int, msg : str, token : str)
            The return status. Note that it will return the token.
        """
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            cursor = get_user_col().update_one(
                {"_id": user_id},
                {"$set": {"token": token, "terminal": terminal}},
            )

            # Otherwise it will return in check_password
            assert cursor.matched_count > 0
            assert cursor.modified_count == cursor.matched_count
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> (int, str):
        """Account logout.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        token : str
            Token generated by last login.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            cursor = get_user_col().update_one(
                {"_id": user_id},
                {"$set": {"token": dummy_token, "terminal": terminal}},
            )

            # Otherwise it will return in check_token
            assert cursor.matched_count > 0
            assert cursor.modified_count == cursor.matched_count
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        """Unregister the account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            cursor = get_user_col().delete_one({"_id": user_id})
            if cursor.deleted_count != 1:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> (int, str):
        """Change password for an account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        old_password : str
            Old password of the account.

        new_password : str
            New password of the account.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            cursor = get_user_col().update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "password": new_password,
                        "token": token,
                        "terminal": terminal,
                    }
                },
            )

            # Otherwise it will return in check_password
            assert cursor.matched_count > 0
            assert cursor.modified_count == cursor.matched_count
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"
