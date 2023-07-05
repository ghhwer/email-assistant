from bs4 import BeautifulSoup
import re
import json

from tools.threaded_pool import ThreadPool
from tools.io import save_data_as_json, read_json_file
from vendor.AI.email_assistent import ai_organize_email

def clean_html(html_text):
    # Remove HTML tags
    soup = BeautifulSoup(html_text, 'html.parser')
    cleaned_text = soup.get_text(separator=' ')
    return cleaned_text

def simple_format_clean_text(text):
    text = text.replace('\u200c', '')
    text = re.sub(r'\t', '', text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r' +', ' ', text).strip()
    return text

# ==== AI PARALLEL START ====
def ai_task_run(id, sender, recipient, subject, contains_html, normalized_body, available_folders, retries=3):
    print(f'AI is looking at email: {id}')
    delegated_task_status, response = False, {}
    for i in range(retries):
        try:
            print(f'AI has made a decision about the email: {id}')
            response = ai_organize_email(id, sender, recipient, subject, contains_html, normalized_body, available_folders)
            delegated_task_status = True
            break
        except Exception as e:
            print(f'AI has failed to make a decision about the email: {id}, retying ({i+1}/{retries})')
            print(f'{e}')
            delegated_task_status = False
            response = {'error': f'{e}'}
    return {
        'status': delegated_task_status,
        'response': response
    }
# ==== AI PARALLEL END ====

def run_ai_read_emails(emails, human_preferences, concurrent_tasks=5):    
    # Create tasks
    tasks = []
    for email in emails:
        email_html = email.get('html', None)
        email_message = email.get('message', None)
        email_snippet = email.get('snippet', None)
        email_subject = email.get('subject', 'NONE')
        
        is_html, email_body_norm = False, ''
        if not email_html is None:
            is_html = True
            email_body_norm = clean_html(email_html)
        elif not email_message is None:
            email_body_norm = email_message
        elif not email_snippet is None:
            email_body_norm = email_snippet
        else:
            email_body_norm = email_subject
        email_body_norm = simple_format_clean_text(email_body_norm)
        tasks.append({
            'kwargs':{
                'id':                   email.get('id'),
                'sender':               email.get('from'),
                'recipient':            email.get('delivered_to'),
                'subject':              email.get('subject'),
                'contains_html':        is_html,
                'normalized_body':      email_body_norm,
                'available_folders':    human_preferences.get('my_labels')
            }
        })
    tp = ThreadPool(concurrent_tasks, ai_task_run, tasks)
    tp.run()
    save_data_as_json('batch_ai_decisions.json', tp.results)

if __name__ == '__main__':
    emails = read_json_file('batch_process_mails.json')
    human_preferences = read_json_file('human_preferences.json')
    run_ai_read_emails(emails, human_preferences)