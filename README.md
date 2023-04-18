# **aws-cust-cognit**

### Description

- AWS Cognito custom attriubutes in user pool exploitation tool

If you're using Amazon Cognito to manage user authentication in your application, you should be aware of the permissions users have by default when issued an access token. These could be abused to overwrite user custom attributes, leading to privilege escalation within the application.


**Setup**

`git clone https://github.com/UN1QUELY/aws-cust-cognit`

`pip install -r requirements.txt`

**Usage**

`python --access_token <access_token> --aws-region <aws_region>`

