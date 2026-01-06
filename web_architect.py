import os
import shutil

class WebArchitect:
    def __init__(self):
        self.template_dir = "templates"
        self.ensure_directory()

    def ensure_directory(self):
        """التأكد من وجود المجلد وحل أي تعارض مع ملفات قديمة"""
        if os.path.exists(self.template_dir):
            if not os.path.isdir(self.template_dir):
                # إذا وجد ملفاً بنفس الاسم، يقوم بحذفه لإنشاء المجلد
                os.remove(self.template_dir)
                os.makedirs(self.template_dir)
        else:
            os.makedirs(self.template_dir)

    def update_dashboard(self, version_name):
        """إنشاء أو تحديث واجهة لوحة التحكم للعملاء"""
        self.ensure_directory() # التأكد من المجلد قبل الكتابة
        
        html_content = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sovereign Guard 2026 | بوابة المشافي</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; color: #1c1e21; margin: 0; padding: 0; }
                .navbar { background: #003366; color: white; padding: 1.2rem; text-align: center; font-size: 1.8rem; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .container { width: 90%; max-width: 800px; margin: 3rem auto; background: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
                .status-card { border-right: 6px solid #2ecc71; background: #fafffb; padding: 1.5rem; margin-bottom: 2rem; border-radius: 8px; }
                .btn { background: #0056b3; color: white; padding: 1rem 2rem; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; width: 100%; transition: 0.3s; }
                .btn:hover { background: #004494; }
                .footer { text-align: center; padding: 2rem; font-size: 0.9rem; color: #606770; }
                input[type="file"] { margin: 1.5rem 0; padding: 1rem; border: 1px dashed #ccc; width: 100%; box-sizing: border-box; }
            </style>
        </head>
        <body>
            <div class="navbar">Sovereign Guard 2026</div>
            <div class="container">
                <h2>بوابة الامتثال الصحي - السويد</h2>
                <div class="status-card">
                    <strong>الحالة القانونية:</strong> ✅ النظام متوافق مع تحديثات Socialstyrelsen لعام 2026
                </div>
                <p>عزيزي المشترك، يرجى رفع ملفات سجلات البيانات (Data Logs) لإجراء الفحص السيادي الفوري للتأكد من خلوها من ثغرات الخصوصية.</p>
                <input type="file" id="data_file">
                <button class="btn">تحليل الامتثال الفوري</button>
            </div>
            <div class="footer">نظام التشغيل السيادي - تم التطوير لصالح مؤسستك © 2026</div>
        </body>
        </html>
        """
        file_path = os.path.join(self.template_dir, "dashboard.html")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return f"Success: {version_name}"
        except Exception as e:
            return f"Error: {str(e)}"
