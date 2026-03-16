import azure.functions as func
import json

app = func.FunctionApp()

# This function just takes the GitHub data and "saves" it to the queue
@app.route(route="GithubWebhook", auth_level=func.AuthLevel.FUNCTION)
@app.queue_output(arg_name="msg", queue_name="github-notifications", connection="AzureWebJobsStorage")
def GithubWebhook(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    payload = req.get_json()
    
    # Push the raw JSON into the queue
    msg.set(json.dumps(payload))
    
    return func.HttpResponse("Accepted into Queue", status_code=202)

import os
import urllib.request
import logging

# This function triggers whenever a message lands in the queue
@app.queue_trigger(arg_name="azqueue", queue_name="github-notifications", connection="AzureWebJobsStorage")
def QueueToSlack(azqueue: func.QueueMessage):
    # 1. Get the data from the queue
    payload = json.loads(azqueue.get_body().decode('utf-8'))
    
    # 2. Extract info
    repo = payload.get('repository', {}).get('name', 'Unknown')
    slack_url = os.environ.get('SLACK_WEBHOOK_URL')
    
    # 3. Try to send to Slack
    msg = {"text": f"📢 *Queue Sentinel*: Change detected in `{repo}`"}
    data = json.dumps(msg).encode('utf-8')
    
    req = urllib.request.Request(slack_url, data=data, headers={'Content-Type': 'application/json'})
    
    # If this line fails (e.g. Slack is down), the function throws an error.
    # Azure will then RETRY this message automatically up to 5 times!
    urllib.request.urlopen(req)
