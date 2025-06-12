import os
from typing import List
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
from src.models import KnowledgeBase, Fact

class GoogleSheetsService:
    def __init__(self, credentials_path: str, spreadsheet_id: str, range_name: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        # Uncomment when Google Cloud is up
        # self.creds = service_account.Credentials.from_service_account_file(
        #     credentials_path,
        #     scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        # )
        # self.service = build('sheets', 'v4', credentials=self.creds)

    def get_knowledge_base(self) -> KnowledgeBase:
        # Uncomment and use this when Google Cloud is up
        # sheet = self.service.spreadsheets()
        # result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=self.range_name).execute()
        # values = result.get('values', [])
        # return self._parse_sheet(values)
        # Fallback to local data for now
        return self._fallback_local()

    def _parse_sheet(self, values: List[List[str]]) -> KnowledgeBase:
        # Example assumes columns: number, description, last_validated
        facts = []
        for row in values[1:]:  # Skip header
            try:
                number = int(row[0])
                description = row[1]
                last_validated = row[2]
                facts.append(Fact(number=number, description=description, last_validated=last_validated))
            except Exception:
                continue
        return KnowledgeBase(title="Current RN Project Facts", facts=facts)

    def _fallback_local(self) -> KnowledgeBase:
        # Import the local fallback
        from src.hardcoded_data import get_current_knowledge_base
        return get_current_knowledge_base() 