https://excalidraw.com/#json=-tj6_-b4UOMwZF_k5dgbN,7-Pi7A5qs1qWUOfZkZH3Vg
https://excalidraw.com/#json=8O1ykPU1DFkcpnFOAcX3G,s7lGyqQcqD2prHCIT8DDXA
https://excalidraw.com/#json=thHpZM_jMCM4vANcAcR6F,ux6M9rzaO-DzLA91rTTbqQ


import httpx
import time
import asyncio


async def delete_document(document_id: str, token: str):

    url = f"https://localhost:8000/api/documents/{document_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    start_time = time.time()

    async with httpx.AsyncClient(
        verify=False,
        timeout=120.0
    ) as client:

        response = await client.delete(
            url,
            headers=headers
        )

    print(f"HTTP Status: {response.status_code}")
    print(f"Time: {time.time() - start_time:.2f}s")
    print(response.text)

    return response


asyncio.run(
    delete_document(
        document_id="c44379ea-167f-4dec-93e9-a2f63c28776a",
        token="YOUR_BEARER_TOKEN"
    )
)


import httpx
import asyncio


async def upload_document(
    file_path: str,
    title: str,
    category: str,
    description: str = None,
    sub_category: str = None,
    token: str = "YOUR_BEARER_TOKEN"
):
    url = "https://localhost:8000/api/documents/upload"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Form fields
    data = {
        "title": title,
        "category": category,
    }

    # Optional fields
    if description is not None:
        data["description"] = description

    if sub_category is not None:
        data["sub_category"] = sub_category

    # File
    with open(file_path, "rb") as f:

        files = {
            "file": (
                file_path.split("/")[-1],
                f,
                "application/octet-stream"
            )
        }

        async with httpx.AsyncClient(
            verify=False,
            timeout=120.0
        ) as client:

            response = await client.post(
                url,
                headers=headers,
                data=data,
                files=files
            )

    print("HTTP Status:", response.status_code)
    print("Response:", response.text)

    return response


asyncio.run(
    upload_document(
        file_path="/path/to/document.pdf",
        title="My Document",
        category="Finance",
        description="Test document",
        sub_category="Reports",
        token="YOUR_BEARER_TOKEN"
    )
)