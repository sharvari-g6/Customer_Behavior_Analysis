from flask import Flask, jsonify, request
from db import get_connection
from nlp import generate_sql
from report import generate_insights
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Backend Running 🚀"


def format_result(cur):
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def is_safe_query(sql):
    return sql and sql.lower().strip().startswith("select")


@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_query = request.json.get("query")

        print(f"\n🧠 User Query: {user_query}")

        sql = generate_sql(user_query)

        # 🔥 Fallback if AI fails
        if not sql:
            if "top customers" in user_query.lower():
                sql = """
                SELECT customer_id, SUM(purchase_amount) AS total_spent
                FROM orders
                GROUP BY customer_id
                ORDER BY total_spent DESC
                LIMIT 5;
                """
            else:
                return jsonify({
                    "status": "error",
                    "message": "AI failed and no fallback available"
                })

        print(f"⚡ SQL:\n{sql}")

        if not is_safe_query(sql):
            return jsonify({
                "status": "error",
                "message": "Only SELECT queries allowed"
            })

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(sql)
        data = format_result(cur)

        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "query": user_query,
            "generated_sql": sql,
            "result": data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/insights", methods=["GET"])
def insights():
    try:
        data = generate_insights()
        return jsonify({"status": "success", "insights": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/health")
def health():
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(debug=True)