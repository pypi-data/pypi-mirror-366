import os, json

def getSecrets():
    secretString = os.environ.get('SECRET_STRING', None)
    secret_dict =  None

    if secretString is not None:
        secret_dict = json.loads(secretString)

    return secret_dict

def getValueFromdDict(dict, key, default=""):
    if dict is not None:
        return dict.get(key, default)
    return default

def getEmailHost(default=""):
    SECRET_IDENTIFIER = "email_host"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getEmailPort(default=""):
    SECRET_IDENTIFIER = "email_port"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)


def getEmailUser(default=""):
    SECRET_IDENTIFIER = "email_user"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getEmailPassword(default=""):
    SECRET_IDENTIFIER = "email_password"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getEmailUseTLS(default=True):
    SECRET_IDENTIFIER = "email_use_tls"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getEmailDefaultFromEmail(default=""):
    SECRET_IDENTIFIER = "email_default_from_email"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getEmailBackend(default="django.core.mail.backends.console.EmailBackend"):
    SECRET_IDENTIFIER = "email_backend"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)
  

def getDBName(default=""):
    SECRET_IDENTIFIER = "dbname"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getDBUser(default=""):
    SECRET_IDENTIFIER = "username"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getDBHost(default=""):
    SECRET_IDENTIFIER = "host"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)


def getDBPort(default=""):
    SECRET_IDENTIFIER = "port"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)

def getDBPassword(default=""):
    SECRET_IDENTIFIER = "password"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)


def getDBEngine(default=""):
    SECRET_IDENTIFIER = "engine"
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, SECRET_IDENTIFIER, default)
    return os.environ.get(SECRET_IDENTIFIER, default)