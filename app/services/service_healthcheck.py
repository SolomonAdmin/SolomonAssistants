# services/service_healthcheck.py

from sqlalchemy.exc import SQLAlchemyError
from rds_db_connection import DatabaseConnector

class HealthcheckService:
    @staticmethod
    async def check_database_connection():
        db_connector = DatabaseConnector()
        try:
            query = "SELECT 1"
            result = db_connector.execute_query(query)
            if result and result[0][0] == 1:
                return True, "Database connection successful"
            else:
                return False, "Database connection failed"
        except SQLAlchemyError as e:
            return False, f"Database connection error: {str(e)}"