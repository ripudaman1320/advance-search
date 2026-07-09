from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import hashlib

# Create base for all models
Base = declarative_base()

class EmailDocumentDB(Base):
    """SQLite model for email documents"""
    __tablename__ = "email_documents"
    
    id = Column(String(50), primary_key=True)
    subject = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    sender_name = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    thread_id = Column(String(100), nullable=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseManager:
    """Manage SQLite connections and queries"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def add_email(self, email_data: dict) -> str:
        """Add email document to database"""
        session = self.get_session()
        try:
            # Generate ID from content hash
            email_id = hashlib.md5(
                f"{email_data['sender_email']}_{email_data['subject']}_{email_data['created_at']}".encode()
            ).hexdigest()[:16]
            
            email_db = EmailDocumentDB(
                id=email_id,
                subject=email_data['subject'],
                sender_email=email_data['sender_email'],
                sender_name=email_data.get('sender_name'),
                body=email_data['body'],
                thread_id=email_data['thread_id'],
                word_count=len(email_data['body'].split()),
                created_at=email_data.get('created_at', datetime.utcnow())
            )
            
            session.add(email_db)
            session.commit()
            return email_id
        finally:
            session.close()
    
    def get_email(self, email_id: str) -> dict:
        """Retrieve email document"""
        session = self.get_session()
        try:
            email = session.query(EmailDocumentDB).filter(
                EmailDocumentDB.id == email_id
            ).first()
            
            if email:
                return {
                    "id": email.id,
                    "subject": email.subject,
                    "sender_email": email.sender_email,
                    "sender_name": email.sender_name,
                    "body": email.body,
                    "thread_id": email.thread_id,
                    "word_count": email.word_count,
                    "created_at": email.created_at,
                }
            return None
        finally:
            session.close()
    
    def list_emails(self) -> list[dict]:
        """List all emails"""
        session = self.get_session()
        try:
            emails = session.query(EmailDocumentDB).all()
            return [
                {
                    "id": e.id,
                    "subject": e.subject,
                    "sender_email": e.sender_email,
                    "created_at": e.created_at,
                    "word_count": e.word_count,
                }
                for e in emails
            ]
        finally:
            session.close()