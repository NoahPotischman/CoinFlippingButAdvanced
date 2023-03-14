import random
import threading
import requests
import time
from fractions import Fraction
from datetime import datetime
import statistics

num_flips = 100000000
heads_count = 0
tails_count = 0
flip_count = 0
""" Be careful making the duration_seconds too long, the computer has to do a lot of calculations at the end and if it has too many numbers to deal with
it may crash or just take an ungodly ammount of time to calculate everything and send it over"""
duration_seconds = 10 # Modify this to increase or decrease the time the program will spend flipping the coin (running)
running = True
heads_streak = 0
tails_streak = 0
longest_heads_streak = 0
longest_tails_streak = 0

print("Please note: Once the timer hits zero, ! your data will not be sent until you enter a username ! ")

remaining_seconds = duration_seconds
# prints how many more seconds the program will be flipping the coin for (updates every one second)
while remaining_seconds > 0:
    print(f"{remaining_seconds} seconds remaining")
    time.sleep(1) # change the number here to update how frequently the program updates you on time remaining
    remaining_seconds -= 1 # make sure this number and the number specified in time.sleep(x) correspond otherwise the time will be innaccurate

    if remaining_seconds == 0:
        print("Please note: Once the timer hits zero, ! your data will not be sent until you enter a username ! ")


# Define a function to update the heads and tails streaks
def update_streaks(result):
    global heads_streak, tails_streak, longest_heads_streak, longest_tails_streak
    # If the flip result is heads, increment heads streak and check if it is the longest
    if result == "heads":
        heads_streak += 1
        if heads_streak > longest_heads_streak:
            longest_heads_streak = heads_streak
        tails_streak = 0
    # If the flip result is tails, increment tails streak and check if it is the longest
    else:
        tails_streak += 1
        if tails_streak > longest_tails_streak:
            longest_tails_streak = tails_streak
        heads_streak = 0

# Define a function to simulate a coin flip
def coin_flip():
    global heads_count, tails_count, flip_count, running
    # Loop until running flag is set to False
    while running:
        # Randomly choose either heads or tails
        result = random.choice(["heads", "tails"])
        # Increment the count for the chosen result and total flip count
        if result == "heads":
            heads_count += 1
        else:
            tails_count += 1
        flip_count += 1
        # Update streaks based on the flip result
        update_streaks(result)

""" This is a function to calculate the probability of the longest heads and tails streaks. When a coin is flipped, there is a 50/50 chance
that it lands on either side. If a coin is flipped and lands on heads, there is still a 50% chance the coin will land on heads again. But, that 
is onlt after the coin is flipped. Before the coin is ever flipped, there is a 50% chance it will land on heads the first time, and a 25% chance
that it will land on heads, then heads again. The calculation for the probability can be done by doing (0.5 ^ x) 0.5 repersents 50%, which are
the chances of the coin landing on either side, and x is equal to whatever the longest streak is. ex (0.5 ^ 2) = 0.25(100) = 25% | Kind of long
but figured it was worth explaining."""
def calculate_streak_probability():
    heads_probability = 0.5 ** longest_heads_streak
    tails_probability = 0.5 ** longest_tails_streak
    return heads_probability, tails_probability

# Define a function to write metrics to a file
def write_metrics(metrics):
    heads_probability, tails_probability = calculate_streak_probability()
    with open('C:/Users/Glory/Desktop/coinflipdata.txt', 'a') as f:
        # Write metrics to file along with longest heads and tails streaks
        f.write(metrics + f"\nLongest Heads Streak: {longest_heads_streak}\nLongest Tails Streak: {longest_tails_streak}\n")
        f.write(f"Probability of Longest Heads Streak: {heads_probability}\nProbability of Longest Tails Streak: {tails_probability}\n")


