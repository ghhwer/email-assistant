def get_or_create_label_id(service, user_id, label_name):
    # Check if the label already exists
    labels = service.users().labels().list(userId=user_id).execute()
    for label in labels['labels']:
        if label['name'] == label_name:
            return label['id']

    # If the label doesn't exist, create it
    new_label = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    created_label = service.users().labels().create(userId=user_id, body=new_label).execute()

    return created_label['id']

def add_label_to_email(service, user_id, email_id, labels):
    message = service.users().messages().modify(
        userId=user_id,
        id=email_id,
        body={
            'addLabelIds': labels,
        }
    ).execute()

    print(f"Label '{labels}' were added to email with ID '{email_id}'.")

def mark_email_as_read(service, user_id, email_id):
    message = service.users().messages().modify(
        userId=user_id,
        id=email_id,
        body={
            'removeLabelIds': ['UNREAD'],
        }
    ).execute()

    print(f"Email with ID {email_id} marked as read.")
