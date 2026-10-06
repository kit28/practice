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