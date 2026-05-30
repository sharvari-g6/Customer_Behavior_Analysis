import os
from openai import OpenAI
from dotenv import load_dotenv
from db import get_connection

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def generate_insights():
    insights = []

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🔥 HARD DATA ANALYSIS

        # Total revenue
        cur.execute("SELECT SUM(purchase_amount) FROM orders;")
        total_revenue = cur.fetchone()[0]

        # Top 5 customer contribution
        cur.execute("""
            SELECT SUM(total) FROM (
                SELECT customer_id, SUM(purchase_amount) AS total
                FROM orders
                GROUP BY customer_id
                ORDER BY total DESC
                LIMIT 5
            ) t;
        """)
        top_revenue = cur.fetchone()[0]

        if total_revenue and top_revenue:
            percent = round((top_revenue / total_revenue) * 100, 2)
            insights.append(f"Top 5 customers contribute {percent}% of total revenue")

        # Best season
        cur.execute("""
            SELECT season, SUM(purchase_amount) AS revenue
            FROM orders
            GROUP BY season
            ORDER BY revenue DESC
            LIMIT 1;
        """)
        best_season = cur.fetchone()
        if best_season:
            insights.append(f"{best_season[0]} season generates highest sales")

        # Repeat customers
        cur.execute("""
            SELECT COUNT(*) FROM customer_behavior
            WHERE previous_purchases > 5;
        """)
        repeat = cur.fetchone()[0]
        insights.append(f"{repeat} customers are repeat buyers")

        cur.close()
        conn.close()

        # 🔥 AI ENHANCEMENT
        prompt = f"""
        You are a business analyst.

        Insights:
        {insights}

        Convert these into 3-5 short, professional business insights.
        """

        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_text = response.choices[0].message.content

        ai_insights = [
            line.strip("- ").strip()
            for line in ai_text.split("\n") if line.strip()
        ]

        return ai_insights

    except Exception as e:
        print("AI Insight Error:", e)

        # 🔥 PURE HARDCODED FALLBACK
        return [
            "A small group of customers contributes significantly to revenue",
            "Seasonal demand strongly influences purchasing behavior",
            "Repeat customers form a valuable customer segment"
        ]