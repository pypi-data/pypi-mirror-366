import os, json
from datetime import timedelta

def getSecrets():
    secretString = os.environ.get('SECRET_STRING', None)
    secret_dict = None
    if secretString is not None:
        secret_dict = json.loads(secretString)
    return secret_dict

def getValueFromdDict(dict, key, default=""):
    if dict is not None:
        return dict.get(key, default)
    return default

def get_config_value(key, default=''):
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, key, default)
    return os.environ.get(key, default)


def environConfig (key, default=""):
    return os.environ.get(key, default)

def getDebugValue(default=False): 
    return get_config_value('DEBUG', default)

def getAdvancedDebugValue(default=False):
    return get_config_value('ADVANCED_DEBUG', default)

# Email configs
def getEmailHost(default=""): return get_config_value('email_host', default)
def getEmailPort(default=""): return get_config_value('email_port', default)
def getEmailUser(default=""): return get_config_value('email_user', default)
def getEmailPassword(default=""): return get_config_value('email_password', default)
def getEmailUseTLS(default=True): return get_config_value('email_use_tls', default)
def getEmailDefaultFromEmail(default=""): return get_config_value('email_default_from_email', default)
def getEmailBackend(default="django.core.mail.backends.console.EmailBackend"): return get_config_value('email_backend', default)
def getContactEmail(default=""): return get_config_value('contactus_email', default)

# Database configs
def getDBName(default=""): return get_config_value('dbname', default)
def getDBUser(default=""): return get_config_value('username', default)
def getDBHost(default=""): return get_config_value('host', default)
def getDBPort(default=""): return get_config_value('port', default)
def getDBPassword(default=""): return get_config_value('password', default)
def getDBEngine(default=""): return get_config_value('engine', default)

# AWS configs
def getRegionName(default=""): return get_config_value('region_name', default)
def getFileOverWrite(default=""): return get_config_value('file_overwrite', default)
def getACL(default=""): return get_config_value('default_acl', default)
def getSignatureVersion(default=""): return get_config_value('signature_version', default)
def getAWSAccessKey(default=""): return get_config_value('access_key', default)
def getAWSSecretKey(default=""): return get_config_value('secret_access_key', default)
def getBucketName(default=""): return get_config_value('bucket_name', default)

#AWS Bedrock configs
def getBedrockModelId(default=""): return get_config_value('bedrock_model_id', default)
def getBedrockEndpointUrl(default=""): return get_config_value('bedrock_endpoint_url', default)
def getBedrockKnowledgeBaseId(default=""): return get_config_value('bedrock_knowledge_base_id', default)
def getBedrockMaxTokens(default=0):
    value = get_config_value('bedrock_max_tokens', default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def getBedrockTemperature(default=0.0):
    value = get_config_value('bedrock_temperature', default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def getBedrockKnowledgeDataSourceId(default=""): return get_config_value('bedrock_knowledge_data_source_id', default)
def getBedrockKnowledgeBasicAgentID(default=""): return get_config_value('bedrock_knowledge_basic_agent_id', default)
def getBedrockKnowledgeBasicAgentAliasID(default=""): return get_config_value('bedrock_knowledge_basic_agent_alias_id', default)
def getBedrockKnowledgeEvidenceCollectionAgentID(default=""): return get_config_value('bedrock_knowledge_evidence_collection_agent_id', default)
def getBedrockKnowledgeEvidenceCollectionAgentAliasID(default=""): return get_config_value('bedrock_knowledge_evidence_collection_agent_alias_id', default)

def getAIDailyLimit(default=50000): 
    value = get_config_value('ai_daily_limit', default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def getAIWarningThreshold(default=80):
    value = get_config_value('ai_warning_threshold', default) 
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def getAIVisualMultiplier(default=2.0):
    value = get_config_value('ai_visual_multiplier', default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# Microsoft Creds
def getMicrosoftClientID(default=""): return get_config_value('microsoft_client_id', default)
def getMicrosoftClientSecret(default=""): return get_config_value('microsoft_client_secret', default)

# SAML configs
def getXMLSecBinaryPath(default=""): return get_config_value('xmlsec_binary_path', default)
def getSamlLoginURL(default=""): return get_config_value('saml_login_url', default)

# Google Creds
def getGoogleClientID(default=""): return get_config_value('google_client_id', default)
def getGoogleClientSecret(default=""): return get_config_value('google_client_secret', default)

# Account Email Subject Prefix
def getAccountEmailSubjectPrefix(default=""): return get_config_value('account_email_subject_prefix', default)

# Internal IP
def getInternalIPs(default=[]): return get_config_value('internal_ips', [])

# Site and Domain
def getSiteID(default=1):
    site_id = get_config_value('site_id', default)
    try:
        return int(site_id)
    except ValueError:
        return default

# Encrypted Model Fields Key
def getEncryptedModelFieldsKey(default=""): return get_config_value('encrypted_model_fields_key', default)


# Ironfort Support Email
def getIronfortSupportEmail(default=""): return get_config_value('support_email', default)


# Temporary OTP Code
def getTempOTPCode(default=""): return get_config_value('temp_otp_code', default)


def get_logger_engine(default=""): return get_config_value('logger_engine', default)

def get_product_name(default=""):
    return get_config_value('product_name', default)

def get_app_name(default=""):
    return get_config_value('app_name', default)

def get_tier(default=""):
    return get_config_value('tier', default)

def get_group_name(default=""):
    return get_config_value('group_name', default)

def get_group_name_cloudwatch_logs(default=""):
    return get_config_value('group_name_cloudwatch_logs', default)


def getRestFrameworkPageSize(default=10):
    return get_config_value('rest_framework_page_size', default)

def getAccessTokenLifetime(default=1):
    return get_config_value('access_token_lifetime', default)

def getRefreshTokenLifetime(default=7):
    return get_config_value('refresh_token_lifetime', default)
