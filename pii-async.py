async def runner():
    chunk_size = 500

    for sheet_name, df in sheet_map.items():

        if args.target_column not in df.columns:
            continue

        logger.info(f"Processing sheet: {sheet_name}")

        all_results = []

        for start in range(0, len(df), chunk_size):
            df_chunk = df.iloc[start:start + chunk_size]

            logger.info(
                f"{sheet_name} | rows {start} to {start + len(df_chunk) - 1}"
            )

            chunk_result = await classify_sheet_async(
                df=df_chunk,
                table_name=f"{sheet_name}_chunk_{start // chunk_size}",
                classifier=classifier,
                examples=examples,
                column_field=args.target_column,
                description_field=args.target_description,
                batch_size=args.batch_size,
                support_example_count=args.support_example_count,
            )

            all_results.append(chunk_result)

        # combine all chunks for this sheet
        final_df = pd.concat(all_results, ignore_index=True)

        final_df.to_excel(
            f"outputs/{sheet_name}_classified.xlsx",
            index=False
        )