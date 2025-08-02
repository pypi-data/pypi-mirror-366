"""
مثال عملي لاستخدام SofizPayClient
"""
import asyncio
from sofizpay.client import SofizPayClient

async def main():
    # بيانات تجريبية (استبدلها ببيانات حقيقية)
    source_secret = "SBKNMEIHTHOVSVV7GLWDPC5DACK7GO3CDUABKMKFYBJA4TARLLFT7EC4"  # المفتاح السري للحساب المرسل
    destination_public_key = "GB6MXBJGI4A7DJKBKUUTMLEUPPG3YWH2IBZQUHXZQJPLUVJOTAKCRDVC"  # المفتاح العام للحساب المستقبل

    client = SofizPayClient()

    # إرسال دفعة DZT
    try:
        payment_result = await client.send_payment(
            source_secret=source_secret,
            destination_public_key=destination_public_key,
            amount="10.5",
            memo="اختبار دفع"
        )
        print("نتيجة الدفع:", payment_result)
    except Exception as e:
        print("خطأ أثناء الدفع:", e)

    # التحقق من الرصيد
    try:
        balance = await client.get_balance(destination_public_key)
        print("الرصيد الحالي:", balance)
    except Exception as e:
        print("خطأ أثناء جلب الرصيد:", e)

    # جلب المعاملات
    try:
        transactions = await client.get_transactions(destination_public_key, limit=5)
        print("آخر المعاملات:", transactions)
    except Exception as e:
        print("خطأ أثناء جلب المعاملات:", e)

    # التحقق من التوقيع (مثال)
    verification_data = {
        "message": "Hello, SofizPay!",
        "signature_url_safe": "SIGNATURE_URL_SAFE_HERE"
    }
    is_valid = client.verify_sofizpay_signature(verification_data)
    print("هل التوقيع صحيح؟", is_valid)

if __name__ == "__main__":
    asyncio.run(main())
