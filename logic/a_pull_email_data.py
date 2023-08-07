from vendor.gmail import get_gmail_service 
from tools.io import read_json_file, save_data_as_json


import base64
import re
import json

from urllib.parse import unquote

def find_from(message_payload):
    headers = message_payload.get('headers', [])
    return [data.get('value') for data in headers if 'From' in data.get('name', '')]
def find_subject(message_payload):
    headers = message_payload.get('headers', [])
    return [data.get('value') for data in headers if 'Subject' in data.get('name', '')]
def find_delivered_to(message_payload):
    headers = message_payload.get('headers', [])
    return [data.get('value') for data in headers if 'Delivered-To' in data.get('name', '')]
def find_content_type(headers):
    data = [data.get('value') for data in headers if 'Content-Type' in data.get('name', '')]
    return data[0] if len(data) > 0 else None
def find_content_transfer_encoding(headers):
    data = [data.get('value') for data in headers if 'Content-Transfer-Encoding' in data.get('name', '')]
    return data[0] if len(data) > 0 else None


def clean_base64(base64_text):
    # Replace "-" with "+" and "_" with "/"
    cleaned_text = base64_text.replace('-', '+').replace('_', '/')
    # Decode the modified base64 string
    decoded_text = base64.b64decode(unquote(cleaned_text) + "=" * (-len(cleaned_text) % 4))
    return decoded_text

def clean_msg(headers, message_payload):
    content_type = find_content_type(headers)
    #content_transfer_encoding = find_content_transfer_encoding(headers)
    # Define charset
    pattern = r'charset="([^"]+)"'
    charset = re.search(pattern, content_type)
    if charset:
        charset = charset.group(1)
    else:
        charset = 'utf-8'
    data = message_payload['data']
    data = clean_base64(data)

    return data.decode(charset)

def message_full_recursion(m):
    html, text = '', ''
    if m is None:
        return m, m
    for i in m:
        mimeType = (i['mimeType'])
        if (mimeType == 'text/plain'):
            text += clean_msg(i.get('headers', []), i.get('body', {}))
        if (mimeType == 'text/html'):
            html += clean_msg(i.get('headers', []), i.get('body', {}))
        elif 'parts' in i:
            html_aux, text_aux = message_full_recursion(i['parts'])
            html += html_aux
            text += text_aux
    return html, text

def get_emails_paginated(userId, labelIds, service, q=None):
    exit, pageToken = False, None
    while not exit:
        unread_msgs = service.users().messages().list(userId=userId,labelIds=labelIds, pageToken=pageToken, q=q).execute()
        mssg_list, pageToken = unread_msgs.get('messages', []), unread_msgs.get('nextPageToken', None)
        print ("Total unread messages in inbox in page: ", str(len(mssg_list)))
        for mssg in mssg_list:
            yield mssg
        if pageToken is None:
            exit = True


def list_emails(service, user_id = 'me', labels = ['INBOX', 'UNREAD']):
    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    unread_msgs = get_emails_paginated(userId='me',labelIds=labels, service=service, q='-(label: read-by-ai)')
    # We get a dictonary. Now reading values for the key 'messages'
    final_list = [ ]
    for mssg in unread_msgs:
        m_id = mssg['id']
        print(f'reading email: {m_id}')
        message = service.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
        payload = message.get('payload')
        parts = payload.get('parts', None)
        html, plain_text_message = message_full_recursion(parts)
        msg_fwd = {
            'id':m_id,
            'current_labels':message.get('labelIds', []),
            'snippet': message.get('snippet', []),
            'from': find_from(payload),
            'subject': find_subject(payload),
            'delivered_to': find_delivered_to(payload),
            'message': plain_text_message,
            'html': html
        }
        final_list.append(msg_fwd)
    print(len(final_list), 'messages after filtering')
    return final_list


def fetch_email_json(human_preferences, service):
    data = list_emails(
        service, 
        user_id=human_preferences.get('user_id'),
        labels=human_preferences.get('ai_read_labels', ['INBOX', 'UNREAD'])
    )
    if(data == False):
        return data
    save_data_as_json('batch_process_mails.json', data)
    return True

if __name__ == '__main__':
    human_preferences = read_json_file('human_preferences.json')
    service = get_gmail_service()
    fetch_email_json(human_preferences, service)