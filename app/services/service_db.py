# services/service_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from rds_db_connection import DatabaseConnector
import logging

class DBService:
    @staticmethod
    async def get_openai_api_key(solomon_consumer_key: str) -> str:
        db_connector = DatabaseConnector()
        try:
            query = """
                SELECT TOP 1 openai_api_key 
                FROM dbo.solConnectConsumers 
                WHERE solomon_consumer_key = :solomon_consumer_key
            """
            result = db_connector.execute_query(query, {"solomon_consumer_key": solomon_consumer_key})
            if result and result[0]:
                return result[0][0]
            else:
                logging.warning(f"No OpenAI API key found for Solomon Consumer Key: {solomon_consumer_key}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Database error in get_openai_api_key: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    @staticmethod
    async def get_consumer_info(solomon_consumer_key: str) -> dict:
        db_connector = DatabaseConnector()
        try:
            query = """
                SELECT TOP 1 
                    solomon_consumer_key,
                    customer_name,
                    aws_key,
                    create_date,
                    modified_on,
                    plan_level,
                    customer_email,
                    openai_api_key
                FROM dbo.solConnectConsumers 
                WHERE solomon_consumer_key = :solomon_consumer_key
            """
            result = db_connector.execute_query(query, {"solomon_consumer_key": solomon_consumer_key})
            print(result[0][7])
            if result and result[0]:
                return {
                    "solomon_consumer_key": result[0][0],
                    "customer_name": result[0][1],
                    "aws_key": result[0][2],
                    "create_date": result[0][3],
                    "modified_on": result[0][4],
                    "plan_level": result[0][5],
                    "customer_email": result[0][6],
                    "openai_api_key": result[0][7]
                }
            else:
                logging.warning(f"No consumer info found for Solomon Consumer Key: {solomon_consumer_key}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Database error in get_consumer_info: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    @staticmethod
    async def get_workspace_names_by_email(email: str) -> list[str]:
        db_connector = DatabaseConnector()
        try:
            query = """
                SELECT workspace_name
                FROM dbo.solConnectUsers 
                WHERE customer_email = :email
            """
            result = db_connector.execute_query(query, {"email": email})
            if result:
                return [row[0] for row in result]  # Just return the workspace names
            return []
        except SQLAlchemyError as e:
            logging.error(f"Database error in get_workspace_names_by_email: {str(e)}")
            raise Exception(f"Database error: {str(e)}")