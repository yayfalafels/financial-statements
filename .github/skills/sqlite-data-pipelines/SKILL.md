---
name: sqlite-data-pipelines
description: Worked code patterns for SCD Type 1, deterministic hashing, idempotent ingest, staging isolation, and transaction recovery.
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Overview

This skill provides reusable code patterns for data pipelines that operate on SQLite. The patterns emphasize idempotence (same input → same output, no side effects on rerun), determinism (reproducible results), and isolation (staging data separate from production). Each pattern includes error recovery strategy and transaction boundary guidance.

## When to Use This Skill

- Designing SCD Type 1 dimension table updates.
- Implementing deterministic UID hashing for transaction lineage.
- Building idempotent ingest pipelines that safely restart.
- Staging external data before production load.
- Isolating failed transactions and enabling safe resume.
- Designing session and transaction management for data operations.

## SCD Type 1 Update Pattern

**Use case**: Reference dimensions (accounts, categories) that change infrequently but need updates without history.

**Idempotency guarantee**: Running the same update with unchanged source data produces zero new rows or modifications.

**Pattern overview**:
1. Create staging table with same schema as target.
2. Load new dimension records into staging.
3. Compute update delta (what changed).
4. Apply updates to production table atomically.
5. Commit transaction; on failure, rollback leaves production untouched.

**Code example**:

```python
from sqlalchemy import create_engine, text, Column, String, Integer
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def scd_type_1_update(
    target_table: str,
    source_records: list[dict],
    key_column: str,
    engine
) -> dict:
    """
    Update dimension table with SCD Type 1 pattern.
    
    Args:
        target_table: production table name (e.g., 'account_dim')
        source_records: list of dicts with new/updated values
        key_column: natural key column name (e.g., 'account_id')
        engine: SQLAlchemy engine
    
    Returns:
        dict with counts: {inserted: int, updated: int, unchanged: int}
    
    Idempotency: same source_records on rerun = zero modifications
    Error recovery: on failure, production table unchanged
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Phase 1: create staging table
        staging_name = f"staging_{target_table}_{datetime.now().timestamp()}"
        staging_sql = f"""
            CREATE TEMP TABLE {staging_name} AS
            SELECT * FROM {target_table} LIMIT 0
        """
        session.execute(text(staging_sql))
        
        # Phase 2: load new data into staging
        for record in source_records:
            stmt = text(f"""
                INSERT INTO {staging_name} ({', '.join(record.keys())})
                VALUES ({', '.join([f':{k}' for k in record.keys()])})
            """)
            session.execute(stmt, record)
        
        # Phase 3: compute update delta
        # Find records in staging that differ from production
        delta_sql = f"""
            SELECT s.{key_column} as key, s.* FROM {staging_name} s
            LEFT JOIN {target_table} p ON s.{key_column} = p.{key_column}
            WHERE p.{key_column} IS NULL
            OR s.* != p.*
        """
        delta_result = session.execute(text(delta_sql))
        
        # Phase 4a: insert new records (not in production)
        insert_sql = f"""
            INSERT OR IGNORE INTO {target_table}
            SELECT * FROM {staging_name} s
            WHERE NOT EXISTS (
                SELECT 1 FROM {target_table} p
                WHERE p.{key_column} = s.{key_column}
            )
        """
        insert_result = session.execute(text(insert_sql))
        inserted = insert_result.rowcount
        
        # Phase 4b: update changed records
        # NOTE: SQLite UPDATE with subquery syntax
        update_sql = f"""
            UPDATE {target_table}
            SET {', '.join([f'{k} = (SELECT {k} FROM {staging_name} WHERE {key_column} = ?)' 
                           for k in source_records[0].keys() if k != key_column])}
            WHERE {key_column} IN (
                SELECT {key_column} FROM {staging_name} s
                WHERE EXISTS (
                    SELECT 1 FROM {target_table} p
                    WHERE p.{key_column} = s.{key_column}
                )
            )
        """
        update_result = session.execute(text(update_sql))
        updated = update_result.rowcount
        
        # Phase 5: atomically commit
        session.commit()
        
        unchanged = len(source_records) - inserted - updated
        logger.info(f"SCD Type 1 update complete: {inserted} inserted, {updated} updated, {unchanged} unchanged")
        
        return {
            "inserted": inserted,
            "updated": updated,
            "unchanged": unchanged
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"SCD Type 1 update failed: {e}; production table unchanged")
        raise
        
    finally:
        session.close()
```

