"""
مثال على stream للمعاملات الجديدة مع القديمة (from_now=False)
"""
import asyncio
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()
    secret_key = 'SBKNMEIHTHOVSVV7GLWDPC5DACK7GO3CDUABKMKFYBJA4TARLLFT7EC4'
    public_key = client.get_public_key_from_secret(secret_key)

    # دالة لمعالجة كل معاملة (قديمة وجديدة)
    async def handle_transaction(transaction):
        if transaction.get('isHistoryComplete'):
            print("✅", transaction['message'])
        else:
            status = "📜 تاريخية" if transaction.get('isHistorical') else "🆕 جديدة"
            print(f"{status} - معاملة:", {
                'id': transaction.get('id'),
                'amount': transaction.get('amount'),
                'memo': transaction.get('memo'),
                'type': transaction.get('type'),
                'created_at': transaction.get('created_at')
            })

    print("بدء مراقبة المعاملات الجديدة مع القديمة (from_now=False)...")
    stream_id = await client.setup_transaction_stream(
        public_key,
        handle_transaction,
        from_now=False,  # المعاملات الجديدة مع القديمة
        check_interval=20  # فحص كل 20 ثانية
    )

    # انتظار لمدة 5 دقائق
    await asyncio.sleep(300)
    stopped = client.stop_transaction_stream(stream_id)
    print("تم إيقاف المراقبة؟", stopped)

if __name__ == "__main__":
    asyncio.run(main())
