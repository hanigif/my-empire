import requests
import re
import json

class TeliaSovereignShield:
    def __init__(self, core_url):
        # تأكد من وضع رابط الـ Render الخاص بك هنا
        self.core_api = f"{core_url}/api/v1/protect"

    def local_sanitize(self, raw_text):
        """الطبقة الأولى: التطهير المحلي الفوري قبل الخروج للسحابة"""
        # إخفاء الهويات السويدية (Personnummer)
        raw_text = re.sub(r'\d{8}-\d{4}', '[CONFIDENTIAL_ID]', raw_text)
        # إخفاء أرقام الهواتف
        raw_text = re.sub(r'(\+46|0)7\d{8}', '[PHONE_LOCKED]', raw_text)
        return raw_text

    def secure_transmission(self, data):
        clean_data = self.local_sanitize(data)
        try:
            response = requests.post(self.core_api, json={"payload": clean_data})
            if response.status_code == 200:
                return response.json().get("data")
            return "Error: Encryption Core Unreachable"
        except Exception as e:
            return f"Critical Failure: {str(e)}"

# --- تجربة حية لـ Telia ---
if __name__ == "__main__":
    shield = TeliaSovereignShield("https://my-empire.onrender.com") # رابط سيرفرك
    
    # عينة بيانات حقيقية لتيليا (سجلات مكالمات ومواقع)
    telia_logs = [
        "User: Anna Berg, PersonalID: 19850512-4432, Call to: 0708123456, Tower: GBG_South",
        "Log: 192.168.10.5, Device: Nokia_Gateway, Location: Stockholm_Kista"
    ]

    print("🚀 بدء المعالجة السيادية لشركة تيليا...")
    for log in telia_logs:
        secured_result = shield.secure_transmission(log)
        print(f"\n[RAW]: {log}")
        print(f"[SECURED]: {secured_result}")