**Idempotency verification**:
```python
def verify_scd_type_1_idempotency(target_table: str, engine):
    """
    Verify that running the same update twice produces identical results.
    Run this after initial update:
    
    1. Record production table checksum.
    2. Run update again with same source.
    3. Verify checksum unchanged.
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Compute table checksum (hash of all rows)
    checksum_sql = text(f"""
        SELECT md5(group_concat(md5(row_hash)))
        FROM (
            SELECT md5(cast({target_table}.* as text)) as row_hash
            FROM {target_table}
            ORDER BY id
        )
    """)
    
    checksum_1 = session.execute(checksum_sql).scalar()
    
    # Run update again (same source)
    scd_type_1_update(target_table, source_records, key_column, engine)
    
    checksum_2 = session.execute(checksum_sql).scalar()
    
    assert checksum_1 == checksum_2, f"Idempotency failed: checksum changed {checksum_1} -> {checksum_2}"
    logger.info("SCD Type 1 idempotency verified")
    session.close()
```

## Deterministic UID Hashing Pattern

**Use case**: Assign reproducible UIDs to transactions for lineage tracking and duplicate detection.

**Idempotency guarantee**: Same transaction input → same UID, always.

**Pattern overview**:
1. Select deterministic hash inputs (date, amount, account, direction).
2. Sort inputs canonically to ensure order-independence.
3. Hash with a stable salt and algorithm (MD5 or SHA256).
4. Verify no collisions for the scope (same account, date, amount, direction).

**Code example**:

```python
from hashlib import md5
from decimal import Decimal
from datetime import date

def compute_hb_txn_uid(
    account_id: str,
    txn_date: date,
    amount: Decimal,
    direction: str,  # "debit" or "credit"
    salt: str = "hb_txn_uid_v1"
) -> str:
    """
    Compute deterministic UID for HomeBudget transaction.
    
    Args:
        account_id: HomeBudget account ID (e.g., 'TWH DBS Multi SGD')
        txn_date: transaction date in ISO format
        amount: absolute amount (Decimal for precision)
        direction: 'debit' or 'credit'
        salt: stable salt for hash algorithm (version-locked)
    
    Returns:
        str: 32-character hex hash (MD5)
    
    Idempotency: same inputs → same UID
    Scope: same account/date/amount/direction cannot have duplicate UIDs
    """
    # Canonical string representation (order-independent)
    hash_input = f"{salt}|{account_id}|{txn_date.isoformat()}|{amount:.2f}|{direction}".lower()
    
    uid = md5(hash_input.encode()).hexdigest()
    return uid


def verify_uid_determinism(txn_records: list[dict]) -> bool:
    """
    Verify that the same transaction record always produces the same UID.
    """
    for record in txn_records:
        uid_1 = compute_hb_txn_uid(
            record["account_id"],
            record["txn_date"],
            record["amount"],
            record["direction"]
        )
        uid_2 = compute_hb_txn_uid(
            record["account_id"],
            record["txn_date"],
            record["amount"],
            record["direction"]
        )
        assert uid_1 == uid_2, f"UID not deterministic: {uid_1} != {uid_2}"
    
    logger.info("UID determinism verified for all records")
    return True


def detect_uid_collisions(txn_records: list[dict]) -> list[tuple]:
    """
    Detect if two different transactions produce the same UID.
    This indicates a hash collision or insufficient input differentiation.
    """
    uid_map = {}
    collisions = []
    
    for i, record in enumerate(txn_records):
        uid = compute_hb_txn_uid(
            record["account_id"],
            record["txn_date"],
            record["amount"],
            record["direction"]
        )
        
        if uid in uid_map:
            # Collision detected
            prior_idx = uid_map[uid]
            collisions.append((prior_idx, i, uid))
        else:
            uid_map[uid] = i
    
    if collisions:
        logger.warning(f"UID collisions detected: {len(collisions)}")
        for prior_idx, curr_idx, uid in collisions:
            logger.warning(f"  Records {prior_idx} and {curr_idx} both hash to {uid}")
    
    return collisions
```

