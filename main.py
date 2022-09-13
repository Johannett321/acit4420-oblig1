# -------- IMPORTS -------- #
import os
import json
import time
import string
import random
import urllib.request
from datetime import datetime
from pathlib import Path

# -------- GLOBALS -------- #
version = '1.0'

# Stored plans
plans = {}
available_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Working directory and savefile path
workdir = os.getcwd() + os.path.sep + "CodePlans"
file_path = workdir + os.path.sep + 'MainPlans.json'

# -------- MAIN -------- #
print()
print('--------------------------------------')
print('      Welcome to CodePlans ' + version)
print('--------------------------------------')
print()
time.sleep(1)


# When first starting the program.
def startup():
    # Check if the workdir has any previously stored plans.
    if Path(file_path).exists():
        def found_plans():
            print("CodePlans automatically found some saved plans. Would you like to load them? (y/n)")
            preload_plans = input()
            if preload_plans == 'y':
                load_plans(allow_filename_change=False)
            elif preload_plans == 'n':
                print("Okay. No problem!")
            else:
                print("Please type either y or n.")
                found_plans()
                return

        found_plans()
    show_menu()


# Show the main menu
def show_menu():
    print()
    print("------------ MAIN MENU ------------")
    menu_options = ("1) Load plans from savefile", "2) Add a plan to your plans",
                    "3) Show plans for a day", "4) Show all plans for all days",
                    "5) Save all plans", "6) Download an example plan", "7) Where am i?", "8) Exit CodePlans")
    for option in menu_options:
        print(option)

    print("Choose option:", end=" ")
    chosen_menu_option = input().lower()
    print("-----------------------------------")

    # Process the user input. Which menu option did the user choose?
    if chosen_menu_option == '1':
        load_plans()
    elif chosen_menu_option == '2':
        add_plan()
    elif chosen_menu_option == '3':
        show_plans()
    elif chosen_menu_option == '4':
        show_all_plans()
    elif chosen_menu_option == '5':
        save_plans()
    elif chosen_menu_option == '6':
        download_example_plan()
    elif chosen_menu_option == '7':
        # Print working directory
        print("Your working directory (the folder where the plans are saved) is at: " + workdir)
        show_how_to_exit()
    elif chosen_menu_option == '8' or chosen_menu_option == 'exit':
        # Close the application
        print("Bye!")
        time.sleep(1)
        print('--------------------------------------')
        exit(0)
    else:
        print('"' + chosen_menu_option + '"' + " is not listed as an option." +
              "Please type the digit in front of the menu option you want. For example '3'")

    # Show the menu again after a process is done
    show_menu()


# Show all plans for a specific day
def show_plans():
    # What day?
    print("What day would you like to see?")
    what_day = input().lower()

    # Check if the day submitted by the user is a real day
    if what_day not in available_days:
        print(what_day + " is not a day!")
        show_plans()
        return

    # Does the plans dictionary contain that day? If not,
    # there are no plans for that day.
    if what_day in plans:
        print("Plans for " + what_day + ":")
        for plan in plans[what_day]:
            print(plans[what_day][plan]['start_time'] + ' - ' + plans[what_day][plan]['end_time'] + ' ' +
                  plans[what_day][plan]['title'])
    else:
        print(what_day + " has no plans")

    show_how_to_exit()


# Show all plans for all days
def show_all_plans():
    print("------- THIS WEEKS SCHEDULE -------")
    for day in available_days:
        print(day + ":")
        # If the day has plans: print them, if not: print no plans
        if day in plans.keys():
            # Get the time millis of the item
            def get_time_as_millis(item):
                # Time is valid
                time_str = '2022-01-01 ' + item[1]["start_time"] + ":00"
                time_format = '%Y-%m-%d %H:%M:%S'
                return datetime.strptime(time_str, time_format).timestamp()*1000

            # Sort and print the plan in the correct order
            for plan in sorted(plans[day].items(), key=get_time_as_millis, reverse=False):
                print(f'    {plan[1]["start_time"]} - {plan[1]["end_time"]} {plan[1]["title"]}')
        else:
            print('    --No plans--')
    show_how_to_exit()


# Populate the plans dictionary if there are any stored plans
def load_plans(allow_filename_change=True):
    # Should we allow a custom filename?
    if allow_filename_change:
        ask_user_for_custom_file_name()

    global plans
    loaded_plans = load_plans_file()
    if loaded_plans is not None:
        plans = loaded_plans


