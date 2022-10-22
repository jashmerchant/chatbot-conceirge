import logging
import boto3
import json
import requests
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from requests_aws4auth import AWS4Auth
import random
import decimal

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(0, len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


def lambda_handler(event, context):
    # Create SQS client
    YOUR_ACCESS_KEY = ""
    YOUR_SECRET_KEY = ""
    region = "us-east-1"
    service = 'es'

    sqs = boto3.client('sqs')

    try:
        response = sqs.receive_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/393391166255/Q1',
            AttributeNames=[
                'Cuisine', 'Location', 'Time', 'NumberOfPeople', 'PhoneNumber'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        # print(response['Messages'][0]['MessageAttributes'])
        messages = response['Messages'] if 'Messages' in response.keys() else [
        ]

        for message in messages:
            receiptHandle = message['ReceiptHandle']
            sqs.delete_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/393391166255/Q1', ReceiptHandle=receiptHandle)
            msg_attributes = message['MessageAttributes']
            cuisine = msg_attributes['Cuisine']['StringValue']
            phNo = msg_attributes['PhoneNumber']['StringValue']

        sms_message = None

        awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, region, service)
        # the Amazon ES domain, with https://
        host = 'https://search-dining-d3yn3ctxj3hwod2n5lmo3axbgy.us-east-1.es.amazonaws.com'
        index = 'restaurants'
        url = host + '/' + index + '/_search?q='+str(cuisine)

        headers = {"Content-Type": "application/json"}
        r = requests.get(url, auth=awsauth, headers=headers)
        response = r.text
        data = json.loads(response)
        randomSelect = random.randint(0, len(data['hits']['hits'])-3)
        # business_id = int(data['hits']['hits'][randomSelect]['_id'])
        # print(f"Data: {data}, B_ID: {business_id}")

        def query_data(dynamodb=None):
            if not dynamodb:
                dynamodb = boto3.resource('dynamodb',  aws_access_key_id=YOUR_ACCESS_KEY,
                                          aws_secret_access_key=YOUR_SECRET_KEY, region_name=region)

            return(dynamodb.Table('yelp-restaurant'))

        restaurant_recommendation = ''

        for i in range(3):
            business_id = int(data['hits']['hits'][randomSelect]['_id'])
            table = query_data()
            # response = table.query(KeyConditionExpression=Key('serial_no').eq(business_id))
            response = table.get_item(
                Key={'serial_no': business_id}, TableName='yelp-restaurant')
            response = replace_decimals(response)
            name = response['Item']['name']
            address = response['Item']['address']
            ratings = response['Item']['rating']
            no_of_reviews = response['Item']['review_count']
            # message = "{}. {} located at {}, which has {} reviews and a rating of {} on Yelp.\n".format(
            #     1, name, address, no_of_reviews, ratings)
            message = f"{i+1}. {name} is located at {address} has {no_of_reviews} reviews and {ratings} rating on Yelp.\n"
            restaurant_recommendation = restaurant_recommendation+message
            randomSelect += 1

        sms_message = f'Hello, here are my suggestions for you {restaurant_recommendation} \n. Enjoy your meal! :)'
        print(sms_message)
        subject = 'Dining Conceirge'
        client = boto3.client("ses")
        body = sms_message
        message = {"Subject": {"Data": subject},
                   "Body": {"Html": {"Data": body}}}
        response = client.send_email(Source="merchantjash@gmail.com", Destination={
                                     "ToAddresses": ["merchantjash@gmail.com"]}, Message=message)
        print(response)

        # print(f"Text: {sms_message}")

        # phone_number = '+1'+phNo
        # # sns_client = boto3.client('sns', 'us-east-1')
        # sns = boto3.client("sns", region_name='us-east-1',
        #                    aws_access_key_id=YOUR_ACCESS_KEY,
        #                    aws_secret_access_key=YOUR_SECRET_KEY)

        # response = sns.publish(PhoneNumber=phone_number, Message=sms_message)
        # print(f"Response: {response}")

    except KeyError:
        print('Queue is empty')
