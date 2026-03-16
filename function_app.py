import azure.functions as func
import urllib.request
import json
import os
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # 1. Get the event type from header
        event = req.headers.get('X-GitHub-Event', 'unknown')
        payload = req.get_json()
        
        # 2. Handle the 'ping' event separately
        if event == "ping":
            return func.HttpResponse("Ping received!", status_code=200)

        # 3. Handle the 'push' event
        repo_name = payload.get('repository', {}).get('name', 'Unknown')
        msg = {"text": f"🔥 *Sentinel Alert*: Push detected in `{repo_name}`"}
        
        # 4. Post to Slack
        slack_url = os.environ.get('SLACK_WEBHOOK_URL')
        data = json.dumps(msg).encode('utf-8')
        req_slack = urllib.request.Request(slack_url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req_slack)
        
        return func.HttpResponse("Slack Notified", status_code=200)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Runtime Error: {str(e)}", status_code=500)
