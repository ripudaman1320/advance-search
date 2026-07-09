import re
from pathlib import Path
from datetime import datetime
from docx import Document
from app.models.schemas import EmailDocumentCreate

class DOCXEmailParser:
    """Parse DOCX files containing email messages"""
    
    @staticmethod
    def extract_email_metadata(doc: Document) -> tuple[str, str, str, str, datetime]:
        """
        Extract From, Subject, Date, Body from DOCX
        Returns: (sender_email, sender_name, subject, body, timestamp)
        """
        full_text = "\n".join([p.text for p in doc.paragraphs])
        
        # Extract From: sender@email.com or From: Name <email@email.com>
        from_pattern = r'From:\s*(?:(.+?)\s*)?<(.+?)>|From:\s*(.+?)(?:\n|$)'
        from_match = re.search(from_pattern, full_text)
        
        if from_match:
            if from_match.group(2):  # <email> format
                sender_name = from_match.group(1) or "Unknown"
                sender_email = from_match.group(2)
            else:  # plain email format
                sender_email = from_match.group(3).strip()
                sender_name = "Unknown"
        else:
            sender_name = "Unknown"
            sender_email = "unknown@email.com"
        
        # Extract Subject
        subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', full_text)
        subject = subject_match.group(1).strip() if subject_match else "No Subject"
        
        # Extract Date from metadata or use current time
        timestamp = doc.core_properties.created or datetime.utcnow()
        
        # Extract Body: after "Hi there" until signature markers
        body_start = full_text.find("Hi there")
        signature_markers = ["Best regards", "Thanks", "Cheers", "Regards"]
        
        body_end = len(full_text)
        for marker in signature_markers:
            marker_pos = full_text.rfind(marker)
            if marker_pos != -1:
                body_end = min(body_end, marker_pos)
        
        if body_start != -1:
            body = full_text[body_start:body_end].strip()
        else:
            body = full_text
        
        return sender_email, sender_name, subject, body, timestamp
    
    @staticmethod
    def parse(docx_path: str) -> EmailDocumentCreate:
        """Parse DOCX file to EmailDocumentCreate"""
        doc = Document(docx_path)
        sender_email, sender_name, subject, body, timestamp = DOCXEmailParser.extract_email_metadata(doc)
        
        return EmailDocumentCreate(
            subject=subject,
            sender_email=sender_email,
            sender_name=sender_name,
            body=body,
            timestamp=timestamp
        )

    @staticmethod
    def parse_from_path(docx_path: str) -> EmailDocumentCreate:
        """Convenience method to parse from file path"""
        path = Path(docx_path)
        if not path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        if not path.suffix.lower() == '.docx':
            raise ValueError(f"Expected .docx file, got: {path.suffix}")
        
        return DOCXEmailParser.parse(docx_path)