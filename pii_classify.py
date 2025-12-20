def classify_sheet(
    df: pd.DataFrame,
    table_name: str,
    classifier: LLMClassifier,
    examples: List[ReferenceExample],
    column_field: str,
    description_field: Optional[str],
    batch_size: int,
    support_example_count: int,
) -> pd.DataFrame:

    df = df.dropna(subset=[column_field])
    df[column_field] = df[column_field].astype(str).str.strip()

    records: List[ColumnRecord] = []
    for _, row in df.iterrows():
        col_name = row[column_field]

        desc_val = None
        if description_field and description_field in df.columns:
            val = row[description_field]
            if not pd.isna(val):
                desc_val = str(val).strip()

        table_val = row.get("table_name") if "table_name" in df.columns else None
        resolved_table = (
            str(table_val).strip()
            if table_val is not None and not pd.isna(table_val)
            else table_name
        )

        records.append(
            ColumnRecord(
                table_name=resolved_table,
                column_name=col_name,
                column_description=desc_val,
            )
        )

    # ----------------------------------------------------
    # ✔ FILTER: Only classify rows where asset_type == "col"
    # ----------------------------------------------------
    classify_records = []
    for rec, (_, row) in zip(records, df.iterrows()):
        if "asset_type" in df.columns:
            if str(row["asset_type"]).strip().lower() == "col":
                classify_records.append(rec)

    if not classify_records:
        return df
    # ----------------------------------------------------

    # Deduplicate before LLM
    unique_records = {}
    for r in classify_records:
        key = (r.table_name, r.column_name)
        if key not in unique_records:
            unique_records[key] = r
    classify_records = list(unique_records.values())

    outputs: List[Dict[str, str]] = []

    # Batch classify only selected rows
    for batch in chunked(classify_records, batch_size):

        context_examples: List[str] = []
        seen: set[str] = set()

        for rec in batch:
            for ex in find_best_examples(rec, examples, support_example_count):
                if ex not in seen:
                    seen.add(ex)
                    context_examples.append(ex)

        prompt = build_prompt(batch, context_examples[:support_example_count])
        result = classifier.classify(prompt)

        for item in result.get("rows", []):
            outputs.append(
                {
                    "table_name": item["table_name"],
                    "column_name": item["column_name"],
                    "pii_classification": item["pii_classification"],
                    "reasoning": item["reasoning"],
                }
            )

    output_df = pd.DataFrame(outputs)

    if output_df.empty:
        return df

    if "table_name" not in df.columns:
        df["table_name"] = table_name

    merged = df.merge(
        output_df,
        how="left",
        left_on=["table_name", column_field],
        right_on=["table_name", "column_name"],
    )

    merged.drop(columns=["column_name"], inplace=True)

    return merged
    
    
    
    
    
import asyncio
import json
from typing import Dict, Any
from tenacity import AsyncRetrying, wait_exponential, stop_after_attempt


async def classify(self, prompt: str) -> Dict[str, Any]:
    async with self.semaphore:
        async for attempt in AsyncRetrying(
            wait=wait_exponential(min=1, max=10),
            stop=stop_after_attempt(1),
            reraise=True,
        ):
            with attempt:
                try:
                    response = await asyncio.wait_for(
                        self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a precise data privacy analyst",
                                },
                                {
                                    "role": "user",
                                    "content": prompt,
                                },
                            ],
                            temperature=self.temperature,
                            response_format={
                                "type": "json_schema",
                                "json_schema": JSON_SCHEMA,
                            },
                        ),
                        timeout=30,   # <<< HARD TIMEOUT (seconds)
                    )

                except asyncio.TimeoutError:
                    raise TimeoutError("LLM request exceeded 30 seconds")

                payload = response.choices[0].message.content
                return json.loads(payload)