**Integration in ingest**:
```python
def ingest_transactions_with_uid(
    source_records: list[dict],
    engine,
    table_name: str = "hb_gl_txn"
) -> int:
    """
    Load transactions, assigning deterministic UIDs.
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Verify determinism before load
        verify_uid_determinism(source_records)
        
        # Detect collisions (should be zero)
        collisions = detect_uid_collisions(source_records)
        if collisions:
            raise ValueError(f"UID collisions detected: {len(collisions)}")
        
        # Assign UIDs and load
        for record in source_records:
            record["hb_txn_uid"] = compute_hb_txn_uid(
                record["account_id"],
                record["txn_date"],
                record["amount"],
                record["direction"]
            )
        
        # Insert with dedup on UID (no duplicate UIDs)
        insert_sql = text(f"""
            INSERT OR IGNORE INTO {table_name} (hb_txn_uid, ...)
            VALUES (:hb_txn_uid, ...)
        """)
        
        for record in source_records:
            session.execute(insert_sql, record)
        
        session.commit()
        logger.info(f"Loaded {len(source_records)} transactions with UIDs")
        return len(source_records)
        
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction load failed: {e}")
        raise
        
    finally:
        session.close()
```

## Idempotent Ingest Pattern

**Use case**: Load external data (bank statements, Google Sheets forms) such that rerunning with the same input produces identical final state.

**Idempotency guarantee**: Running the ingest twice with the same source → same row count, same data, no duplicates.

**Pattern overview**:
1. Staging table isolated from production (separate transaction).
2. Staging table uses same schema as production + dedup keys.
3. Load source data into staging with error capture.
4. Deduplicate staging by source reference (natural key).
5. Atomic merge of staging into production.
6. Clean up staging on commit; rollback on error.

**Code example**:

```python
from sqlalchemy import UniqueConstraint, ForeignKey
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def idempotent_ingest(
    source_records: list[dict],
    source_name: str,  # e.g., "dbs_statement_2026_03"
    target_table: str,  # e.g., "statement_line"
    dedup_key_columns: list[str],  # e.g., ["statement_ref"]
    engine
) -> dict:
    """
    Load external data with idempotence guarantee.
    
    Args:
        source_records: list of dicts to load
        source_name: stable identifier for this ingest (same per rerun)
        target_table: production table name
        dedup_key_columns: columns that define uniqueness
        engine: SQLAlchemy engine
    
    Returns:
        dict with counts: {loaded: int, skipped_dups: int, errors: list}
    
    Idempotency: rerun with same source_records → same final state
    Error recovery: failed load leaves production unchanged
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Phase 1: Create isolated staging table
        staging_table = f"staging_{target_table}_{datetime.now().timestamp()}"
        
        staging_schema_sql = f"""
            CREATE TEMPORARY TABLE {staging_table} AS
            SELECT * FROM {target_table} LIMIT 0
        """
        session.execute(text(staging_schema_sql))
        
        # Add source tracking columns if not present
        session.execute(text(f"""
            ALTER TABLE {staging_table}
            ADD COLUMN source_name TEXT
        """))
        
        # Phase 2: Load source data into staging
        load_errors = []
        for i, record in enumerate(source_records):
            try:
                record["source_name"] = source_name
                insert_stmt = text(f"""
                    INSERT INTO {staging_table} ({', '.join(record.keys())})
                    VALUES ({', '.join([f':{k}' for k in record.keys()])})
                """)
                session.execute(insert_stmt, record)
            except Exception as e:
                load_errors.append({"record_idx": i, "error": str(e)})
                logger.warning(f"Failed to load record {i}: {e}")
        
        # Phase 2b: Fail if errors exceed threshold (e.g., >10%)
        error_rate = len(load_errors) / len(source_records) if source_records else 0
        if error_rate > 0.1:
            session.rollback()
            raise ValueError(f"Load error rate {error_rate:.1%} exceeds threshold")
        
        # Phase 3: Deduplicate staging by source reference
        # Remove any duplicates within staging (same source_name + dedup_key)
        dedup_where = " AND ".join([f"s.{col} = d.{col}" for col in dedup_key_columns])
        dedup_sql = f"""
            DELETE FROM {staging_table} s
            WHERE EXISTS (
                SELECT 1 FROM {staging_table} d
                WHERE d.rowid < s.rowid
                AND d.source_name = s.source_name
                AND {dedup_where}
            )
        """
        session.execute(text(dedup_sql))
        dedup_count = session.execute(text(f"SELECT COUNT(*) FROM {staging_table}")).scalar()
        
        # Phase 4: Merge staging into production (atomically)
        # Skip rows already in production with same dedup key
        where_clause = " AND ".join([f"p.{col} = s.{col}" for col in dedup_key_columns])
        merge_sql = f"""
            INSERT OR IGNORE INTO {target_table}
            SELECT * FROM {staging_table} s
            WHERE NOT EXISTS (
                SELECT 1 FROM {target_table} p
                WHERE {where_clause}
            )
        """
        merge_result = session.execute(text(merge_sql))
        loaded = merge_result.rowcount
        skipped_dups = dedup_count - loaded
        
        # Phase 5: Commit atomically
        session.commit()
        
        logger.info(f"Idempotent ingest complete: {loaded} loaded, {skipped_dups} skipped dups, {len(load_errors)} errors")
        
        return {
            "loaded": loaded,
            "skipped_dups": skipped_dups,
            "errors": load_errors
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Idempotent ingest failed: {e}; production unchanged")
        raise
        
    finally:
        session.close()


def verify_idempotent_ingest_idempotency(
    source_records: list[dict],
    source_name: str,
    target_table: str,
    dedup_key_columns: list[str],
    engine
):
    """
    Verify that running idempotent_ingest twice produces identical results.
    """
    # Run 1
    result_1 = idempotent_ingest(source_records, source_name, target_table, dedup_key_columns, engine)
    
    # Run 2 (same source)
    result_2 = idempotent_ingest(source_records, source_name, target_table, dedup_key_columns, engine)
    
    # On rerun, no new rows should load (all are duplicates)
    assert result_2["loaded"] == 0, f"Idempotency failed: second run loaded {result_2['loaded']} rows (expected 0)"
    assert result_2["skipped_dups"] == len(source_records), f"Idempotency failed: second run skipped {result_2['skipped_dups']} (expected {len(source_records)})"
    
    logger.info("Idempotent ingest idempotency verified")
```

