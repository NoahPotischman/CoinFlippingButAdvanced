import requests
import datetime

# Define the webhook URL and headers
webhook_url = "https://discordapp.com/api/webhooks/1081510475973525504/e0ZOJVbopQ2Cx8GK7xUb2mmFOnEDK87K9No5AsK-tV-Jo9_zphpGoo_s5nnL_kNAi9xV"
headers = {"Content-Type": "application/json"}

# Define the path to the input and output files
input_file_path = "C:/Users/Glory/Desktop/coinflipdata.txt"
output_file_path = "C:/Users/Glory/Desktop/coinflipbests.txt"

# Initialize variables
longest_heads_streak = 0
longest_tails_streak = 0

# Open the input file and loop over each line
with open(input_file_path, "r") as input_file:
    for line in input_file:
        # Extract the longest heads and tails streaks from the line
        if line.startswith("Longest Heads Streak: "):
            current_heads_streak = int(line[len("Longest Heads Streak: "):])
            if current_heads_streak > longest_heads_streak:
                longest_heads_streak = current_heads_streak
        elif line.startswith("Longest Tails Streak: "):
            current_tails_streak = int(line[len("Longest Tails Streak: "):])
            if current_tails_streak > longest_tails_streak:
                longest_tails_streak = current_tails_streak

# Construct the message to send to the webhook
message = {
    "embeds": [
        {
            "title": "Coinflip Bests",
            "description": f"The longest Heads streak from the most recent session is: {longest_heads_streak}\n"
                           f"The longest Tails streak from the most recent session is: {longest_tails_streak}",
            "color": 13632027,
            "footer": {
                "text": f"Requested at {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}"
            }
        }
    ]
}

# Send the message to the webhook
response = requests.post(webhook_url, headers=headers, json=message)
print(f"Webhook Response: {response.status_code}")

# Write the message to the output file
with open(output_file_path, "w") as output_file:
    output_file.write(message["embeds"][0]["description"])
