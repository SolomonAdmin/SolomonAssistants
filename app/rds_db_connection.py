# test_db_connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import urllib
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
import logging

class DatabaseConnector:
    def __init__(self):
        self.engine = None
        self.Session = None
        self._load_env_variables()
        self._create_connection_string()
        self._create_engine()

    def _load_env_variables(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(os.path.dirname(current_dir), '.env')
        load_dotenv(dotenv_path)

        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_type = os.getenv('DB_TYPE', 'mssql+pyodbc')

    def _create_connection_string(self):
        params = urllib.parse.quote_plus(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.db_host},{self.db_port};'
            f'DATABASE={self.db_name};'
            f'UID={self.db_user};'
            f'PWD={self.db_password}'
        )
        self.connection_string = f'{self.db_type}:///?odbc_connect={params}'

    def _create_engine(self):
        self.engine = create_engine(
            self.connection_string,
            echo=False,  # Set to True for debugging
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20
        )
        self.Session = sessionmaker(bind=self.engine)

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return result.scalar() == 1
        except SQLAlchemyError as e:
            logging.error(f"Database connection test failed: {e}")
            return False

    def execute_query(self, query, params=None):
        with self.Session() as session:
            try:
                result = session.execute(text(query), params or {})
                return result.fetchall()
            except SQLAlchemyError as e:
                logging.error(f"Database error in execute_query: {e}")
                session.rollback()
                raise

    def get_threads(self, solomon_consumer_key: str) -> List[Dict[str, Any]]:
        query = text("SELECT thread_id, thread_name FROM dbo.solConnectThreads WHERE solomon_consumer_key = :key")
        with self.Session() as session:
            try:
                result = session.execute(query, {"key": solomon_consumer_key})
                return [row._asdict() for row in result.fetchall()]
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving threads: {e}")
                return []
    
    def get_consumer_key_by_email(self, email: str) -> Optional[str]:
        query = text("SELECT TOP 1 solomon_consumer_key FROM dbo.solConnectConsumers WHERE customer_email = :email")
        with self.Session() as session:
            try:
                result = session.execute(query, {"email": email})
                row = result.fetchone()
                return row[0] if row else None
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving consumer key by email: {e}")
                return None
            
    def update_solomon_consumer_key(self, email: str, new_key: str) -> bool:
        query = text("UPDATE dbo.solConnectConsumers SET solomon_consumer_key = :new_key WHERE customer_email = :email")
        with self.Session() as session:
            try:
                result = session.execute(query, {"email": email, "new_key": new_key})
                session.commit()
                if result.rowcount == 0:
                    logging.warning(f"No record found for email: {email}")
                    return False
                return True
            except SQLAlchemyError as e:
                logging.error(f"Error updating Solomon consumer key: {e}")
                session.rollback()
                return False
    
    def get_workspaces_by_email(self, email: str) -> list[str]:
        query = text("""
            SELECT workspace_name
            FROM dbo.solConnectUsers 
            WHERE customer_email = :email
        """)
        
        with self.Session() as session:
            try:
                result = session.execute(query, {"email": email})
                # Extract just the workspace_name values from the result
                return [row[0] for row in result]
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving workspaces by email: {e}")
                return []
    
    def get_consumer_key_by_email_and_workspace(self, email: str, workspace_name: str) -> Optional[str]:
        query = text("""
            SELECT solomon_consumer_key
            FROM dbo.solConnectUsers 
            WHERE customer_email = :email 
            AND workspace_name = :workspace_name
        """)
        
        with self.Session() as session:
            try:
                result = session.execute(query, {
                    "email": email,
                    "workspace_name": workspace_name
                })
                row = result.fetchone()
                return row[0] if row else None
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving consumer key: {e}")
                return None
            

def test_db_connection():
    db = DatabaseConnector()
    if db.test_connection():
        print("Database connection successful")
        
        # # Test get_threads method
        # threads = db.get_threads("C69E685B-A783-4950-A040-414B69F61FCC")
        # print(f"Retrieved threads: {threads}")
        
        # Test get_consumer_key_by_email method
        test_email = "jsturgis@solomonconsult.com"
        consumer_key = db.get_consumer_key_by_email(test_email)
        if consumer_key:
            print(f"Consumer key for {test_email}: {consumer_key}")
        else:
            print(f"No consumer key found for {test_email}")
    else:
        print("Database connection failed")

if __name__ == "__main__":
    test_db_connection()

# def main():
#     db_connector = DatabaseConnector()
    
#     try:
#         # Example query
#         query = "SELECT TOP 10 * FROM dbo.solConnectConsumers WHERE solomon_consumer_key = :key"
#         params = {"key": "C69E685B-A783-4950-A040-414B69F61FCC"}
        
#         results = db_connector.execute_query(query, params)
        
#         if results:
#             for row in results:
#                 print(row)
#         else:
#             print("No results found.")
#     except Exception as e:
#         logging.error(f"Error in main: {e}")
#         print("An error occurred while executing the query.")

# if __name__ == '__main__':
#     main()