"""
مثال على استخدام stream لمتابعة المعاملات الجديدة لحساب معين
"""
import asyncio
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()
    secret_key = 'SBKNMEIHTHOVSVV7GLWDPC5DACK7GO3CDUABKMKFYBJA4TARLLFT7EC4'
    public_key = client.get_public_key_from_secret(secret_key)  # الحصول على المفتاح العام للحساب

    # دالة لمعالجة كل معاملة جديدة
    async def handle_transaction(transaction):
        print("معاملة جديدة وصلت:", transaction)

    print("بدء مراقبة المعاملات الجديدة...")
    stream_id = await client.setup_transaction_stream(
        public_key,
        handle_transaction,
        from_now=False,  # المعاملات الجديدة مع القديمة
        check_interval=10  # فحص كل 10 ثواني
    )

    # انتظر لمدة 1200 ثانية (20 دقيقة) ثم أوقف المراقبة
    await asyncio.sleep(1200)
    stopped = client.stop_transaction_stream(stream_id)
    print("تم إيقاف المراقبة؟", stopped)

if __name__ == "__main__":
    asyncio.run(main())
