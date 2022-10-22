import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

def lambda_handler(event, context):
    client = boto3.client("sqs")
    response = client.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/393391166255/Q1",
        # create variables
        # create dict out of those
        # sqs.send_message
        MessageAttributes={
                'Cuisine': {
                    'DataType': 'String',
                    'StringValue': event["currentIntent"]["slots"]["Cuisine"]
                },
                'Location': {
                    'DataType': 'String',
                    'StringValue': event["currentIntent"]["slots"]["Location"]
                },
                'PhoneNumber': {
                    'DataType': 'Number',
                    'StringValue': event["currentIntent"]["slots"]["PhoneNumber"]
                },
                'Time': {
                    'DataType': 'String',
                    'StringValue': str(event["currentIntent"]["slots"]["DiningTime"])
                },
                'NumberOfPeople': {
                    'DataType': 'Number',
                    'StringValue': str(event["currentIntent"]["slots"]["NumberofPeople"])
                }
        },
        MessageBody=('Information about the diner')
    )

    reply =  {

        "sessionAttributes": {
        "key1": "value1",
        "key2": "value2"
        },

        "dialogAction":
                        {
                            "fulfillmentState":"Fulfilled",
                            "type":"Close",
                            "message":
                                {
                                    "contentType":"PlainText",
                                    "content": "Hi, we have received your inputs and will be back with suggestions!"
                                }
                        }
    }

    return reply