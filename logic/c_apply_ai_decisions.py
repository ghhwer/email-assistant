from tools.io import read_json_file 
from vendor.gmail import get_gmail_service
from vendor.gmail.gmail_functions import (
    get_or_create_label_id,
    add_label_to_email,
    mark_email_as_read
)

def run_apply_changes(service, human_preferences, batch_ai_decisions):
    my_labels = human_preferences.get("my_labels")
    user_id = human_preferences.get("user_id")
    
    my_labels += ['flagged-as-ad', 'flagged-as-urgent', 'read-by-ai', 'ai-failed-to-classify']
    label_meta = {label: get_or_create_label_id(service, user_id, label) for label in my_labels}
    for decision in batch_ai_decisions:
        label_ids = []
        label_ids.append(label_meta['read-by-ai'])
        if(decision.get('status') == True):
            ai_response = decision.get('response', {}).get('decision')
            mail_id = ai_response.get('email_id')
            new_folder = ai_response.get('new_folder')
            is_ad = ai_response.get('is_ad')
            is_urgent = ai_response.get('is_urgent')
            assistent_notes = ai_response.get('assistent_notes')
            # Logic to make folder precedent
            if is_urgent:
                # AI thinks it is urgent
                label_ids.append(label_meta['flagged-as-urgent'])
            elif is_ad:
                # AI thinks it is an ad
                label_ids.append(label_meta['flagged-as-ad'])
            
            label_ids.append(label_meta[new_folder])
            #mark_email_as_read(service, user_id, mail_id)
        else:
            # Status is False, add to read by AI and not abble to classify
            label_meta['ai-failed-to-classify']
        add_label_to_email(service, user_id, mail_id, label_ids)

if __name__ == '__main__':
    human_preferences = read_json_file('human_preferences.json')
    batch_ai_decisions = read_json_file('batch_ai_decisions.json')
    service = get_gmail_service()
    run_apply_changes(human_preferences, batch_ai_decisions, service)