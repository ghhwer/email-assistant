# email-assistant

email-assistant is an AI-based email assistant that organizes your mail automatically. It fetches any unread emails and sorts them, providing you with a full AI-powered email sorting experience. The assistant marks the emails as read but labels them as "read-by-ai" for reference. Additionally, the AI may flag emails as "flagged-as-ad" or "flagged-as-urgent" for your convenience.

## Features

- Fetches and organizes unread emails based on the labels created by the human.
- Marks emails as read (labeled as "read-by-ai")
- Labels emails as "flagged-as-ad" or "flagged-as-urgent"
- Provides AI-powered email sorting experience

## Prerequisites

Before running the project, ensure you have the following:

- Google credentials set up in a JSON file named `credentials.json` 
    - [Google's Guide](https://developers.google.com/workspace/guides/create-credentials)
- OpenAI API key stored in a file named `local.env` as follows:
  ```bash
  OPENAI_API_KEY=<YOUR-KEY>
  ```
  - [OpenAI's Guide](https://platform.openai.com/docs/api-reference)

## Setup

To set up the project, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/email-assistant.git
   cd email-assistant
   ```

2. Install the dependencies using Poetry:

   ```bash
   poetry install
   ```

## Usage

1. Define your preferences in the `human_preferences.json` file. Here is an example:

   ```json
   {
       "my_labels": [
           "personal", "banking", "payment-info", "job-application", "automated-notifications", 
           "promotions", "social", "urgent-action-required"
       ],
       "user_id": "me",
       "ai_read_labels": ["INBOX", "UNREAD"],
       "credentials_json": "my-gmail-bot-391322-d71aae822aac.json"
   }
   ```

2. Run the email assistant:

   ```bash
   poetry run python app.py
   ```

   The assistant will fetch unread emails, sort them, apply labels to your mail and store the decisions made by the AI in the `__history__` folder.

## Folder Structure

The project has the following folder structure:

- `__history__/`: Contains the decisions made by the AI and the data fed to the assistant.
  - `[YYYYMMddhhmmss]/batch_ai_decisions.json`: Stores AI decisions made during batch processing.
  - `[YYYYMMddhhmmss]/batch_process_mails.json`: Stores data fed to the assistant during batch processing.
- `logic/`: Contains the Python code that can be customized according to your preferences.
- `credentials.json`: Stores Google credentials.
- `local.env`: Stores the OpenAI API key.

## Poetry Guide

This project uses Poetry for dependency management. Poetry simplifies the management of package dependencies and provides an isolated environment for your project.

To add a new dependency, use the following command:

```bash
poetry add <package-name>
```

To run a command within the Poetry environment, prefix it with `poetry run`. For example:

```bash
poetry run python app.py
```

For more information on how to use Poetry, refer to the official documentation: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
