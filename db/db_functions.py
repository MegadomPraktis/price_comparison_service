# db/db_functions.py

import pyodbc
from datetime import datetime
from config import DB_CONNECTION_STRING

def upsert_data_to_db(data, table_name="ProductDetails"):
    """
    Upserts product records into the SQL Server table.
    Returns a changes dictionary with keys "new_items" and "price_changes".
    """
    changes = {"new_items": [], "price_changes": []}
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        create_table_sql = f"""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
        BEGIN
            CREATE TABLE [{table_name}] (
                [Praktis Code] NVARCHAR(255) PRIMARY KEY,
                [Praktiker Code] NVARCHAR(255),
                [Praktis Name] NVARCHAR(255),
                [Praktiker Name] NVARCHAR(255),
                [Praktis Regular Price] NVARCHAR(255),
                [Praktiker Regular Price] NVARCHAR(255),
                [Praktis Promo Price] NVARCHAR(255),
                [Praktiker Promo Price] NVARCHAR(255),
                [RunTimestamp] DATETIME
            )
        END
        """
        cursor.execute(create_table_sql)
        conn.commit()
        for row in data:
            praktis_code = str(row.get("Praktis Code", ""))
            praktiker_code = str(row.get("Praktiker Code", ""))
            current_timestamp = datetime.now()
            select_sql = f"""
                SELECT [Praktis Regular Price], [Praktiker Regular Price],
                       [Praktis Promo Price], [Praktiker Promo Price]
                FROM [{table_name}]
                WHERE [Praktis Code] = ?
            """
            cursor.execute(select_sql, praktis_code)
            existing = cursor.fetchone()
            if existing is None:
                insert_sql = f"""
                    INSERT INTO [{table_name}]
                    ([Praktis Code], [Praktiker Code], [Praktis Name], [Praktiker Name],
                     [Praktis Regular Price], [Praktiker Regular Price],
                     [Praktis Promo Price], [Praktiker Promo Price], [RunTimestamp])
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_sql,
                    praktis_code,
                    praktiker_code,
                    str(row.get("Praktis Name", "")),
                    str(row.get("Praktiker Name", "")),
                    str(row.get("Praktis Regular Price", "")),
                    str(row.get("Praktiker Regular Price", "")),
                    str(row.get("Praktis Promo Price", "")),
                    str(row.get("Praktiker Promo Price", "")),
                    current_timestamp
                )
                changes["new_items"].append({"Praktis Code": praktis_code, "Praktiker Code": praktiker_code})
            else:
                old_praktis_price = str(existing[0])
                old_praktiker_price = str(existing[1])
                old_praktis_promo = str(existing[2])
                old_praktiker_promo = str(existing[3])
                new_praktis_price = str(row.get("Praktis Regular Price", ""))
                new_praktiker_price = str(row.get("Praktiker Regular Price", ""))
                new_praktis_promo = str(row.get("Praktis Promo Price", ""))
                new_praktiker_promo = str(row.get("Praktiker Promo Price", ""))
                if (old_praktis_price != new_praktis_price or
                    old_praktiker_price != new_praktiker_price or
                    old_praktis_promo != new_praktis_promo or
                    old_praktiker_promo != new_praktiker_promo):
                    changes["price_changes"].append({
                        "code": praktis_code,
                        "praktiker_code": praktiker_code,
                        "praktis_old_price": old_praktis_price,
                        "praktis_new_price": new_praktis_price,
                        "praktiker_old_price": old_praktiker_price,
                        "praktiker_new_price": new_praktiker_price
                    })
                update_sql = f"""
                    UPDATE [{table_name}]
                    SET [Praktiker Code] = ?,
                        [Praktis Name] = ?,
                        [Praktiker Name] = ?,
                        [Praktis Regular Price] = ?,
                        [Praktiker Regular Price] = ?,
                        [Praktis Promo Price] = ?,
                        [Praktiker Promo Price] = ?,
                        [RunTimestamp] = ?
                    WHERE [Praktis Code] = ?
                """
                cursor.execute(update_sql,
                    praktiker_code,
                    str(row.get("Praktis Name", "")),
                    str(row.get("Praktiker Name", "")),
                    new_praktis_price,
                    new_praktiker_price,
                    new_praktis_promo,
                    new_praktiker_promo,
                    current_timestamp,
                    praktis_code
                )
        conn.commit()
        print(f"Data upserted to table '{table_name}' successfully.")
        return changes
    except Exception as e:
        print(f"Error saving data to table '{table_name}': {e}")
        return changes
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

def upsert_product_buyers(buyer_mappings, table_name="ProductBuyers"):
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        create_table_sql = f"""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
        BEGIN
            CREATE TABLE [{table_name}] (
                [Praktis Code] NVARCHAR(255),
                [Praktiker Code] NVARCHAR(255),
                [Buyer Code] NVARCHAR(255),
                PRIMARY KEY ([Praktis Code], [Praktiker Code], [Buyer Code])
            )
        END
        """
        cursor.execute(create_table_sql)
        conn.commit()
        for mapping in buyer_mappings:
            praktis_code = mapping["Praktis Code"]
            praktiker_code = mapping["Praktiker Code"]
            buyer_code = mapping["Buyer Code"]
            select_sql = f"SELECT COUNT(*) FROM [{table_name}] WHERE [Praktis Code] = ? AND [Praktiker Code] = ? AND [Buyer Code] = ?"
            cursor.execute(select_sql, praktis_code, praktiker_code, buyer_code)
            count = cursor.fetchone()[0]
            if count == 0:
                insert_sql = f"INSERT INTO [{table_name}] ([Praktis Code], [Praktiker Code], [Buyer Code]) VALUES (?, ?, ?)"
                cursor.execute(insert_sql, praktis_code, praktiker_code, buyer_code)
        conn.commit()
        print("Product buyer mappings upserted successfully.")
    except Exception as e:
        print("Error upserting product buyers:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

def get_product_buyers(table_name="ProductBuyers"):
    mapping = {}
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        select_sql = f"SELECT [Praktis Code], [Praktiker Code], [Buyer Code] FROM [{table_name}]"
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        for row in rows:
            key = (row[0], row[1])
            mapping.setdefault(key, []).append(row[2])
    except Exception as e:
        print("Error getting product buyers:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
    return mapping

def get_buyer_emails(table_name="BuyerEmails"):
    emails = {}
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        create_table_sql = f"""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
        BEGIN
            CREATE TABLE [{table_name}] (
                [Buyer Code] NVARCHAR(255) PRIMARY KEY,
                [Email] NVARCHAR(255),
                [Buyer Name] NVARCHAR(255)
            )
        END
        """
        cursor.execute(create_table_sql)
        conn.commit()
        select_sql = f"SELECT [Buyer Code], [Email], [Buyer Name] FROM [{table_name}]"
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        for row in rows:
            emails[row[0]] = {"email": row[1], "name": row[2]}
    except Exception as e:
        print("Error getting buyer emails:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
    return emails
