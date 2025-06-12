import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleDocsService:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/documents.readonly"]
        )
        self.service = build('docs', 'v1', credentials=self.creds)

    def get_document_text(self, document_id: str) -> str:
        doc = self.service.documents().get(documentId=document_id).execute()
        text = self._read_structural_elements(doc.get('body', {}).get('content', []))
        return text

    def _read_structural_elements(self, elements) -> str:
        text = ''
        for value in elements:
            if 'paragraph' in value:
                elements = value.get('paragraph').get('elements', [])
                for elem in elements:
                    if 'textRun' in elem:
                        text += elem['textRun'].get('content', '')
            elif 'table' in value:
                # Optionally handle tables if needed
                pass
            elif 'tableOfContents' in value:
                # Optionally handle TOC if needed
                pass
        return text 