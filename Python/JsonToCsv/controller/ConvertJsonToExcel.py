import json
import csv

with open('output.json', 'r') as f:
    data = json.load(f)


with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    writer.writerow(["Service", "BlendedCost (USD)"])


    for group in data["ResultsByTime"][0]["Groups"]:
        service_name = group["Keys"][0]  
        cost = group["Metrics"]["BlendedCost"]["Amount"]  
        writer.writerow([service_name, cost])  

print("Conversion completed! File saved as 'output.csv'")
