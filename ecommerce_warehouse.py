import logging
import pandas as pd
import sqlite3

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ECommerceWarehousePipeline:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect_db(self):
        """Establish connection to the SQLite Data Warehouse."""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to E-Commerce Warehouse: {self.db_name}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def build_star_schema(self, csv_file_path):
        """Extract raw data and model it into Star Schema (Fact & Dimensions)."""
        logger.info(f"Extracting and modeling star schema from {csv_file_path}")
        try:
            df = pd.read_csv(csv_file_path)
            
            # --- 1. CREATE DIMENSION TABLES ---
            
            # Dimension: Customers
            dim_customer = df[['customer_id', 'customer_name', 'customer_city']].drop_duplicates().reset_index(drop=True)
            
            # Dimension: Products
            dim_product = df[['product_id', 'product_name', 'category', 'unit_price']].drop_duplicates().reset_index(drop=True)
            
            # Dimension: Date
            df['order_date'] = pd.to_datetime(df['order_date'])
            dim_date = pd.DataFrame({
                'date_id': df['order_date'].dt.strftime('%Y%m%d').astype(int),
                'full_date': df['order_date'].dt.strftime('%Y-%m-%d'),
                'year': df['order_date'].dt.year,
                'month': df['order_date'].dt.month,
                'day': df['order_date'].dt.day,
                'day_of_week': df['order_date'].dt.day_name()
            }).drop_duplicates().reset_index(drop=True)
            
            # --- 2. CREATE FACT TABLE ---
            fact_orders = pd.DataFrame({
                'order_id': df['order_id'],
                'customer_id': df['customer_id'],
                'product_id': df['product_id'],
                'date_id': df['order_date'].dt.strftime('%Y%m%d').astype(int),
                'quantity_ordered': df['quantity'],
                'total_revenue': df['quantity'] * df['unit_price']
            })

            return dim_customer, dim_product, dim_date, fact_orders

        except Exception as e:
            logger.error(f"Failed to model star schema: {e}")
            raise

    def load_warehouse(self, dim_customer, dim_product, dim_date, fact_orders):
        """Load the Fact and Dimension tables into SQLite Data Warehouse."""
        logger.info("LOAD: Writing Star Schema tables into database.")
        try:
            # Create tables with foreign key relationships
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS dim_customer (
                    customer_id INTEGER PRIMARY KEY,
                    customer_name TEXT,
                    customer_city TEXT
                );

                CREATE TABLE IF NOT EXISTS dim_product (
                    product_id INTEGER PRIMARY KEY,
                    product_name TEXT,
                    category TEXT,
                    unit_price REAL
                );

                CREATE TABLE IF NOT EXISTS dim_date (
                    date_id INTEGER PRIMARY KEY,
                    full_date TEXT,
                    year INTEGER,
                    month INTEGER,
                    day INTEGER,
                    day_of_week TEXT
                );

                CREATE TABLE IF NOT EXISTS fact_orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    product_id INTEGER,
                    date_id INTEGER,
                    quantity_ordered INTEGER,
                    total_revenue REAL,
                    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
                    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
                    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
                );
            """)

            # Load DataFrames into SQLite tables
            dim_customer.to_sql('dim_customer', self.connection, if_exists='replace', index=False)
            dim_product.to_sql('dim_product', self.connection, if_exists='replace', index=False)
            dim_date.to_sql('dim_date', self.connection, if_exists='replace', index=False)
            fact_orders.to_sql('fact_orders', self.connection, if_exists='replace', index=False)

            self.connection.commit()
            logger.info("LOAD Complete: Star Schema warehouse tables successfully populated.")

        except Exception as e:
            logger.error(f"Error loading warehouse tables: {e}")
            self.connection.rollback()
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    db_file = 'ecommerce_warehouse.db'
    
    # Create sample raw e-commerce dataset for testing
    dummy_csv = 'raw_ecommerce_transactions.csv'
    sample_df = pd.DataFrame({
        'order_id': [1001, 1002, 1003, 1004],
        'customer_id': [501, 502, 501, 503],
        'customer_name': ['Aarav Sharma', 'Priya Patel', 'Aarav Sharma', 'Rohan Verma'],
        'customer_city': ['Pune', 'Mumbai', 'Pune', 'Delhi'],
        'product_id': [201, 202, 203, 201],
        'product_name': ['Wireless Mouse', 'Mechanical Keyboard', 'HD Monitor', 'Wireless Mouse'],
        'category': ['Accessories', 'Accessories', 'Electronics', 'Accessories'],
        'unit_price': [799.0, 2499.0, 11999.0, 799.0],
        'quantity': [2, 1, 1, 3],
        'order_date': ['2026-06-01', '2026-06-01', '2026-06-02', '2026-06-03']
    })
    sample_df.to_csv(dummy_csv, index=False)

    pipeline = ECommerceWarehousePipeline(db_file)
    try:
        pipeline.connect_db()
        c_dim, p_dim, d_dim, f_orders = pipeline.build_star_schema(dummy_csv)
        pipeline.load_warehouse(c_dim, p_dim, d_dim, f_orders)
    except Exception as e:
        logger.error(f"Pipeline Failed: {e}")
    finally:
        pipeline.close()