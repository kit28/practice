async def classify_batch(
    batch: List[ColumnRecord],
    classifier: AsyncLLMClassifier,
    support_example_count: int,
    table_name: str,
    chunk_id: int,
) -> List[Dict[str, str]]:

    logger.info(f"Running sheet={table_name}, chunk={chunk_id}")

    try:
        prompt = build_prompt(batch)
        result = await classifier.classify(prompt)

        outputs = []
        for item in result.get("rows", []):
            outputs.append(
                {
                    "TableName": item["table_name"],
                    "ColumnName": item["column_name"],
                    "pii_classification": item["pii_classification"],
                    "reasoning": item["reasoning"],
                }
            )
        return outputs

    except Exception as e:
        logger.exception(
            "classify_batch failed",
            extra={"table_name": table_name, "chunk_id": chunk_id},
        )
        return []   # <<< NEVER propagate


async def classify_sheet_async(
    df: pd.DataFrame,
    table_name: str,
    classifier: AsyncLLMClassifier,
    column_field: str,
    description_field: Optional[str],
    batch_size: int,
    support_example_count: int,
) -> pd.DataFrame:

    df = df.dropna(subset=[column_field])
    df[column_field] = df[column_field].astype(str).str.strip()
    df["TableName"] = df["TableName"].astype(str).str.strip()

    records: List[ColumnRecord] = []

    for _, row in df.iterrows():
        try:
            col_name = row[column_field]
            desc_val = None

            if description_field and description_field in df.columns:
                val = row[description_field]
                if pd.notna(val):
                    desc_val = str(val).strip()

            table_val = row.get("TableName")
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
        except Exception:
            logger.exception("Row processing failed")
            continue

    # De-duplicate
    records = list({(r.table_name, r.column_name): r for r in records}.values())

    tasks = [
        classify_batch(
            batch=batch,
            classifier=classifier,
            support_example_count=support_example_count,
            table_name=table_name,
            chunk_id=idx,
        )
        for idx, batch in enumerate(chunked(records, batch_size), start=1)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    outputs = []

    for idx, result in enumerate(results, start=1):
        if isinstance(result, Exception):
            logger.exception("Batch crashed", exc_info=result)
            continue
        outputs.extend(result)

    if not outputs:
        logger.warning("No successful batches for %s", table_name)
        return df

    try:
        output_df = pd.DataFrame(outputs)
        merged = df.merge(output_df, how="left", on=["TableName", "ColumnName"])
        return merged
    except Exception:
        logger.exception("Final merge failed")
        return df