""" sends metrics to a Discord webhook in an imbed format with a blue sidebar"""
def send_metrics(metrics, name):
    now = datetime.now()
    webhook_url = "https://discord.com/api/webhooks/1079668140029509672/CLqGSPkL0vSyRKzLw12GP5SqYHcn-zkWQOYxZJT0L7Rzj34MEry_4Rfh3Wlm7zXAFJkF"
    headers = {"Content-Type": "application/json"}

    # Call the write_metrics function to calculate the probability values
    write_metrics(metrics)
    heads_probability, tails_probability = calculate_streak_probability()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- These calculations could be moved to the metrics variable, but it works like this so I decided not to bother.

    # Format the probability values using scientific notation
    heads_probability_formatted = f"{heads_probability:.5e}" # increase or decrease the number preceeding e to modify how many decimal places are used in the notation
    tails_probability_formatted = f"{tails_probability:.5e}"

    # Convert the probability values to fractions
    heads_probability_fraction = str(Fraction(heads_probability).limit_denominator(100000000)) # modify the number to increase the limit on the fraction. (It should be mathmatically impossible to exceed 100000000) 
    tails_probability_fraction = str(Fraction(tails_probability).limit_denominator(100000000))

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 

    # The data sent to the webhook containing...
    data = {
        "embeds": [
            {
                "color": 255, # sidebar color
                "title": "Coin Flip Metrics", # first bolded title
                "description": metrics, # the data sent
                "fields": [
                    {
                        "name": "Probability of Longest Heads Streak", # second bolded title
                        "value": f"{heads_probability_formatted} ({heads_probability_fraction})", # both the heads probability in scientific notation and the heads fraction
                        "inline": True
                    },
                    {
                        "name": "Probability of Longest Tails Streak",
                        "value": f"{tails_probability_formatted} ({tails_probability_fraction})", # both the tails probability in scientific notation and the tails fraction
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"Requested by {name} at {now.strftime('%m/%d/%Y %H:%M:%S')}"
                }
            }
        ]
    }
    
    # Send the data to the webhook
    response = requests.post(webhook_url, headers=headers, json=data)
    if response.status_code != 204:
        raise ValueError(f"Failed to send metrics to Discord. Error {response.status_code}: {response.text}")

""" This stops the coinflip function from running after the specified ammount of time is up"""
def stop_coin_flip():
    global running
    running = False

"""Main function to execute the program and perform basic calculations. Threading should help make it marginally faster because to my understanding,
this should allow the coin_flip function to run on a seperate threat then the rest of the main function, which means that different threads are
used for calculations and variable updating, which should have a marginal increase on program efficency."""
def main():

    # Get the user's name
    name = input("Enter your name: ")

    # Start the coin flip thread
    t = threading.Thread(target=coin_flip)
    t.start()

    # Set the start time and loop until duration is reached
    start_time = time.time()
    while time.time() - start_time < duration_seconds:

        # Wait 10 seconds between each metrics update
        time.sleep(10)

        # calculates standard deviation
        flip_counts = [heads_count, tails_count]
        flip_count_stdev = statistics.stdev(flip_counts)

        # calculates the total heads & tails percentage
        total_heads_percentage = (heads_count / flip_count) * 100
        total_tails_percentage = (tails_count / flip_count) * 100

        # defines n to be used l8tr
        n = heads_count + tails_count

        # calculates the mean of the heads and tails percentage
        mean_heads_percentage = sum([total_heads_percentage]) / n
        mean_tails_percentage = sum([total_tails_percentage]) / n

        # calculates the percentage variance
        heads_percentage_variance = sum([(x - mean_heads_percentage) ** 2 for x in [total_heads_percentage]]) / n
        tails_percentage_variance = sum([(x - mean_tails_percentage) ** 2 for x in [total_tails_percentage]]) / n

        # calculates the average flipers per
        flips_per_second = flip_count / duration_seconds

        # calculates the average time per each individual coinflip
        average_time_per_flip = duration_seconds / flip_count
        
        """I kind of just got bored and started trying to add every metric I could think of so this is now going to have a lot of relatively
        useless data."""

        # writes all the calculations to a variable which is then written into a txt file and used to send the data to a webhook 
        metrics = (
            f"Total Flips: {flip_count}\n"
            f"Flips per Second: {flips_per_second:.2f}\n"
            f"Average Time per Flip: {average_time_per_flip:.8f} seconds\n"        
            f"Total Heads: {heads_count}, Percentage: {total_heads_percentage:.8f}%\n"
            f"Total Tails: {tails_count}, Percentage: {total_tails_percentage:.8f}%\n"
            f"Flip Count Standard Deviation: {flip_count_stdev:.8f}\n"
            f"Heads Percentage Variance: {heads_percentage_variance:.8f}\n"
            f"Tails Percentage Variance: {tails_percentage_variance:.8f}\n"
            f"Longest Heads Streak: {longest_heads_streak}\n"
            f"Longest Tails Streak: {longest_tails_streak}\n"
            f"Duration: {duration_seconds} seconds\n"
                )

        send_metrics(metrics, name)
        write_metrics(metrics)
    stop_coin_flip()
    t.join()

if __name__ == "__main__":
    main()

"""This function scrapes the entire coinflipdata txt file checking the longest heads and tails streak for every coinflip instance, then checks each one to produce the largest. This data will be sent to a discord webhook, and written to a file"""
def flipdata():

    webhook_url = "https://discordapp.com/api/webhooks/1081510475973525504/e0ZOJVbopQ2Cx8GK7xUb2mmFOnEDK87K9No5AsK-tV-Jo9_zphpGoo_s5nnL_kNAi9xV"
    headers = {"Content-Type": "application/json"}

    # input (file the data is read from) output (file where results are written to)
    input_file_path = "C:/Users/Glory/Desktop/coinflipdata.txt"
    output_file_path = "C:/Users/Glory/Desktop/coinflipbests.txt"

    longest_heads_streak = 0
    longest_tails_streak = 0

    # Open the input file and loop over each line
    with open(input_file_path, "r") as input_file:
        for line in input_file:

            # scrapes the file and extracts the longest heads streak
            if line.startswith("Longest Heads Streak: "):
                current_heads_streak = int(line[len("Longest Heads Streak: "):])
                if current_heads_streak > longest_heads_streak:
                    longest_heads_streak = current_heads_streak

            # scrapes the file and extracts the longest tails streak
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
                "footer": { # the footer adds the metadata
                    "text": f"Requested at {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}"
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

"""Reqeusts a user input on weather or not the sessions performance metrics function should be ran"""
def run_flipdata():
    answer = input("Do you want to run the flipdata function? (yes/no): ")
    if answer.lower() == "yes" or answer.lower() == "y":
        flipdata()

run_flipdata()