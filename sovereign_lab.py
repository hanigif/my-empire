import requests
import os
import datetime

class GitHubMonitor:
    def __init__(self):
        self.repo_owner = os.environ.get("GITHUB_OWNER")
        self.repo_name = os.environ.get("GITHUB_REPO")
        self.access_token = os.environ.get("GITHUB_TOKEN")
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"

    def get_latest_activity(self):
        # التحقق من وجود المتغيرات أولاً
        if not all([self.repo_owner, self.repo_name, self.access_token]):
            return "نقص في إعدادات البيئة (Owner/Repo/Token) في Render."
            
        url = f"{self.base_url}/commits"
        # تعديل بسيط في شكل الهيدر لضمان القبول
        headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    latest = commits[0]
                    msg = latest['commit']['message']
                    auth = latest['commit']['author']['name']
                    return f"آخر تعديل: {msg} بواسطة {auth}"
            elif response.status_code == 401:
                return "خطأ 401: التوكن غير صالح أو انتهت صلاحيته."
            elif response.status_code == 404:
                return f"خطأ 404: لم يتم العثور على المستودع {self.repo_name} تحت اسم {self.repo_owner}."
            return f"خطأ غير معروف: {response.status_code}"
        except Exception as e:
            return f"عطل تقني في المراقبة: {str(e)}"

def run_lab_test():
    monitor = GitHubMonitor()
    result = monitor.get_latest_activity()
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detail": result
    }
