# query_metrics.py

from pymongo import MongoClient
import argparse
from tabulate import tabulate

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["ad_analytics"]
collection = db["campaign_metrics"]

# CLI argument parser
parser = argparse.ArgumentParser(description="Query ad campaign metrics from MongoDB.")
parser.add_argument("--campaign", type=str, help="Campaign ID")
parser.add_argument("--ad", type=str, help="Ad ID")

args = parser.parse_args()

query = {}
if args.campaign:
    query["campaign_id"] = args.campaign
if args.ad:
    query["ad_id"] = args.ad

results = list(collection.find(query, {"_id": 0}))

if not results:
    print("❌ No matching results found.")
else:
    print("✅ Matching Results:")
    print(tabulate(results, headers="keys", tablefmt="grid"))
