# Load the env
from tools.load_env import load_env
load_env()

from logic.a_pull_email_data import fetch_email_json
from logic.b_ai_read_emails import run_ai_read_emails
from logic.c_apply_ai_decisions import run_apply_changes
from logic.d_manage_decisions import manage_historical_folder

from vendor.gmail import get_gmail_service 
from tools.io import read_json_file, save_data_as_json


if __name__ == '__main__':
    # Get the service and human preferences
    service = get_gmail_service()
    human_preferences = read_json_file('human_preferences.json')
    # Fetch emails using JSON
    new_emails = fetch_email_json(human_preferences, service)
    if (new_emails == False):
        print('No new mails')
        exit()
    batch_process_mails = read_json_file('batch_process_mails.json')
    # Process the emails  
    run_ai_read_emails(batch_process_mails, human_preferences, concurrent_tasks=5)
    batch_ai_decisions = read_json_file('batch_ai_decisions.json')
    # Push the changes out to gmail
    run_apply_changes(service, human_preferences, batch_ai_decisions)    
    # Manage the historical data
    manage_historical_folder(months_delta=6, file_list=['batch_process_mails.json', 'batch_ai_decisions.json'])
