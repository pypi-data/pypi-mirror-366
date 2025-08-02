"""
مثال على stream للمعاملات الجديدة فقط (from_now=True)
"""
import asyncio
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()
    secret_key = 'SBKNMEIHTHOVSVV7GLWDPC5DACK7GO3CDUABKMKFYBJA4TARLLFT7EC4'
    public_key = client.get_public_key_from_secret(secret_key)

    # دالة لمعالجة كل معاملة جديدة
    async def handle_transaction(transaction):
        if transaction.get('isHistoryComplete'):
            print(transaction['message'])
        else:
            print("معاملة جديدة فقط:", {
                'id': transaction.get('id'),
                'amount': transaction.get('amount'),
                'memo': transaction.get('memo'),
                'type': transaction.get('type'),
                'isHistorical': transaction.get('isHistorical', False)
            })

    print("بدء مراقبة المعاملات الجديدة فقط (from_now=True)...")
    stream_id = await client.setup_transaction_stream(
        public_key,
        handle_transaction,
        from_now=True,  # المعاملات الجديدة فقط
        check_interval=15  # فحص كل 15 ثانية
    )

    # انتظار لمدة 5 دقائق
    await asyncio.sleep(300)
    stopped = client.stop_transaction_stream(stream_id)
    print("تم إيقاف المراقبة؟", stopped)

if __name__ == "__main__":
    asyncio.run(main())
