from datetime import datetime, time, timezone
from pymongo import ASCENDING, DESCENDING
from pydantic import ValidationError
from bson import ObjectId

from .models import AIReport
from . import DB_NAME
from db2_hj3415.common.db_ops import get_collection
from db2_hj3415.common import connection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

async def save(col: str, data: AIReport) -> dict:
    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, col)
    await collection.create_index([("날짜", ASCENDING), ("ticker", ASCENDING)], unique=True)

    if not data.날짜:
        data.날짜 = datetime.now(timezone.utc)

    # 날짜 기준 중복 확인
    today = data.날짜.date()

    existing = await collection.find_one({
        "ticker": data.ticker,
        "날짜": {
            "$gte": datetime.combine(today, time.min).replace(tzinfo=timezone.utc),
            "$lt": datetime.combine(today, time.max).replace(tzinfo=timezone.utc)
        }
    })
    mylogger.debug(f"이미 저장된 오늘 날짜 데이터가 있나?: {existing}")

    if existing:
        return {"status": "skipped", "reason": "already_saved_today"}

    # datetime 그대로 유지하기 위해 mode='python' 사용
    doc = data.model_dump(by_alias=True, mode='python', exclude_none=False)

    # ObjectId가 존재하면 업데이트, 아니면 삽입
    if '_id' in doc:
        if doc['_id'] is None:
            doc.pop('_id')  # None이면 제거하여 MongoDB에서 자동 생성되게 함
        else:
            doc['_id'] = ObjectId(doc['_id']) if isinstance(doc['_id'], str) else doc['_id']
            await collection.replace_one({'_id': doc['_id']}, doc, upsert=True)
            return {"status": "updated", "_id": str(doc['_id'])}

    result = await collection.insert_one(doc)
    data.id = str(result.inserted_id)
    return {"status": "inserted", "_id": data.id}


async def get_latest(col: str, ticker: str) -> AIReport | None:
    if col not in ['by_nfs', 'by_price']:
        raise ValueError(f"지원되지 않는 컬렉션: {col}")

    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, col)
    doc = await collection.find_one(
        {"ticker": ticker},
        sort=[("날짜", DESCENDING)]
    )

    if not doc:
        mylogger.warning("데이터 없음: %s (%s)", col, ticker)
        return None

    doc["_id"] = str(doc["_id"])  # 필요 시만

    try:
        return AIReport(**doc)  # type: ignore[arg-type]
    except ValidationError as e:
        mylogger.error("Pydantic 검증 실패 (%s, %s): %s", col, ticker, e)
        return None