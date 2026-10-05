import requests

API_URL = "https://your-api-domain.com/documents/{document_id}"


def delete_document(document_id: str, user_token: str):
    url = API_URL.format(document_id=document_id)

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.delete(
            url,
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            print("Document deleted successfully.")
            print(response.json())

        elif response.status_code == 404:
            print(f"Document not found: {document_id}")

        elif response.status_code in (401, 403):
            print("Authentication/authorization failed. Check the user token.")

        else:
            print(f"Delete failed.")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")


if __name__ == "__main__":
    document_id = input("Enter document ID: ").strip()
    user_token = input("Enter user token: ").strip()

    delete_document(document_id, user_token)