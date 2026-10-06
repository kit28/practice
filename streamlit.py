import os
import asyncio
import httpx


BASE_URL = "https://localhost:8000"
UPLOAD_ENDPOINT = "/api/documents/upload"

TOKEN = "YOUR_BEARER_TOKEN"

ROOT_FOLDER = "/path/to/documents"


async def upload_document(
    client: httpx.AsyncClient,
    file_path: str,
    title: str,
    category: str,
    sub_category: str,
):
    """
    Upload a single PDF document.
    """

    url = f"{BASE_URL}{UPLOAD_ENDPOINT}"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    data = {
        "title": title,
        "category": category,
        "sub_category": sub_category,
    }

    try:
        with open(file_path, "rb") as f:

            files = {
                "file": (
                    os.path.basename(file_path),
                    f,
                    "application/pdf"
                )
            }

            response = await client.post(
                url,
                headers=headers,
                data=data,
                files=files
            )

        print(
            f"[{response.status_code}] "
            f"{sub_category} -> {os.path.basename(file_path)}"
        )

        if response.status_code >= 400:
            print("Response:", response.text)

        return response

    except Exception as e:

        print(
            f"[ERROR] {file_path} | {str(e)}"
        )

        return None


async def upload_all_documents():

    # Find all PDFs recursively
    pdf_files = []

    for root, dirs, files in os.walk(ROOT_FOLDER):

        for file in files:

            if file.lower().endswith(".pdf"):

                full_path = os.path.join(root, file)
                pdf_files.append(full_path)

    print(f"Found {len(pdf_files)} PDF files.\n")

    async with httpx.AsyncClient(
        verify=False,
        timeout=120.0
    ) as client:

        for pdf_path in pdf_files:

            # Get path relative to root folder
            relative_path = os.path.relpath(
                pdf_path,
                ROOT_FOLDER
            )

            # First folder = sub_category
            path_parts = relative_path.split(os.sep)

            if len(path_parts) < 2:
                print(
                    f"[SKIPPED] PDF is directly inside root folder: "
                    f"{pdf_path}"
                )
                continue

            sub_category = path_parts[0]

            # Filename without .pdf = title
            filename = os.path.basename(pdf_path)

            title = os.path.splitext(filename)[0]

            await upload_document(
                client=client,
                file_path=pdf_path,
                title=title,
                category="WPB",
                sub_category=sub_category
            )

            print()


if __name__ == "__main__":
    asyncio.run(upload_all_documents())
    
    
    
    
import pandas as pd
import httpx
import asyncio


BASE_URL = "https://localhost:8000"
TOKEN = "YOUR_BEARER_TOKEN"

EXCEL_FILE = "/path/to/documents.xlsx"

DELETE_ENDPOINT = "/api/documents/{}"


async def delete_document(
    client: httpx.AsyncClient,
    doc_id: str
):
    url = f"{BASE_URL}{DELETE_ENDPOINT.format(doc_id)}"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    try:
        response = await client.delete(
            url,
            headers=headers
        )

        if response.status_code in [200, 204]:
            print(f"[SUCCESS] Deleted document: {doc_id}")
            return True

        else:
            print(
                f"[FAILED] {doc_id} | "
                f"Status: {response.status_code} | "
                f"Response: {response.text}"
            )
            return False

    except Exception as e:
        print(f"[ERROR] {doc_id} | {str(e)}")
        return False


async def delete_wpb_documents():

    # Read Excel
    df = pd.read_excel(EXCEL_FILE)

    print(f"Total rows in Excel: {len(df)}")

    # Filter WPB documents
    wpb_df = df[
        df["category"]
        .astype(str)
        .str.strip()
        .str.upper()
        == "WPB"
    ]

    # Get document IDs
    doc_ids = (
        wpb_df["doc_id"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    print(f"WPB documents found: {len(doc_ids)}")

    if not doc_ids:
        print("No WPB documents found.")
        return

    print("\nStarting deletion...\n")

    successful = 0
    failed = 0

    async with httpx.AsyncClient(
        verify=False,
        timeout=120.0
    ) as client:

        for doc_id in doc_ids:

            result = await delete_document(
                client,
                doc_id
            )

            if result:
                successful += 1
            else:
                failed += 1

    print("\n" + "=" * 50)
    print("DELETE SUMMARY")
    print("=" * 50)
    print(f"WPB documents : {len(doc_ids)}")
    print(f"Successful    : {successful}")
    print(f"Failed        : {failed}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(delete_wpb_documents())