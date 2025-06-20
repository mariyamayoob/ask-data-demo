# AskData - DB Agnostic Design

**Natural language to SQL with enterprise analytics dashboard**

Transform business questions into database insights. Built for enterprise deployment with any database.

## What It Does

- **Business users** ask questions in plain English
- **AI generates** optimized SQL queries  
- **Get instant results** with performance analytics
- **Deploy on any database in minutes.** Just update environment variables, schema metadata, and domain config - the AI automatically learns your database structure and domain. **Works with MySQL, PostgreSQL, SQLite, and any SQLAlchemy-supported database without code changes.**


**Example:** *"Show customers with declining engagement"* → Generates complex SQL with joins → Returns formatted results

## Real Example

**Input:** *"Show me all customer details for urgent transfers over 10k for investment"*

**Generated SQL:**
```sql
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS full_name,
    c.phone_number,
    c.email,
    c.address_line1,
    c.address_line2,
    c.city,
    c.state,
    c.postal_code,
    c.country,
    c.customer_type,
    c.customer_status,
    c.kyc_status
FROM 
    customers c
JOIN 
    account_holders ah ON c.customer_id = ah.customer_id
JOIN 
    payment_instructions pi ON (ah.account_id = pi.payer_account_id OR ah.account_id = pi.payee_account_id)
WHERE 
    pi.priority = 'URGENT'
    AND pi.amount > 10000
    AND pi.payment_purpose LIKE '%investment%'
    AND pi.instruction_status = 'COMPLETED';
```

**AI automatically:**
- Selected 3 relevant tables from 12 available
- Used proper ENUM values (`URGENT`, `COMPLETED`)
- Applied name concatenation hint from schema
- Handled OR logic for payer/payee accounts
- Added text search for "investment" in purpose field

## Tech Stack

**Backend:** Python FastAPI + Azure OpenAI + SQLAlchemy  
**Frontend:** Streamlit dashboard with real-time analytics  
**Deployment:** Docker containers with health monitoring  

## Key Features

- **Smart Query Generation** - AI selects tables and generates SQL
- **Enterprise Dashboard** - Usage analytics and performance tracking  
- **Database Agnostic** - MySQL, PostgreSQL, SQLite support
- **Security First** - Read-only access with query validation

## For Development Teams

### Quick Setup
```bash
# 1. Clone and run
git clone <repo>
docker-compose up

# 2. Access at http://localhost:8501
```

### Use With Different Database

**Only 3 files to change:**

**1. Backend Environment (`.env`)**
```bash
# Switch database type
DATABASE_TYPE=postgresql  # or mysql, sqlite
DATABASE_HOST=your-host
DATABASE_USER=your-user
DATABASE_PASSWORD=your-password
DATABASE_NAME=your-database

# Keep Azure OpenAI config
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
```

**2. Schema Definition (`schema_metadata.json`)**
```json
{
  "your_table": {
    "description": "What this table contains",
    "keywords": ["search", "terms"],
    "columns": {
      "column_name": {
        "type": "VARCHAR(50)",
        "description": "Column purpose"
      }
    }
  }
}
```

**3. Business Config (`system_config.json`)**
```json
{
  "default_tables": {
    "emergency_fallback": ["your_main_tables"]
  },
  "test_questions": {
    "basic": ["Questions users will ask"]
  }
}
```

**That's it.** The system automatically adapts to your database structure and business domain.

## Production Ready

- **Docker deployment** with health checks
- **Environment-based config** for dev/staging/prod
- **Built-in monitoring** and error tracking
- **Horizontal scaling** ready

## Architecture Decisions

**Azure OpenAI:** Enterprise compliance + consistent performance  
**FastAPI:** High performance async with auto docs  
**SQLAlchemy:** Database agnostic ORM  
**Docker:** Consistent deployment across environments  

---

**Skills Demonstrated:** Full-stack Python, AI/LLM integration, Enterprise architecture, Docker deployment