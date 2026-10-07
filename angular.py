import os
import asyncio
import httpx
import csv
from datetime import datetime


BASE_URL = "https://localhost:8000"
UPLOAD_ENDPOINT = "/api/documents/upload"

TOKEN = "YOUR_BEARER_TOKEN"
ROOT_FOLDER = "/path/to/documents"

LOG_FILE = "upload_log.csv"


def initialize_log():
    """Create log file with headers if it doesn't exist."""

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow([
                "Timestamp",
                "Document",
                "File_Path",
                "Category",
                "Sub_Category",
                "Status",
                "HTTP_Status",
                "Response"
            ])


def write_log(
    document,
    file_path,
    category,
    sub_category,
    status,
    http_status,
    response
):
    """Write upload result to CSV."""

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            document,
            file_path,
            category,
            sub_category,
            status,
            http_status,
            response
        ])


async def upload_document(
    client: httpx.AsyncClient,
    file_path: str,
    title: str,
    category: str,
    sub_category: str
):

    url = f"{BASE_URL}{UPLOAD_ENDPOINT}"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    data = {
        "title": title,
        "category": category,
        "sub_category": sub_category
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

        # Successful response
        if 200 <= response.status_code < 300:

            print(
                f"[SUCCESS] "
                f"{category} | "
                f"{sub_category} | "
                f"{os.path.basename(file_path)}"
            )

            write_log(
                document=os.path.basename(file_path),
                file_path=file_path,
                category=category,
                sub_category=sub_category,
                status="SUCCESS",
                http_status=response.status_code,
                response=response.text
            )

            return True

        # Failed response
        else:

            print(
                f"[FAILED] "
                f"{category} | "
                f"{sub_category} | "
                f"{os.path.basename(file_path)} | "
                f"HTTP {response.status_code}"
            )

            write_log(
                document=os.path.basename(file_path),
                file_path=file_path,
                category=category,
                sub_category=sub_category,
                status="FAILED",
                http_status=response.status_code,
                response=response.text
            )

            return False

    except Exception as e:

        print(
            f"[ERROR] "
            f"{category} | "
            f"{sub_category} | "
            f"{os.path.basename(file_path)} | "
            f"{str(e)}"
        )

        write_log(
            document=os.path.basename(file_path),
            file_path=file_path,
            category=category,
            sub_category=sub_category,
            status="ERROR",
            http_status="",
            response=str(e)
        )

        return False


async def upload_all_documents():

    initialize_log()

    pdf_files = []

    # Find PDFs recursively
    for root, dirs, files in os.walk(ROOT_FOLDER):

        for file in files:

            if file.lower().endswith(".pdf"):

                full_path = os.path.join(root, file)

                pdf_files.append(full_path)

    print(f"Found {len(pdf_files)} PDF files.\n")

    successful = 0
    failed = 0
    errors = 0

    async with httpx.AsyncClient(
        verify=False,
        timeout=120.0
    ) as client:

        for pdf_path in pdf_files:

            relative_path = os.path.relpath(
                pdf_path,
                ROOT_FOLDER
            )

            path_parts = relative_path.split(os.sep)

            # PDF directly inside root folder
            if len(path_parts) < 2:

                print(
                    f"[SKIPPED] "
                    f"{pdf_path}"
                )

                continue

            # Folder name
            folder_name = path_parts[0]

            # Extract English name
            #
            # Example:
            # Accounts - الحسابات
            #       ↓
            # Accounts
            #
            english_name = folder_name.split(
                " - ",
                1
            )[0].strip()

            # Lowercase sub-category
            sub_category = english_name.lower()

            # Document name
            filename = os.path.basename(pdf_path)

            # Title without extension
            title = os.path.splitext(filename)[0]

            print(
                f"Uploading: {filename}\n"
                f"Category: WPB\n"
                f"Sub-category: {sub_category}"
            )

            result = await upload_document(
                client=client,
                file_path=pdf_path,
                title=title,
                category="WPB",
                sub_category=sub_category
            )

            if result:
                successful += 1
            else:
                failed += 1

            print()

    # Final summary
    print("\n")
    print("=" * 60)
    print("UPLOAD SUMMARY")
    print("=" * 60)

    print(f"Total documents : {len(pdf_files)}")
    print(f"Successful      : {successful}")
    print(f"Failed          : {failed}")
    print(f"Log file        : {LOG_FILE}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(upload_all_documents())