## Transaction Boundary and Error Recovery Pattern

**Use case**: Multi-phase operations that must either fully succeed or fully rollback.

**Pattern overview**:
1. Start transaction at operation boundary.
2. Execute each phase with explicit error capture.
3. On phase failure: rollback all prior phases.
4. On success: commit atomically.
5. Log decision and final state for audit.

**Code example**:

```python
from enum import Enum

class IngestPhase(Enum):
    VALIDATE = 1
    STAGE = 2
    DEDUPLICATE = 3
    MERGE = 4
    COMMIT = 5

def multi_phase_ingest_with_recovery(
    source_records: list[dict],
    engine
) -> dict:
    """
    Multi-phase ingest with explicit recovery and audit logging.
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    result = {
        "status": "unknown",
        "phase_completed": None,
        "error": None,
        "row_count": 0
    }
    
    try:
        # Phase 1: Validate
        result["phase_completed"] = IngestPhase.VALIDATE.name
        assert source_records, "No source records to ingest"
        logger.info(f"Validation passed for {len(source_records)} records")
        
        # Phase 2: Stage
        result["phase_completed"] = IngestPhase.STAGE.name
        # ... staging logic
        logger.info(f"Staging complete")
        
        # Phase 3: Deduplicate
        result["phase_completed"] = IngestPhase.DEDUPLICATE.name
        # ... dedup logic
        logger.info(f"Deduplication complete")
        
        # Phase 4: Merge
        result["phase_completed"] = IngestPhase.MERGE.name
        # ... merge logic
        result["row_count"] = 100  # example
        logger.info(f"Merge complete: {result['row_count']} rows")
        
        # Phase 5: Commit (atomic)
        result["phase_completed"] = IngestPhase.COMMIT.name
        session.commit()
        result["status"] = "success"
        logger.info(f"Ingest succeeded: {result['row_count']} rows committed")
        
    except Exception as e:
        session.rollback()
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error(f"Ingest failed at phase {result['phase_completed']}: {e}")
        raise
        
    finally:
        session.close()
    
    return result
```

## Validation Checklist for Data Pipelines

When implementing a data pipeline:

- [ ] Staging table is isolated from production (separate transaction scope).
- [ ] SCD Type 1 updates are deterministic (same source → zero modifications on rerun).
- [ ] UIDs are deterministic and collision-free for the scope.
- [ ] Deduplication logic uses correct natural keys.
- [ ] Ingest is idempotent (same input → same output, no side effects on rerun).
- [ ] Error recovery leaves production unchanged (rollback on failure).
- [ ] Transaction boundaries are explicit and atomic.
- [ ] Session management prevents leaks (always closed in finally block).
- [ ] Logging captures phase boundaries and decision points.
- [ ] Idempotency verified by running twice with same input.

## Related Documentation

- `docs/requirements/data-model.md` — schema definitions and ownership.
- `docs/requirements/source-systems-lineage.md` — lineage requirements.
- `docs/develop/010/design/database-schema.md` — SQLite schema design.
- Agent `python-data` — for data pipeline architecture guidance.
- Skill `homebudget` — for HomeBudget integration patterns.
