import hmac
import hashlib
import base64
import logging
from bson.objectid import ObjectId
from alfred.config import SECRET_KEY_1, SALT

logger = logging.getLogger(__name__)


def encrypt(value: str, key: str = SECRET_KEY_1):
    digest = hmac.new(bytes(key, "utf-8"), msg=bytes(SALT + value, "utf-8"), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    return signature


def hash_dict_values(d):
    """
    Recursively traverses dictionary hashing the string fields prefixed with "hashed:"
    :params d: dictioanry to hash
    :returns dictionary (w/hashed string values)
    """
    for k, v in d.items():
        if type(v) is dict:
            d[k] = hash_dict_values(v)
        elif type(v) is str:
            if "hashed:" in k:
                signature = encrypt(v, key=SECRET_KEY_1)
                d[k] = signature
    return d


def convert_object_ids(d):
    """
    Recursively traverses dictionary converting the mongodb ObjectId values to strings
    :params d: dictioanry to convert
    :returns dictionary (w/string formatted ObjectId fields)
    """
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = convert_object_ids(v)
        else:
            if type(v) is ObjectId:
                d[k] = str(v)
    return d
