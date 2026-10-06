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