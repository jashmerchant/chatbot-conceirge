import json
import boto3
import datetime


def lambda_handler(event, context):
    message = event['messages']
    bot_response_message = "Please Try again!"

    if message is not None or len(message) > 0:
        data = message[0]['unstructured']['text']
        client = boto3.client('lex-runtime')
        bot_response = client.post_text(
            botName='ChatBot', botAlias='LexAlias', userId='text', inputText=data)

        bot_response_message = bot_response['message']

    response = {
        'messages': [
            {
                "type": "unstructured",
                "unstructured": {
                    "id": "1",
                    "text": bot_response_message,
                    "timestamp": "string"
                }
            }
        ]
    }

    return response
