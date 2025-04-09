import csv
import random
from datetime import datetime, timedelta


# Generate a random timestamp within the last 30 days
def random_timestamp():
    now = datetime.now()
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    return (now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')


# Available interaction types
interaction_types = ['view', 'cart', 'purchase']

# Available customer IDs
customer_ids = [1, 2, 3, 4, 5]

# Available product IDs
product_ids = [
    "67e3589ca21f190a6fad92c7", "67ed791ee1d9088051060a7d", "67ed792fe1d9088051060a7e",
    "67ed7934e1d9088051060a7f", "67ed7939e1d9088051060a80", "67ed7947e1d9088051060a81",
    "67ed79e3e1d9088051060a82", "67ed7a07e1d9088051060a83", "67ed7a19e1d9088051060a84",
    "67ed7a34e1d9088051060a85"
]

# Create interaction patterns - views are more common than cart adds, which are more common than purchases
interactions = []
interaction_id = 1

# For each customer, generate multiple interactions
for customer_id in customer_ids:
    # Determine how many products this user interacted with
    products_interacted = random.sample(product_ids, random.randint(3, len(product_ids)))

    for product_id in products_interacted:
        # Every product viewed
        interactions.append({
            'id': interaction_id,
            'user_id': customer_id,
            'product_id': product_id,
            'interaction_type': 'view',
            'timestamp': random_timestamp()
        })
        interaction_id += 1

        # 70% chance of adding to cart
        if random.random() < 0.7:
            interactions.append({
                'id': interaction_id,
                'user_id': customer_id,
                'product_id': product_id,
                'interaction_type': 'cart',
                'timestamp': random_timestamp()
            })
            interaction_id += 1

            # 50% chance of purchase after adding to cart
            if random.random() < 0.5:
                interactions.append({
                    'id': interaction_id,
                    'user_id': customer_id,
                    'product_id': product_id,
                    'interaction_type': 'purchase',
                    'timestamp': random_timestamp()
                })
                interaction_id += 1

# Add some extra random interactions to make the data more realistic
for _ in range(50):
    interactions.append({
        'id': interaction_id,
        'user_id': random.choice(customer_ids),
        'product_id': random.choice(product_ids),
        'interaction_type': random.choice(interaction_types),
        'timestamp': random_timestamp()
    })
    interaction_id += 1

# Write interactions to CSV
with open('user_interactions.csv', 'w', newline='') as csvfile:
    fieldnames = ['id', 'user_id', 'product_id', 'interaction_type', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for interaction in interactions:
        writer.writerow(interaction)

print(f"Generated {len(interactions)} interactions in user_interactions.csv")