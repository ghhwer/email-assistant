import json
import openai
import re 
make_ai_email_text = lambda sender, recipient, subject, contains_html, normalized_body  : f"""
I need you to help me sort/organize my mail, here is an email:
[START OF EMAIL]
[SENDER]={sender}
[RECIPIENT]={recipient}
[SUBJECT]={subject}
[CONTAINS HTML]={contains_html}
[START BODY]
{normalized_body}
[END OF BODY]
[END OF EMAIL]
"""

instruction = """To organize the email, please provide an explanation of why the email should be moved to the new folder.
After that provide a text that with the following format
(1) "The name of the new folder" (Replace with one of the available folders: {})
(2) "If the email is an advertisement" (Replace with "yes" or "no")
(3) "If the email is urgent" (Replace with "yes" or "no")
"""

def transform_string(input_string):
    # Remove (N) if present using regex
    input_string = re.sub(r"\(\d+\)", "", input_string).strip()
    # Remove any non-alphanumeric characters but keep - and _ and whitespace
    input_string = re.sub(r'[^\w\s-]', '', input_string)
    # Convert to lowercase
    input_string = input_string.lower().replace('"', '')
    return input_string

def ai_organize_email(id, sender, recipient, subject, contains_html, normalized_body, available_folders, model):
    if model.startswith('gpt-'):
        return ai_organize_email_gpts(id, sender, recipient, subject, contains_html, normalized_body, available_folders, model)
    else:
        return ai_organize_email_llama(id, sender, recipient, subject, contains_html, normalized_body, available_folders, model)

def ai_organize_email_llama(id, sender, recipient, subject, contains_html, normalized_body, available_folders, model):
    # Make the prompt
    available_folders_text = ", ".join(available_folders)
    text = make_ai_email_text(sender, recipient, subject, contains_html, normalized_body)
    text += '\n'+instruction.format(available_folders_text)
    
    # Create a single shot example of the conversation to stabilize the response 
    text_first_shot = make_ai_email_text('example@example.com', recipient, "an example", True, "this is an example email")
    text_first_shot_available_folders_text = ", ".join(["folder1", "folder2", "folder3"])
    text_first_shot += '\n'+instruction.format(text_first_shot_available_folders_text)
    response_first_shot = "Even though this is an example, I will provide a response to show you how to do it. The email should be moved to the folder 'folder1' because it is an advertisement and it is urgent."
    response_first_shot = f"{response_first_shot}\n(1) folder1\n(2) yes\n(3) yes"

    # Use openai api to get the response (This will work if the user has an openai endpoint and the model is properly configured)
    chat_completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an email sorting assistant. Please follow the instructions below to sort the email."},
            {"role": "user", "content": text_first_shot},
            {"role": "assistant", "content": response_first_shot},
            {"role": "user", "content": text}
        ],
        max_tokens=150,
        temperature=0.3,
    )
    # Extract the response
    response = chat_completion.choices[0].message.content
    assistent_notes = '\n'.join(response.split('\n')[:-3]).strip()
    response = response.split('\n')[-3:]
    folder, is_advertisement, is_urgent = map(transform_string, response)
    
    # Check for stable response
    if folder in available_folders and is_advertisement in ["yes", "no"] and is_urgent in ["yes", "no"]:
        return {
            'decision': {
                    'email_id':id, 
                    'new_folder':folder, 
                    'is_ad': is_advertisement == "yes",
                    'is_urgent':is_urgent == "yes",
                    'assistent_notes':assistent_notes
            }
        }
    else:
        raise ValueError(f'The assistant did not provide a valid response for the id: {id}')

def organize_email(email_id, new_folder, is_ad, is_urgent, assistent_notes):
    return {
        'email_id':email_id, 
        'new_folder':new_folder, 
        'is_ad':is_ad, 
        'is_urgent':is_urgent, 
        'assistent_notes':assistent_notes
    }

def ai_organize_email_gpts(id, sender, recipient, subject, contains_html, normalized_body, available_folders, model):
    # Step 1: make the prompt
    prompt = make_ai_email_text(sender, recipient, subject, contains_html, normalized_body)
    # Step 2: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": prompt}]
    # Register function
    functions = [
        {
            "name": "organize_email",
            "description": "Email organization tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_folder": {
                        "type": "string", "enum": available_folders
                    },
                    "is_ad": {
                        "type": "boolean",
                        "description": "Defines if this is an advertisement",
                    },
                    "is_urgent": {
                        "type": "boolean",
                        "description": "Defines if this is urgent",
                    },
                    "assistent_notes": {
                        "type": "string",
                        "description": "notes from the assistant, describe in a few words why the action was taken",
                    }
                },
                "required": ["id", "new_folder", "is_ad", "is_urgent", "assistent_notes"],
            },
        }
    ]
    available_functions = {"organize_email": organize_email,} 
    # Delegate task to AI
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call={"name": "organize_email"},
    )
    response_message = response["choices"][0]["message"]
    # Step 3: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3.1: call the function
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        if function_args.get('new_folder') in available_folders:
            function_response = fuction_to_call(
                email_id=id, 
                new_folder=function_args.get('new_folder'),
                is_ad=function_args.get('is_ad'), 
                is_urgent=function_args.get('is_urgent'), 
                assistent_notes=function_args.get('assistent_notes')
            )
            # Return the desision
            return {'decision': function_response, 'openai_usage': response.get('usage', {})}
        else:
            raise ValueError('The assistant placed the email on a nonexistent folder')
    else:
        raise ValueError('The assistent did not call a function')
