import asyncio
import uuid
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Third-party imports
from sqlalchemy import Column, String, Text, Date, TIMESTAMP, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base  # Updated import for SQLAlchemy 2.0
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from pydantic import BaseModel, ValidationError, field_validator  # Updated to field_validator
from pydantic import ConfigDict  # Updated config syntax
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base - Updated for SQLAlchemy 2.0
Base = declarative_base()


# SQLAlchemy Model for Neon PostgreSQL
class Document(Base):
    __tablename__ = 'documents'

    document_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_uri = Column(Text, nullable=False)
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)
    doc_no = Column(String(100))
    dname = Column(String(255))
    rdate = Column(Date)
    sro_name = Column(String(255))
    property_description = Column(Text)
    sro_code = Column(String(50))
    status = Column(String(50))
    extra_data = Column(JSONB, default={})
    property_id = Column(PG_UUID(as_uuid=True))
    seller_name = Column(ARRAY(Text))
    purchaser_name = Column(ARRAY(Text))


# Pydantic Models for Validation - Updated to Pydantic V2
class DocumentInput(BaseModel):
    # Updated to Pydantic V2 config syntax
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )

    DocNo: str
    DName: str
    RDate: str
    SROName: str
    PropertyDescription: str = ""
    SROCode: str
    Status: str
    SellerName: List[str] = []
    PurchaserName: List[str] = []

    # IndexII is intentionally excluded as per requirements

    @field_validator('RDate')
    @classmethod
    def parse_date(cls, v):
        """Convert date string from DD/MM/YYYY format to date object"""
        try:
            if isinstance(v, str):
                return datetime.strptime(v, '%d/%m/%Y').date()
            return v
        except ValueError:
            raise ValueError(f'Invalid date format. Expected DD/MM/YYYY, got: {v}')

    @field_validator('DocNo', 'DName', 'SROName', 'SROCode', 'Status')
    @classmethod
    def validate_required_strings(cls, v):
        """Ensure required string fields are not empty"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    @field_validator('SellerName', 'PurchaserName', mode='before')
    @classmethod
    def validate_name_lists(cls, v):
        """Clean up name lists and remove quotes"""
        if isinstance(v, list):
            cleaned_names = []
            for name in v:
                if isinstance(name, str):
                    # Remove surrounding quotes and extra whitespace
                    cleaned_name = name.strip().strip('"').strip("'").strip()
                    if cleaned_name:
                        cleaned_names.append(cleaned_name)
            return cleaned_names
        elif isinstance(v, str):
            # If it's a single string, convert to list
            cleaned_name = v.strip().strip('"').strip("'").strip()
            return [cleaned_name] if cleaned_name else []
        return []


class NeonDocumentService:
    def __init__(self, file_uri_default: str = "neon_document_upload"):
        """
        Initialize the NeonDocumentService with async database connection

        Args:
            file_uri_default: Default file URI for documents
        """
        self.database_url, use_ssl_connection = self._get_database_url()
        self.file_uri_default = file_uri_default

        connect_args = {
            "server_settings": {
                "jit": "off"  # Disable JIT for better compatibility with Neon
            }
        }

        # For asyncpg, SSL is handled differently - use ssl parameter in connect_args
        if use_ssl_connection:
            connect_args["ssl"] = "require"  # Use string instead of boolean for asyncpg

        # Create async engine for Neon PostgreSQL
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections every 5 minutes
            connect_args=connect_args
        )

        # Create async session factory for SQLAlchemy 2.0
        self.async_session = lambda: AsyncSession(
            bind=self.engine,
            expire_on_commit=False
        )

    def _get_database_url(self) -> tuple[str, bool]:
        """
        Get database URL from environment variables

        Returns:
            Tuple of (database connection string, use_ssl_flag)

        Raises:
            ValueError: If DATABASE_URL is not found in environment
        """
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError(
                "DATABASE_URL not found in environment variables. "
                "Please ensure your .env file contains the Neon PostgreSQL connection string."
            )

        # Initialize use_ssl flag
        use_ssl = False

        # List of parameters that asyncpg doesn't understand but PostgreSQL uses
        asyncpg_incompatible_params = [
            'sslmode', 'sslcert', 'sslkey', 'sslrootcert', 'sslcrl',
            'channel_binding', 'gssencmode', 'krbsrvname', 'gsslib',
            'service', 'passfile', 'requiressl', 'prefer_prepared_statements'
        ]

        # Handle different URL schemes and SSL configuration
        if database_url.startswith(('postgresql://', 'postgres://')):
            parsed_url = urlparse(database_url)
            query_params = parse_qs(parsed_url.query)

            # Extract SSL mode before removing it
            ssl_mode = query_params.get('sslmode', ['require'])[0]  # Default to 'require' for Neon
            use_ssl = ssl_mode.lower() not in ('disable', 'allow')

            # Remove all asyncpg-incompatible parameters
            for param in asyncpg_incompatible_params:
                query_params.pop(param, None)

            # Reconstruct the query string without incompatible parameters
            new_query = urlencode(query_params, doseq=True)

            # Use postgresql+asyncpg scheme
            database_url = urlunparse(
                parsed_url._replace(scheme='postgresql+asyncpg', query=new_query)
            )

        # If it already has the asyncpg scheme, just ensure incompatible params are handled
        elif database_url.startswith('postgresql+asyncpg://'):
            parsed_url = urlparse(database_url)
            query_params = parse_qs(parsed_url.query)

            # Extract SSL mode before removing it
            ssl_mode = query_params.get('sslmode', ['require'])[0]
            use_ssl = ssl_mode.lower() not in ('disable', 'allow')

            # Remove all asyncpg-incompatible parameters
            for param in asyncpg_incompatible_params:
                query_params.pop(param, None)

            new_query = urlencode(query_params, doseq=True)
            database_url = urlunparse(parsed_url._replace(query=new_query))

        logger.info(f"Successfully processed database URL. SSL enabled: {use_ssl}")
        return database_url, use_ssl

    async def init_database(self):
        """Initialize database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def validate_document_data(self, document_data: Dict[str, Any]) -> DocumentInput:
        """
        Validate a single document's data

        Args:
            document_data: Dictionary containing document information

        Returns:
            DocumentInput: Validated document data

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Handle field name mapping for keys with spaces
            mapped_data = {
                'DocNo': document_data.get('DocNo'),
                'DName': document_data.get('DName'),
                'RDate': document_data.get('RDate'),
                'SROName': document_data.get('SROName'),
                'PropertyDescription': document_data.get('Property Description', ''),
                'SROCode': document_data.get('SROCode'),
                'Status': document_data.get('Status'),
                'SellerName': document_data.get('Seller Name', []),
                'PurchaserName': document_data.get('Purchaser Name', []),
                # IndexII is intentionally ignored
            }

            return DocumentInput(**mapped_data)
        except ValidationError as e:
            logger.error(f"Validation error for document {document_data.get('DocNo', 'Unknown')}: {e}")
            raise

    async def save_document(self, validated_data: DocumentInput, session: AsyncSession) -> Document:
        """
        Save a validated document to the database

        Args:
            validated_data: Validated document data
            session: Async database session

        Returns:
            Document: Saved document instance
        """
        try:
            document = Document(
                file_uri=self.file_uri_default,
                doc_no=validated_data.DocNo,
                dname=validated_data.DName,
                rdate=validated_data.RDate,
                sro_name=validated_data.SROName,
                property_description=validated_data.PropertyDescription,
                sro_code=validated_data.SROCode,
                status=validated_data.Status,
                seller_name=validated_data.SellerName,
                purchaser_name=validated_data.PurchaserName,
                extra_data={}
            )

            session.add(document)
            await session.commit()
            await session.refresh(document)

            logger.info(f"Successfully saved document: {document.doc_no}")
            return document

        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving document {validated_data.DocNo}: {e}")
            raise

    async def process_documents_batch(self, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process and save a batch of documents asynchronously

        Args:
            documents_data: List of document dictionaries

        Returns:
            Dict containing processing results
        """
        results = {
            'successful': [],
            'failed': [],
            'total_processed': len(documents_data),
            'success_count': 0,
            'error_count': 0
        }

        async with self.async_session() as session:
            try:
                for i, document_data in enumerate(documents_data):
                    try:
                        # Skip the last invalid record (appears to be test data)
                        if (document_data.get('DocNo') == "1" and
                                document_data.get('DName') == "2"):
                            logger.info("Skipping invalid test record")
                            continue

                        # Validate document data
                        validated_data = self.validate_document_data(document_data)

                        # Save to database
                        saved_document = await self.save_document(validated_data, session)

                        results['successful'].append({
                            'index': i,
                            'doc_no': saved_document.doc_no,
                            'document_id': str(saved_document.document_id)
                        })
                        results['success_count'] += 1

                    except Exception as e:
                        error_info = {
                            'index': i,
                            'doc_no': document_data.get('DocNo', 'Unknown'),
                            'error': str(e)
                        }
                        results['failed'].append(error_info)
                        results['error_count'] += 1
                        logger.error(f"Failed to process document at index {i}: {e}")

            except Exception as e:
                logger.error(f"Critical error during batch processing: {e}")
                raise

        return results

    async def get_document_by_doc_no(self, doc_no: str) -> Optional[Document]:
        """
        Retrieve a document by its DocNo asynchronously

        Args:
            doc_no: Document number

        Returns:
            Document instance or None if not found
        """
        async with self.async_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(
                    select(Document).where(Document.doc_no == doc_no)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error retrieving document {doc_no}: {e}")
                raise

    async def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents from the database asynchronously

        Returns:
            List of Document instances
        """
        async with self.async_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(select(Document))
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error retrieving all documents: {e}")
                raise

    async def get_documents_by_status(self, status: str) -> List[Document]:
        """
        Retrieve documents by status asynchronously

        Args:
            status: Document status

        Returns:
            List of Document instances
        """
        async with self.async_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(
                    select(Document).where(Document.status == status)
                )
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error retrieving documents by status {status}: {e}")
                raise

    async def close(self):
        """Close the database engine"""
        await self.engine.dispose()
        logger.info("Database connection closed")


# Utility functions for easy usage
async def process_json_file(file_path: str, service: NeonDocumentService = None) -> Dict[str, Any]:
    """
    Process a JSON file containing document data

    Args:
        file_path: Path to JSON file
        service: Optional service instance

    Returns:
        Processing results dictionary
    """
    if service is None:
        service = NeonDocumentService()

    try:
        # Initialize database if needed
        await service.init_database()

        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            documents_data = json.load(f)

        # Process documents
        results = await service.process_documents_batch(documents_data)

        return results

    except Exception as e:
        logger.error(f"Error processing JSON file {file_path}: {e}")
        raise
    finally:
        await service.close()


# Example usage and testing
async def main():
    """
    Example usage of the NeonDocumentService
    """
    service = None  # Initialize service variable
    try:
        # Initialize service
        service = NeonDocumentService()

        # Initialize database tables
        await service.init_database()

        # Sample data for testing (subset of your provided data)
        sample_data = [
            {
                "DocNo": "2547",
                "DName": "पुरवणी करारनामा",
                "RDate": "03/03/2021",
                "SROName": "सह दु.नि.हवेली 1",
                "Seller Name": [
                    "भाडेकरू  -  स्टेट बँक ऑफ इंडिया थ्रु ऑथोराइज़्ड सिग्नेटोरी प्रकाश मोतीलाल  डुंगरवाल"
                ],
                "Purchaser Name": [
                    "मालक-दीपा संतोष आथवाणी--",
                    "मालक - संतोष मूलचंद आथवाणी--"
                ],
                "Property Description": "इतर  माहिती: पुणे मनापा हदीतील औंध येथील...",
                "SROCode": "1",
                "Status": "4",
                "IndexII": ""
            },
            {
                "DocNo": "8939",
                "DName": "हक्कसोडपत्र",
                "RDate": "16/07/2021",
                "SROName": "सह दु.नि.हवेली 1",
                "Seller Name": [
                    "सुमनमनोहरटिंगरे",
                    "लक्ष्मीबाईनथोबाचोंधे"
                ],
                "Purchaser Name": [
                    "विकासनथोबाचोंधे"
                ],
                "Property Description": "मौजे औंध येथील खालील नमूद मिळकतीतील...",
                "SROCode": "1",
                "Status": "4",
                "IndexII": ""
            }
        ]

        # Process documents
        print("Processing documents...")
        results = await service.process_documents_batch(sample_data)

        # Print results
        print(f"\n=== Processing Results ===")
        print(f"Total Processed: {results['total_processed']}")
        print(f"Successful: {results['success_count']}")
        print(f"Failed: {results['error_count']}")

        if results['successful']:
            print("\nSuccessfully processed documents:")
            for doc in results['successful']:
                print(f"  - DocNo: {doc['doc_no']}, ID: {doc['document_id']}")

        if results['failed']:
            print("\nFailed documents:")
            for failed in results['failed']:
                print(f"  - Index {failed['index']}, DocNo: {failed['doc_no']}, Error: {failed['error']}")

        # Test retrieval
        if results['successful']:
            doc_no = results['successful'][0]['doc_no']
            print(f"\n=== Testing Document Retrieval ===")
            retrieved_doc = await service.get_document_by_doc_no(doc_no)
            if retrieved_doc:
                print(f"Retrieved document: {retrieved_doc.doc_no} - {retrieved_doc.dname}")
                print(f"Seller names: {retrieved_doc.seller_name}")
                print(f"Purchaser names: {retrieved_doc.purchaser_name}")

        # Get all documents
        all_docs = await service.get_all_documents()
        print(f"\nTotal documents in database: {len(all_docs)}")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        # Only close service if it was successfully initialized
        if service is not None:
            await service.close()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
