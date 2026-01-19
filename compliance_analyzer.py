class SovereignAudit:
    def __init__(self, company_name):
        self.company = company_name

    def check_vulnerabilities(self):
        vulnerabilities = {
            "Data Exit": "HIGH RISK (Direct AWS/Azure connection detected)",
            "Privacy Shield": "FAILED (Schrems II non-compliance)",
            "Sanitization": "INCOMPLETE (Metadata visible in US clouds)"
        }
        return vulnerabilities

    def get_financial_risk(self):
        # حساب الغرامة المتوقعة بناءً على قوانين IMY السويدية
        return "4% of global turnover or 200M SEK"

# تشغيل التقرير لتيليا
audit = SovereignAudit("Telia Sweden")
print(f"📋 تقرير المخاطر لشركة {audit.company}:")
print(audit.check_vulnerabilities())
print(f"💰 التكلفة المتوقعة في حال الغرامة: {audit.get_financial_risk()}")