# Loads plans from filepath
def load_plans_file():
    try:
        # Does the file exist?
        my_file = open(file_path, "r")
        plans_txt = my_file.read()

        try:
            my_file.close()
            # Can the JSON data stored in the file be parsed to the 'plans' dict?
            parsed_json = json.loads(plans_txt)
            print("Plans loaded!")
            time.sleep(1)
            return parsed_json
        except:
            print("Could not parse JSON")
    except:
        print(f"Could not find the plans file: '{file_path}'. Does the program "
              f"have reading permission to this directory, and does the file exist?")
    time.sleep(1)

    return None


# Add a plan to plans dict
def add_plan():
    # Ask user for day
    print("Which day would you like to add a plan to?")
    day = input().lower()

    # Let user exit to main menu
    if day == 'exit':
        return

    # Check if the day submitted by the user is a real day
    if day not in available_days:
        print(day + " is not a day!")
        add_plan()
        return

    # Ask for a time, and check if it's a real time
    def ask_for_time(line_to_print):
        print(line_to_print)
        chosen_time = input()
        if not time_is_valid(chosen_time):
            print(chosen_time + " is not a time")
            return ask_for_time(line_to_print)
        return chosen_time

    # Ask for event start/end time
    start_time = ask_for_time("When does it start? (e.g. 15:30)")
    end_time = ask_for_time("When does it end? (e.g. 15:30)")

    # Ask for the plan
    print("What is the plan?")
    the_plan = input()

    # Does the dictionary contain the day? If not, add it
    if day not in plans:
        plans[day] = {}
    plans[day][id_generator()] = {'start_time': start_time, 'end_time': end_time, 'title': the_plan}

    print("Plan added!")
    time.sleep(1)


# Generate a random ID for the plan
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Did the user submit a real time?
def time_is_valid(time_str: str):
    try:
        # Time is valid
        time_str = '2022-01-01 ' + time_str + ":00"
        time_format = '%Y-%m-%d %H:%M:%S'
        datetime.strptime(time_str, time_format)
        return True
    except:
        # Time is not valid
        return False


# Ask user for custom name of file
def ask_user_for_custom_file_name():
    print("Name of file (without file extension)? Just press enter for main plans file")
    wanted_file_name = input()
    global file_path
    # If user specifies filename: use it, if not: use default
    if wanted_file_name != "":
        file_path = workdir + os.path.sep + wanted_file_name + ".json"
    else:
        file_path = workdir + os.path.sep + 'MainPlans.json'


# Store the plans dict in the filepath
def save_plans():
    # Check if there are any plans at all in the dictionary
    if plans == {} or plans is None:
        print("There are no plans to save")
        return

    # Custom file name or default?
    ask_user_for_custom_file_name()

    # Save the plans dict to the filepath
    try:
        plans_as_json = json.dumps(plans)
        if write_to_file(file_path, plans_as_json):
            print("Plans saved!")
        else:
            print("Failed to save plans")
    except:
        print("Could not save plans. Does the program have write permission to the following path: " + workdir + "?")
    time.sleep(1)


def write_to_file(custom_file_path, content):
    # Create the workdir if it does not exist
    if not os.path.exists(workdir):
        os.makedirs(workdir)

    try:
        my_file = open(custom_file_path, "w")
        my_file.write(content)
        my_file.close()
        return True
    except:
        return False


# Don't show the menu before the user is done reading
def show_how_to_exit():
    print("[Press enter to exit]", end="")
    input()


# Download the example plan, and load it
def download_example_plan():
    example_plan_url = 'https://github.com/Johannett321/acit4420-oblig1/blob/main/CodePlans/ExamplePlans.json?raw=true'

    # Download example plan
    print("Downloading example plan...")
    response = urllib.request.urlopen(example_plan_url)
    data = response.read()
    text = data.decode('utf-8')
    write_to_file(workdir + os.path.sep + "ExamplePlan.json", text)
    print("Example plan downloaded! Loading the plan...")
    time.sleep(2)

    # Load exampleplan
    global file_path
    file_path = workdir + os.path.sep + 'ExamplePlan.json'
    load_plans(False)

    show_how_to_exit()

# Start the program
startup()
