import requests
import re
import pyotp
import time

class TeliaSovereignShield:
    def __init__(self, core_url):
        self.core_api = f"{core_url}/api/v1/protect"
        # يجب أن يكون هذا السر مطابقاً تماماً لما هو موجود في app.py
        self.totp = pyotp.TOTP("JBSWY3DPEHPK3PXP", interval=1)

    def local_sanitize(self, raw_text):
        """تطهير أولي قبل الإرسال"""
        raw_text = re.sub(r'\d{8}-\d{4}', '[CONFIDENTIAL_ID]', raw_text)
        raw_text = re.sub(r'(\+46|0)7\d{8}', '[PHONE_LOCKED]', raw_text)
        return raw_text

    def secure_transmission(self, data):
        clean_data = self.local_sanitize(data)
        
        # توليد كود الأمان لهذه الثانية تحديداً
        dynamic_token = self.totp.now()
        
        headers = {
            "X-Sovereign-Token": dynamic_token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.core_api, json={"payload": clean_data}, headers=headers)
            if response.status_code == 200:
                return response.json().get("data")
            elif response.status_code == 401:
                return "❌ ACCESS DENIED: Security Token Mismatch (Check Server Time)"
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Critical Failure: {str(e)}"

# --- تجربة حية لـ Telia ---
if __name__ == "__main__":
    shield = TeliaSovereignShield("https://my-empire.onrender.com")
    
    telia_logs = [
        "User: Anna Berg, PersonalID: 19850512-4432, Call to: 0708123456",
        "Tower Location: Stockholm_Kista, Gateway_ID: TK-99"
    ]

    print(f"🔐 جاري تفعيل المصافحة الرقمية المتغيرة (TOTP)...")
    for log in telia_logs:
        secured_result = shield.secure_transmission(log)
        print(f"\n[RAW]: {log}")
        print(f"[SECURED]: {secured_result}")
        # انتظر ثانية واحدة لتغيير الكود في المرة القادمة
        time.sleep(1.1)
