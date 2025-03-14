import os
import psycopg2
from psycopg2.extras import DictCursor
from pgvector.psycopg2 import register_vector
import numpy as np
import random
from datetime import datetime


class DBAction:
    __categories = ["Groceries", "Dining", "Shopping", "Entertainment", "Bills", "Travel"]
        # Mock financial data
    __mock_financial_data = {
        "user_123": {
            "name": "John Doe",
            "account_balance": 25000,
            "monthly_income": 5000,
            "most_frequent_spend": "Groceries",
            "highest_category_spend": "Travel",
            "financial_goals": "Wants to buy a house in 2 years",
            "preferred_products": ["Premium Credit Card", "Home Loan"],
            "loan_eligibility": "Eligible for Home Loan up to $200,000",
            "investment_suggestions": ["Index Funds", "Fixed Deposits"],
            "transactions": []
        }
    }

    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("PG_DB", "ai"),
            user=os.getenv("PG_USER", "ai"),
            password=os.getenv("PG_PASSWORD", "ai"),
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5532")
        )
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        register_vector(self.cursor)

    def create_tables(self):
        # Ensure table exists
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_memory (
                user_id TEXT PRIMARY KEY,
                vector VECTOR(1536),
                conversation TEXT
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                timestamp TIMESTAMP,
                amount FLOAT,
                category TEXT
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                account_balance FLOAT,
                monthly_income FLOAT,
                most_frequent_spend TEXT,
                highest_category_spend TEXT,
                financial_goals TEXT,
                preferred_products TEXT,
                loan_eligibility TEXT,
                investment_suggestions TEXT
            );
        """)

        self.conn.commit()



    def retrieve_chat_memory(self, user_id):
        # Retrieve chat memory from PgVector
        self.cursor.execute("SELECT message FROM chat_memory WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        past_chat = result[0] if result else ""
        return past_chat

    def __generate_random_transaction():
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": round(random.uniform(5, 500), 2),
            "category": random.choice(DBAction.__categories)
        }

    def store_new_transaction(self, user_id):
        new_transaction = DBAction.__generate_random_transaction()
        self.cursor.execute(
            "INSERT INTO transactions (user_id, timestamp, amount, category) VALUES (%s, %s, %s, %s)",
            (user_id, new_transaction["timestamp"], new_transaction["amount"], new_transaction["category"])
        )
        self.update_user_profile(user_id)
        self.conn.commit()

    def update_user_profile(self, user_id):
        self.cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE user_id = %s GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1", (user_id,))
        result = self.cursor.fetchone()
        highest_category_spend = result["category"]
        self.cursor.execute("SELECT category, COUNT(category) FROM transactions WHERE user_id = %s GROUP BY category ORDER BY COUNT(category) DESC LIMIT 1", (user_id,))
        result = self.cursor.fetchone()
        most_frequent_spend = result["category"]
        self.cursor.execute(
            "UPDATE users SET most_frequent_spend = %s, highest_category_spend = %s WHERE user_id = %s", 
            (most_frequent_spend, highest_category_spend, user_id)

        )
        self.conn.commit()


    def get_user_profile(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                "name": result["name"],
                "account_balance": result["account_balance"],
                "monthly_income": result["monthly_income"],
                "most_frequent_spend": result["most_frequent_spend"],
                "highest_category_spend": result["highest_category_spend"],
                "loan_eligibility": result["loan_eligibility"],
                "investment_suggestions": result["investment_suggestions"],
                "financial_goals": result["financial_goals"],
                "preferred_products": result["preferred_products"]
            }
        else:
            result = DBAction.mock_financial_data.get(user_id, {})
        return result
    
    def store_chat_memory(self, user_id, embedding, message):
        self.cursor.execute(
            "INSERT INTO chat_memory (user_id, embedding, message) VALUES (%s, %s, %s)",
            (user_id, embedding, message)
        )
        self.conn.commit()
        
    
    def close_connection(self):
        self.cursor.close() # Close the cursor
        self.conn.close() # Close the connection
        print("Connection closed")
