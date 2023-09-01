import csv
import os
import json
import datetime

time = datetime.datetime.now()

def export_csv(posts, need):
    # Create the directory if it doesn't exist
    output_dir = 'csv-outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"output-{need}.csv")

    # Open the file in write mode
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['need', 'title', 'body', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # Writes the headers
        for post in posts:
            # Writes a row in the CSV file. 'body' corresponds to 'selftext' in the original data
            writer.writerow({'need': post['need'], 'title': post['title'], 'body': post['selftext'], 'score': post['score']})


def export_json(posts):
    # Create the directory if it doesn't exist
    output_dir = 'json-outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"all-outputs-{time}.json")

    # If the file exists, load its contents, otherwise start with an empty list
    if os.path.exists(output_file):
        with open(output_file, 'r') as jsonFile:
            existing_posts = json.load(jsonFile)
    else:
        existing_posts = []

    # Create new dictionaries in the required format and append them to the list
    for post in posts:
        new_post = {
            "experimentId": "redditExperimentId",
            "sortIndex": len(existing_posts),
            "variableValues": {
                "need": post["need"],
                "title": post["title"],
                "body": post["selftext"],
                "score": post["score"],
            },
        }
        existing_posts.append(new_post)

    # Convert the updated list of dictionaries to a JSON string
    json_str = json.dumps(existing_posts, indent=2)  # 'indent=2' pretty-prints the JSON

    # Open the file in write mode and write the JSON string to it
    with open(output_file, 'w') as jsonFile:
        jsonFile.write(json_str)

