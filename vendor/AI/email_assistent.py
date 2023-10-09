import json
import openai

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

def organize_email(email_id, new_folder, is_ad, is_urgent, assistent_notes):
    return {
        'email_id':email_id, 
        'new_folder':new_folder, 
        'is_ad':is_ad, 
        'is_urgent':is_urgent, 
        'assistent_notes':assistent_notes
    }

def ai_organize_email(id, sender, recipient, subject, contains_html, normalized_body, available_folders, use_gpt_4=False):
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
        model="gpt-4-0613" if use_gpt_4 else "gpt-3.5-turbo-0613",
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
