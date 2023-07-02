import os
import shutil
from datetime import datetime, timedelta

def move_files_to_historical_folder(file_list, historical_folder_path):
    # Create the historical folder if it doesn't exist
    if not os.path.exists(historical_folder_path):
        os.makedirs(historical_folder_path)

    # Move files to the historical folder
    for file_path in file_list:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            destination_folder = datetime.now().strftime("%Y%m%d%H%M%S")
            destination_path = os.path.join(historical_folder_path, destination_folder, file_name)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.move(file_path, destination_path)
            print(f"Moved '{file_name}' to the historical folder.")
        else:
            print(f"File '{file_path}' does not exist.")

def remove_folders_before_date_delta(historical_folder_path, months_delta):
    current_date = datetime.now()
    cutoff_date = current_date - timedelta(days=months_delta * 30)
    removed_folders_count = 0

    for folder_name in os.listdir(historical_folder_path):
        folder_path = os.path.join(historical_folder_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        folder_date = datetime.strptime(folder_name, "%Y%m%d%H%M%S")
        if folder_date < cutoff_date:
            shutil.rmtree(folder_path)
            print(f"Removed folder '{folder_name}' from the historical folder.")
            removed_folders_count += 1

    print(f"Total folders removed: {removed_folders_count}.")

def manage_historical_folder(months_delta = 6, file_list = ['batch_process_mails.json','batch_ai_decisions.json']):
    historical_folder_path = '__history__'
    # Call the function to move the files to the historical folder
    move_files_to_historical_folder(file_list, historical_folder_path)
    # Call the function to remove files before a date delta in months
    remove_folders_before_date_delta(historical_folder_path, months_delta)


if __name__ == '__main__':
    manage_historical_folder()