# main.py

import os
from datetime import datetime
from db import db_functions
from mailer import email_functions
from utils import excel_utils
from config import (
    INPUT_EXCEL_PATH,
    BASE_OUTPUT_DIR,
    DB_CONNECTION_STRING,
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    BUYER_EMAIL_TABLE,
    PRAKTIS_SEARCH_URL,
    PRAKTIKER_SEARCH_URL,
)


def main():
    # Process the input Excel file and get product data and buyer mappings.
    product_data, buyer_mappings = excel_utils.process_excel_and_split_files(INPUT_EXCEL_PATH)

    # Upsert product data into the ProductDetails table.
    changes = db_functions.upsert_data_to_db(product_data, table_name="ProductDetails")

    # Upsert buyer mappings into the ProductBuyers table.
    db_functions.upsert_product_buyers(buyer_mappings, table_name="ProductBuyers")

    # Get mapping from product pair to buyer codes.
    buyer_mapping_dict = db_functions.get_product_buyers(table_name="ProductBuyers")

    # Get buyer emails (and names) from the BuyerEmails table.
    buyer_email_dict = db_functions.get_buyer_emails(table_name="BuyerEmails")

    # Group product updates by buyer.
    buyer_updates = {}
    for update in changes.get("price_changes", []):
        key = (update["code"], update["praktiker_code"])
        buyers = buyer_mapping_dict.get(key, [])
        for b in buyers:
            buyer_updates.setdefault(b, {"price_changes": [], "new_items": []})
            buyer_updates[b]["price_changes"].append(update)
    for update in changes.get("new_items", []):
        key = (update["Praktis Code"], update["Praktiker Code"])
        buyers = buyer_mapping_dict.get(key, [])
        for b in buyers:
            buyer_updates.setdefault(b, {"price_changes": [], "new_items": []})
            buyer_updates[b]["new_items"].append(update)

    # For each buyer with updates, filter the product data and send an email with a buyer-specific Excel file.
    for buyer_code, updates in buyer_updates.items():
        if updates["price_changes"] or updates["new_items"]:
            filtered_data = excel_utils.filter_product_data_by_buyer(product_data, buyer_code, buyer_mapping_dict)
            buyer_info = buyer_email_dict.get(buyer_code)
            if not buyer_info:
                print(f"No email found for Buyer Code {buyer_code}. Skipping email.")
                continue
            buyer_details = {"buyer_code": buyer_code, "email": buyer_info["email"], "name": buyer_info["name"]}
            # Construct buyer folder name: "First_Last_BuyerCode"
            name_parts = buyer_info["name"].split()
            if len(name_parts) >= 2:
                folder_name = f"{name_parts[0]}_{name_parts[1]}_{buyer_code}"
            else:
                folder_name = f"{buyer_code}"
            buyer_folder = os.path.join(BASE_OUTPUT_DIR, folder_name)
            if not os.path.exists(buyer_folder):
                os.makedirs(buyer_folder)
            # Construct the buyer-specific Excel filename.
            timestamp_excel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            buyer_filename = f"product_details_{buyer_info['name'].replace(' ', '_')}_{timestamp_excel}.xlsx"
            buyer_excel_filepath = os.path.join(buyer_folder, buyer_filename)
            # Write the filtered Excel file.
            excel_utils.write_filtered_excel(buyer_excel_filepath, filtered_data, buyer_details)
            # Build the HTML email body using only the filtered changes and filtered product data.
            email_body = excel_utils.format_email_body_table_html(updates, filtered_data)
            subject = f"Price Comparison Report for {buyer_info['name']} (Changes Detected)"
            email_functions.send_email(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, [buyer_info["email"]],
                                       subject, email_body, buyer_excel_filepath)
        else:
            print(f"No updates for Buyer Code {buyer_code}. No email sent.")


if __name__ == "__main__":
    main()
