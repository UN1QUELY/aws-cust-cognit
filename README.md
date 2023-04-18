# **aws-cust-cognit**

### Description

- AWS Cognito custom attriubutes in user pool exploitation tool

If you're using Amazon Cognito to manage user authentication in your application, you should be aware of the permissions users have by default when issued an access token. These could be abused to overwrite user custom attributes, leading to privilege escalation within the application.


**Setup**

`git clone https://github.com/UN1QUELY/aws-cust-cognit`

`cd aws-cust-cognit`

`pip install -r requirements.txt`

**Usage**

`python --aws-region <aws_region> --access_token <access_token>`

**Example**

`python --aws-region us-west-1 --access_token eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY4MTgyNzY5OSwiaWF0IjoxNjgxODI3Njk5fQ.FZuoFFpjUS48zlO4sje3Y84-phcccVtgS9ymKgGFwrc`

