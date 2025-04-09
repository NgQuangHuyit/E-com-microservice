import csv
import datetime
import json
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Create the CSV file for product features
with open('product_features.csv', 'w', newline='') as csvfile:
    fieldnames = ['product_id', 'features', 'updated_at']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    # Write data for each product
    features_data = [
        # Books
        {
            "product_id": "67e3589ca21f190a6fad92c7",
            "features": {
                "type": "Book",
                "category": "book",
                "author": "reter",
                "publisher": "3242",
                "price_range": "low"
            }
        },
        {
            "product_id": "67ed791ee1d9088051060a7d",
            "features": {
                "type": "Book",
                "category": "book",
                "author": "author a",
                "publisher": "kim dong",
                "price_range": "low"
            }
        },
        {
            "product_id": "67ed792fe1d9088051060a7e",
            "features": {
                "type": "Book",
                "category": "book",
                "author": "author sadf",
                "publisher": "kim dong",
                "price_range": "medium"
            }
        },
        {
            "product_id": "67ed7934e1d9088051060a7f",
            "features": {
                "type": "Book",
                "category": "book",
                "author": "author sadf",
                "publisher": "kim dong",
                "price_range": "medium"
            }
        },
        {
            "product_id": "67ed7939e1d9088051060a80",
            "features": {
                "type": "Book",
                "category": "book",
                "author": "author sadf",
                "publisher": "kim dong",
                "price_range": "medium"
            }
        },
        {
            "product_id": "67ed7947e1d9088051060a81",
            "features": {
                "type": "Book",
                "category": "story",
                "author": "author asdfe",
                "publisher": "kim dong",
                "price_range": "medium"
            }
        },
        # Laptops
        {
            "product_id": "67ed79e3e1d9088051060a82",
            "features": {
                "type": "Laptop",
                "category": "tech",
                "brand": "mac",
                "ram": 16,
                "price_range": "high"
            }
        },
        {
            "product_id": "67ed7a07e1d9088051060a83",
            "features": {
                "type": "Laptop",
                "category": "tech",
                "brand": "lenovo",
                "ram": 8,
                "price_range": "high"
            }
        },
        {
            "product_id": "67ed7a19e1d9088051060a84",
            "features": {
                "type": "Laptop",
                "category": "tech",
                "brand": "lenovo",
                "ram": 8,
                "price_range": "medium"
            }
        },
        {
            "product_id": "67ed7a34e1d9088051060a85",
            "features": {
                "type": "Laptop",
                "category": "tech",
                "brand": "lenovo",
                "ram": 8,
                "price_range": "medium"
            }
        }
    ]

    for feature in features_data:
        writer.writerow({
            'product_id': feature['product_id'],
            'features': json.dumps(feature['features']),  # Properly JSON encode the features
            'updated_at': now  # Add the updated_at field
        })

print("Created product_features.csv")