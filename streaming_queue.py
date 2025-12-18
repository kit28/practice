
import argparse
import json
import sys
import asyncio
import logging
import pandas as pd
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential
from logger import setup_logging
import csv
import os


@dataclass
class ColumnRecord:
    table_name: str
    column_name: str
    column_description: Optional[str]


JSON_SCHEMA = {
    "name": "pii_classification_batch",
    "schema": {
        "type": "object",
        "properties": {
            "rows": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "column_name": {"type": "string"},
                        "pii_classification": {
                            "type": "string",
                            "enum": ["PII", "Not PII", "Unknown"],
                        },
                        "reasoning": {"type": "string"},
                    },
                    "required": [
                        "table_name",
                        "column_name",
                        "pii_classification",
                        "reasoning",
                    ],
                },
            }
        },
        "required": ["rows"],
    },
}


def build_prompt(records: List[ColumnRecord]) -> str:
    guideline = """You are classifying dataset columns into:
- PII
- Not PII
- Unknown
(Be conservative)"""

    rows = []
    for i, r in enumerate(records, 1):
        rows.append(
            f"{i}. table_name: {r.table_name}\n"
            f"   column_name: {r.column_name}\n"
            f"   column_description: {r.column_description or ''}"
        )

    return guideline + "\n\n" + "\n".join(rows)


class AsyncLLMClassifier:
    def __init__(self, model: str, temperature: float, concurrency: int):
        self.model = model
        self.temperature = temperature
        self.concurrency = concurrency

    async def setup(self):
        self.client = AsyncOpenAI(
            api_key="EMPTY",
            base_url="http://localhost:8003/v1/",
            max_retries=0,
        )
        self.semaphore = asyncio.Semaphore(self.concurrency)

    async def classify(self, prompt: str) -> Dict[str, Any]:
        async with self.semaphore:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(2),
                wait=wait_exponential(min=1, max=10),
                reraise=True,
            ):
                with attempt:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a precise data privacy analyst."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=self.temperature,
                        response_format={
                            "type": "json_schema",
                            "json_schema": JSON_SCHEMA,
                        },
                    )
                    return json.loads(response.choices[0].message.content)


async def worker(
    worker_id: int,
    queue: asyncio.Queue,
    classifier: AsyncLLMClassifier,
    writer_lock: asyncio.Lock,
    output_path: str,
    logger: logging.Logger,
):
    while True:
        batch = await queue.get()
        if batch is None:
            queue.task_done()
            break

        prompt = build_prompt(batch)
        logger.info("Worker-%d processing batch size=%d", worker_id, len(batch))

        result = await classifier.classify(prompt)

        async with writer_lock:
            with open(output_path, "a", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["TableName", "ColumnName", "pii_classification", "reasoning"],
                )
                for row in result.get("rows", []):
                    writer.writerow(
                        {
                            "TableName": row["table_name"],
                            "ColumnName": row["column_name"],
                            "pii_classification": row["pii_classification"],
                            "reasoning": row["reasoning"],
                        }
                    )

        queue.task_done()


async def producer(
    df_iter,
    table_name: str,
    column_field: str,
    description_field: Optional[str],
    batch_size: int,
    queue: asyncio.Queue,
):
    batch = []

    for df in df_iter:
        for _, row in df.iterrows():
            batch.append(
                ColumnRecord(
                    table_name=table_name,
                    column_name=str(row[column_field]).strip(),
                    column_description=str(row[description_field]).strip()
                    if description_field and not pd.isna(row[description_field])
                    else None,
                )
            )

            if len(batch) == batch_size:
                await queue.put(batch)
                batch = []

    if batch:
        await queue.put(batch)


async def run_pipeline(args):
    logger = logging.getLogger("pipeline")

    classifier = AsyncLLMClassifier(
        model=args.model,
        temperature=args.temperature,
        concurrency=5,
    )
    await classifier.setup()

    queue = asyncio.Queue(maxsize=10)
    writer_lock = asyncio.Lock()

    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/final_output.csv"

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["TableName", "ColumnName", "pii_classification", "reasoning"],
        )
        writer.writeheader()

    workers = [
        asyncio.create_task(
            worker(i, queue, classifier, writer_lock, output_path, logger)
        )
        for i in range(5)
    ]

    df_iter = pd.read_csv(
        args.input_file,
        chunksize=5000,  # tune as needed
    )

    await producer(
        df_iter=df_iter,
        table_name=args.table_name,
        column_field=args.target_column,
        description_field=args.target_description,
        batch_size=args.batch_size,
        queue=queue,
    )

    for _ in workers:
        await queue.put(None)

    await queue.join()

    for w in workers:
        await w

    logger.info("Processing completed")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--table-name", default="set_2")
    parser.add_argument("--target-column", default="ColumnName")
    parser.add_argument("--target-description", default="Description")
    parser.add_argument("--model", required=True)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--batch-size", type=int, default=100)
    return parser.parse_args()


def main():
    setup_logging("logs")
    args = parse_args()
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
