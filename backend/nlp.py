import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def generate_sql(user_query):
    user_query_lower = user_query.lower()

    # 🔥 HARDCODED RULES (FAST + RELIABLE)
    if "top customers" in user_query_lower and "winter" in user_query_lower:
        return """
        SELECT customer_id, SUM(purchase_amount) AS total_spent
        FROM orders
        WHERE season = 'Winter'
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 5;
        """

    elif "top customers" in user_query_lower:
        return """
        SELECT customer_id, SUM(purchase_amount) AS total_spent
        FROM orders
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 5;
        """

    elif "total orders" in user_query_lower:
        return "SELECT COUNT(order_id) AS total_orders FROM orders;"

    elif "total revenue" in user_query_lower:
        return "SELECT SUM(purchase_amount) AS total_revenue FROM orders;"

    elif "monthly sales" in user_query_lower or "monthly revenue" in user_query_lower:
        return """
        SELECT DATE_TRUNC('month', order_date) AS month,
               SUM(purchase_amount) AS revenue
        FROM orders
        GROUP BY month
        ORDER BY month;
        """

    elif "revenue by season" in user_query_lower:
        return """
        SELECT season, SUM(purchase_amount) AS revenue
        FROM orders
        GROUP BY season
        ORDER BY revenue DESC;
        """

    elif "average rating" in user_query_lower:
        return "SELECT AVG(review_rating) AS avg_rating FROM customer_behavior;"

    elif "repeat customers" in user_query_lower:
        return """
        SELECT COUNT(*) AS repeat_customers
        FROM customer_behavior
        WHERE previous_purchases > 5;
        """

    # 🔥 AI FALLBACK
    try:
        prompt = f"""
        You are an expert PostgreSQL SQL generator.

        STRICT RULES:
        - Only return SQL query
        - No explanation
        - Only SELECT queries

        DATABASE SCHEMA:
        customers(customer_id, age, gender, location)
        orders(order_id, customer_id, order_date, purchase_amount, season, payment_method)
        products(product_id, item_name, category, size, color)
        order_items(order_id, product_id)
        customer_behavior(customer_id, review_rating, previous_purchases, frequency)

        EXAMPLES:

        User: total orders
        SQL: SELECT COUNT(order_id) FROM orders;

        User: revenue in winter
        SQL: SELECT SUM(purchase_amount) FROM orders WHERE season = 'Winter';

        User: top customers
        SQL: SELECT customer_id, SUM(purchase_amount) FROM orders GROUP BY customer_id ORDER BY SUM(purchase_amount) DESC LIMIT 5;

        USER QUERY:
        {user_query}
        """

        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b",
            messages=[{"role": "user", "content": prompt}]
        )

        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        print("🤖 AI SQL:", sql)

        return sql

    except Exception as e:
        print("AI Error:", e)
        return None