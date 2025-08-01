from typing import Iterable
import redis

from redis.asyncio import Redis
from .schemas import KeyWithTTL
from .common.connection import get_redis_client_async

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__)


BATCH_SIZE = 1000  # 상황에 맞게 조절

async def get_redis_keys_with_ttl(prefix: str = "") -> list[KeyWithTTL]:
    """
    Redis 키(prefix 매칭)와 TTL을 비동기/배치 파이프라인으로 조회.

    - 클라이언트는 decode_responses=True 로 문자열 키를 받는다고 가정.
    - TTL 의미:
        * -1: 만료 없음
        * -2: 키 없음 (SCAN 이후 삭제된 경우 가능)
    """
    r: Redis = get_redis_client_async()  # decode_responses=True 권장
    pattern = f"{prefix}*" if prefix else "*"

    results: list[KeyWithTTL] = []
    batch: list[str] = []

    # 1) 키 스캔 (count 힌트로 왕복 최적화)
    async for k in r.scan_iter(match=pattern, count=1000):
        batch.append(k)
        if len(batch) >= BATCH_SIZE:
            # 2) 배치 파이프라인으로 TTL 조회
            ttls = await _fetch_ttls_batch(r, batch)
            results.extend(KeyWithTTL(key=key, ttl=int(ttl)) for key, ttl in zip(batch, ttls))
            batch.clear()

    # 3) 남은 키 처리
    if batch:
        ttls = await _fetch_ttls_batch(r, batch)
        results.extend(KeyWithTTL(key=key, ttl=int(ttl)) for key, ttl in zip(batch, ttls))

    # 정렬(키 기준)
    results.sort(key=lambda x: x.key)
    return results


async def _fetch_ttls_batch(r: Redis, keys: Iterable[str]) -> list[int]:
    """주어진 키들에 대해 TTL을 파이프라인으로 조회 (transaction=False)."""
    async with r.pipeline(transaction=False) as pipe:
        for k in keys:
            pipe.ttl(k) # IDE경고 무시해도 됨
        return await pipe.execute()


async def delete_key(key: str) -> bool:
    """
    주어진 Redis 키를 삭제합니다.

    Returns
    -------
    bool
        True : 키가 존재해 삭제됨 (DEL 결과 1)
        False: 키가 없었음 (DEL 결과 0) 또는 Redis 오류 발생
    """
    r: Redis = get_redis_client_async()
    try:
        deleted: int = await r.delete(key)  # 1: 삭제됨, 0: 없음
        return bool(deleted)
    except (redis.ConnectionError, redis.TimeoutError, redis.RedisError) as e:
        mylogger.warning("Redis DEL 실패: key=%s, err=%s", key, e)
        return False