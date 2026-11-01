# E-Commerce Star Schema Data Warehouse Pipeline

An advanced data engineering project demonstrating dimensional modeling, translating flat transactional data into a rigorous **Star Schema** (Fact and Dimension tables) using Python and SQLite.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Data Modeling & Transformation:** Pandas, NumPy
* **Data Warehouse / Storage:** SQLite (Relational Database with Foreign Key constraints)
* **Architecture:** Dimensional Modeling, Star Schema, Custom Logging

---

## 🔄 Pipeline Architecture

1. **Extract & Model (Dimensional Transformation):**
   * Normalizes flat e-commerce transaction logs into normalized tables.
   * **Dimension Tables Created:** `dim_customer`, `dim_product`, and `dim_date` (with extracted calendar attributes like year, month, day, and day of week).
   * **Fact Table Created:** `fact_orders` containing foreign keys and high-level metrics (`quantity_ordered`, `total_revenue`).
2. **Load:**
   * Initializes relational schema definitions with primary and foreign key constraints.
   * Commits the modeled dimensional data securely into the SQLite data warehouse.

---

## 📁 Project File Structure
```text
Ecommerce-Data-Warehouse-Pipeline/
│
├── ecommerce_warehouse.py           # Main star schema modeling and ETL script
├── raw_ecommerce_transactions.csv   # Source transaction dataset
└── README.md                        # Project documentation
