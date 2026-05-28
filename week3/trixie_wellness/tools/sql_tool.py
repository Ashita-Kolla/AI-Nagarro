"""
sql_tool.py
-----------
Text-to-SQL querying tool for Trixie AI's wellness database.
Uses LangChain core prompt templates and the local TinyLlama model to translate
natural language questions into valid SQLite queries, executes them,
and synthesizes empathetic responses.
"""

import os
import re
import sqlite3
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm.tinyllama import chat
from database import DB_PATH

# ---------------------------------------------------------------------------
# Prompts Definitions
# ---------------------------------------------------------------------------

SQL_GENERATION_TEMPLATE = """You are a precise SQLite query generator for an employee wellness database.

Analyze the user's natural language question and convert it into a valid SQLite query.
Respond with ONLY the SQLite query inside a ```sql ... ``` block or as plain text. Do not provide any conversational text or explanation.

Database Schema:
{schema_context}

SQLite Date Functions and Time Calculations:
- SQLite does not have a dedicated DATETIME type. Dates are stored as strings.
- Current date: `date('now')`
- Yesterday: `date('now', '-1 day')`
- Start of this week: `date('now', '-7 days')`
- Start of this month: `date('now', 'start of month')`
- Current month: `strftime('%m', 'now')`
- Substring of timestamp matches: e.g. `timestamp LIKE '2026-05%'` for May 2026.

Important Mappings:
- Mood severity or stress level ordering (from lowest to highest):
  CASE stress_level WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 ELSE 0 END
  Or similarly for severity:
  CASE severity WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 ELSE 0 END
- Emotion score mapping (average mood score, higher is better):
  CASE emotion
    WHEN 'happy' THEN 5
    WHEN 'neutral' THEN 4
    WHEN 'tired' THEN 3
    WHEN 'stressed' THEN 2
    WHEN 'anxious' THEN 2
    WHEN 'overwhelmed' THEN 1
    ELSE 3
  END

Examples:
Question: "When was my stress level highest this month?"
Query: SELECT timestamp, stress_level, user_input FROM mood_logs WHERE timestamp >= date('now', 'start of month') AND stress_level != '' ORDER BY CASE stress_level WHEN 'high' THEN 3 WHEN 'medium' THEN 2 WHEN 'low' THEN 1 ELSE 0 END DESC, timestamp DESC LIMIT 1;

Question: "How many journal entries did I make this week?"
Query: SELECT COUNT(*) as total_entries FROM journal_metadata WHERE timestamp >= date('now', '-7 days');

Question: "Show my average mood score."
Query: SELECT AVG(CASE emotion WHEN 'happy' THEN 5 WHEN 'neutral' THEN 4 WHEN 'tired' THEN 3 WHEN 'stressed' THEN 2 WHEN 'anxious' THEN 2 WHEN 'overwhelmed' THEN 1 ELSE 3 END) as avg_mood FROM mood_logs;

Only output valid SQLite query code. Respond with ONLY the query inside standard markdown ```sql ... ``` block or as plain text. Do not explain the code. Write the SQLite query now.

Question: {question}
Query:"""

SYNTHESIS_TEMPLATE = """You are Trixie AI, a warm, supportive employee wellness advisor.
Given a user's question, the SQL query executed, and the raw database result, synthesize a caring and beautifully structured insights response.

Database Schema context:
- Table 'mood_logs' contains: stress_level, emotion, sleep_hours, user_input, timestamp
- Table 'journal_metadata' contains: content, emotion, severity, cause, timestamp

Guidelines:
1. Never mention database tables, SQL queries, columns, or database records (e.g. do not say "mood_logs", "query result", "database", "SQL", "stress_level column").
2. Write in a highly empathetic and supportive tone.
3. Structure your response into exactly three sections:
   - A warm, supportive opening paragraph summarizing what the data shows in simple human terms.
   - A bulleted list of 2-3 key findings/facts from the query results (e.g., specific dates, values, sleep hours, stress causes) using bold terms.
   - A bulleted list of 2-3 warm, actionable suggestions to help the employee.
4. Keep the sections concise so it doesn't get cut off.
5. Limit the entire response to around 150 words in total. Keep each section extremely brief, focused, and high-impact to stay within this limit.

Structure Format to follow exactly:
Hi there! [Write a warm, empathetic opening paragraph summarizing the data findings in human terms without database jargon]

### Key Insights
- **Highest Stress Point**: On [Date], stress level was [level] because: "[Brief context from user_input if present]"
- **Wellness Pattern**: [Summarize the pattern or other data points found]

### Empathetic Next Steps
- **Take a Breath**: [Actionable tip 1]
- **Support System**: [Actionable tip 2]

---

User Question: {question}
SQL Query: {query}
Raw Database Result: {result}

Write the structured response now:"""


# ---------------------------------------------------------------------------
# LangChain components setup
# ---------------------------------------------------------------------------

sql_gen_prompt_template = PromptTemplate.from_template(SQL_GENERATION_TEMPLATE)
synthesis_prompt_template = PromptTemplate.from_template(SYNTHESIS_TEMPLATE)

