import csv


def save_to_csv(data, filename='products.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            data['marketplace'],
            data['product_name'],
            data['product_url'],
            data['price'],
            data['date']
        ])
