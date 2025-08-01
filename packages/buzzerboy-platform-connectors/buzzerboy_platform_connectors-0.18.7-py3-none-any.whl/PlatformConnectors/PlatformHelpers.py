import os
from django.core.mail import send_mail
from smtplib import SMTPRecipientsRefused
from pathlib import Path
import json

import logging
logger = logging.getLogger(__name__)


def addHttpPrefix(url):
    result = {'http': '', 'https': ''}
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
        result = {'http': url, 'https': url.replace('http://', 'https://')} 

    return result

def allowHostCSVtoArray (csvString):
    if csvString == '*':
        return ['*']
    else:
        arr= [origin.strip() for origin in csvString.split(',')]
        #remove any traling slashes that might be in the array
        arr = [origin.rstrip('/') for origin in arr]
        return arr
    

def removeHttpPrefix(url):
    return url.replace('http://', '').replace('https://', '')

def getCSRFHostsFromAllowedHosts (allowedHostsArray):
    result = []
    for host in allowedHostsArray:
        cleanHost = removeHttpPrefix(host)
        
        #only append to result if the result does not already include the value in cleanHost
        if not cleanHost in result:
            result.append(addHttpPrefix(cleanHost)['http'])
            result.append(addHttpPrefix(cleanHost)['https'])
    return result


def getAllowedHosts():
    ALLOWED_HOSTS_CSV = os.getenv('ALLOWED_HOSTS_CSV', '*')
    ALLOWED_HOSTS = ['127.0.0.1']


    try:
        ALLOWED_HOSTS.append(socket.gethostbyname(socket.gethostname()))
    except Exception as e:
        ALLOWED_HOSTS.append('127.0.0.1')
    ALLOWED_HOSTS += allowHostCSVtoArray(ALLOWED_HOSTS_CSV)
    return ALLOWED_HOSTS


def getCSRFTrustedOrigins():
    CSRF_TRUSTED_ORIGINS = ['http://localhost:85', 'http://127.0.0.1', 'http://localhost:8000']
    CSRF_TRUSTED_ORIGINS = getCSRFHostsFromAllowedHosts(getAllowedHosts())

    return CSRF_TRUSTED_ORIGINS


def GetEmailTemplate(template_name, variablesDict, BASE_DIR):
    """
    Get the email template with the given name and replace the variables with the provided values.
    
    Parameters:
    - template_name: The name of the email template file.

    Returns:
    - template: The email template with the variables replaced. 
    """

    filename = os.path.join(BASE_DIR, 'email_templates', template_name)


    #read contents of file name into template
    with open(filename, 'r') as file:
        template = file.read()
        logger.debug(template)
        file.close()

    #replace variables in template with values from variablesDict
    for key, value in variablesDict.items():
        template = template.replace('{{'+key+'}}', value.__str__())

    return template

def send_email (subject, message, recipient_list, from_email, **kwargs):
    """
    Send an email to the specified recipients with the given subject and message.
    
    Parameters:
    - subject: The subject of the email.
    - message: The message content of the email.
    - recipient_list: A list of email addresses to which the email should be sent.
    - from_email: The email address from which the email should be sent.
    - kwargs: Additional keyword arguments to pass to the send_mail function.


    Comments:
    - This function sends an email to the specified recipients with the given subject and message.
    - The from_email parameter specifies the email address from which the email should be sent.
    - Additional keyword arguments can be passed to the send_mail function.
    """


    logger.debug(f'subject: {subject}')
    logger.debug(f'message: {message}')
    logger.debug(f'recipient_list: {recipient_list}')
    logger.debug(f'from_email: {from_email}')
    logger.debug(f'kwargs: {kwargs}')
    
    #set content type to html
    kwargs['html_message'] = message
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, **kwargs)
    except SMTPRecipientsRefused:
        logger.error(f"Failed to send email to {recipient_list}. SMTPRecipientsRefused error.")





def LoadChoicesFromFile(file_name, prefixFolder='fixtures/'):

    CHOICE_FILE = f'{prefixFolder}{file_name}.json'
    with open(CHOICE_FILE) as file:
        choice_data = json.load(file)
    CHOICES = [(row['value'], row['label']) for row in choice_data]
    return CHOICES

def GetJsonFileContent(file_name, prefixFolder='fixtures/'):
    try:
        JSON_FILE = f'{prefixFolder}{file_name}.json'
        with open(JSON_FILE) as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"JSON file {file_name} not found in fixtures directory")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in {file_name}.json")