def get_db_schema() -> str:
    """Dynamically retrieves the schema of all user tables in the SQLite database."""
    try:
        if not os.path.exists(DB_PATH):
            return "No database found."
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get list of all non-system tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row["name"] for row in cursor.fetchall()]
        
        schema_text = []
        for index, table in enumerate(tables, 1):
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            col_strings = []
            for col in columns:
                pk_suffix = " PRIMARY KEY" if col["pk"] else ""
                not_null = " NOT NULL" if col["notnull"] else ""
                dflt = f" DEFAULT {col['dflt_value']}" if col["dflt_value"] is not None else ""
                col_strings.append(f"   - {col['name']} {col['type']}{pk_suffix}{not_null}{dflt}")
            
            table_schema = f"{index}. Table '{table}':\n" + "\n".join(col_strings)
            schema_text.append(table_schema)
            
        conn.close()
        return "\n\n".join(schema_text)
    except Exception as e:
        return f"Error retrieving dynamic schema: {e}"

def clean_sql_query(raw_sql: str) -> str:
    """Helper to extract clean SQL from markdown or conversational LLM output."""
    sql_match = re.search(r"```sql\s*(.*?)\s*```", raw_sql, re.DOTALL | re.IGNORECASE)
    if sql_match:
        sql = sql_match.group(1).strip()
    else:
        sql_match_general = re.search(r"```\s*(.*?)\s*```", raw_sql, re.DOTALL)
        if sql_match_general:
            sql = sql_match_general.group(1).strip()
        else:
            sql = raw_sql.strip()

    # Clean leading SQL identifiers
    sql = re.sub(r"^sql\s*", "", sql, flags=re.IGNORECASE).strip()
    # Strip final trailing semicolons
    sql = sql.rstrip(";")
    return sql

def execute_sqlite_query(sql: str) -> tuple[list[str], list[dict], str | None]:
    """Safely execute the SQL query on the local SQLite DB."""
    try:
        if not os.path.exists(DB_PATH):
            return [], [], f"Database file not found at: {DB_PATH}"

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)

        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = [dict(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            columns = ["status"]
            rows = [{"rows_affected": cursor.rowcount}]

        conn.close()
        return columns, rows, None
    except Exception as e:
        return [], [], str(e)

def run_text_to_sql(question: str) -> dict:
    """
    Translates a natural language question to SQLite, executes it, and
    synthesizes a supportive wellness answer.
    """
    # Step 1: Prompt formatting for SQL Generation
    schema_ctx = get_db_schema()
    gen_prompt_str = sql_gen_prompt_template.format(
        schema_context=schema_ctx,
        question=question
    )
    
    # Step 2: Call TinyLlama LLM
    try:
        raw_llm_sql = chat(
            system_prompt="You are a precise SQLite query writer.",
            user_message=gen_prompt_str,
            max_new_tokens=180,
            temperature=0.1
        )
        sql_query = clean_sql_query(raw_llm_sql)
    except Exception as e:
        # Graceful fallback to raw query or string
        sql_query = ""
        error_msg = f"Failed to generate query with LLM: {str(e)}"
        return {
            "query": "N/A",
            "columns": ["error"],
            "rows": [{"message": error_msg}],
            "response": "I had a bit of trouble translating your request. Could you try rephrasing your wellness question?"
        }

    # Step 3: Run SQLite Query
    columns, rows, error = execute_sqlite_query(sql_query)
    
    # Handle DB errors (attempt a clean fallback query if possible)
    if error:
        # Try a keyword-based fallback if it was a basic question
        fallback_query = None
        q_lower = question.lower()
        if "journal" in q_lower:
            fallback_query = "SELECT COUNT(*) as total_entries FROM journal_metadata"
        elif "stress" in q_lower or "mood" in q_lower:
            fallback_query = "SELECT timestamp, stress_level, emotion FROM mood_logs ORDER BY timestamp DESC LIMIT 5"
        
        if fallback_query:
            sql_query = fallback_query
            columns, rows, error = execute_sqlite_query(sql_query)
            
        if error:
            return {
                "query": sql_query or "N/A",
                "columns": ["error"],
                "rows": [{"message": error}],
                "response": "I ran into a database system error while looking up your wellness logs. Let's try again in a moment."
            }

    # Step 4: Synthesize response
    result_summary = str(rows) if rows else "No records found."
    synthesis_prompt_str = synthesis_prompt_template.format(
        question=question,
        query=sql_query,
        result=result_summary
    )

    try:
        synthesis_response = chat(
            system_prompt="You are Trixie AI, a supportive employee wellness advisor.",
            user_message=synthesis_prompt_str,
            max_new_tokens=260,
            temperature=0.5
        )
    except Exception as e:
        synthesis_response = f"I retrieved your wellness logs successfully. The database returned {len(rows)} matching record(s). Keep up the daily check-ins!"

    return {
        "query": sql_query,
        "columns": columns,
        "rows": rows,
        "response": synthesis_response.strip()
    }
