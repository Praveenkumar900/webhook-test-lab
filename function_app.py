import azure.functions as func
import urllib.request
import json
import os
import logging

# This is the "app" instance Azure is looking for!
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="HttpTrigger1")
def HttpTrigger1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        # 1. Handle GitHub Ping vs Push
        event = req.headers.get('X-GitHub-Event', 'unknown')
        payload = req.get_json()
        
        if event == "ping":
            return func.HttpResponse("Ping received!", status_code=200)

        # 2. Extract info for Slack
        repo_name = payload.get('repository', {}).get('name', 'Unknown Repo')
        sender = payload.get('sender', {}).get('login', 'Someone')
        
        # 3. Send to Slack using environment variable
        # We are adding emoji and bolding for a "Senior" look
        repo_url = payload.get('repository', {}).get('html_url', '#')
        msg = {
            "text": f"🚨 *DevOps Alert* 🚨\n*User:* `{sender}`\n*Action:* Pushed to repo\n*Repository:* <{repo_url}|{repo_name}>\n---\n_Status: Automated via Azure Functions_"
        }
        data = json.dumps(msg).encode('utf-8')
        req_slack = urllib.request.Request(slack_url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req_slack)
        
        return func.HttpResponse("Success", status_code=200)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Runtime Error: {str(e)}", status_code=500)
