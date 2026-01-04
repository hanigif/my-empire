import requests
import os
import datetime

class GitHubMonitor:
    def __init__(self):
        # جلب البيانات من Render Environment Variables التي أضفتها أنت
        self.repo_owner = os.environ.get("GITHUB_OWNER")
        self.repo_name = os.environ.get("GITHUB_REPO")
        self.access_token = os.environ.get("GITHUB_TOKEN")
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"

    def get_latest_activity(self):
        url = f"{self.base_url}/commits"
        headers = {"Authorization": f"token {self.access_token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    latest = commits[0]
                    # سيعود التقرير بالوقت والرسالة وصاحب التعديل
                    return f"Commit: {latest['commit']['message']} | Author: {latest['commit']['author']['name']}"
            return "No recent commits found or access denied."
        except Exception as e:
            return f"Monitor Error: {str(e)}"

def run_lab_test():
    monitor = GitHubMonitor()
    result = monitor.get_latest_activity()
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detail": result
    }
