# -------- IMPORTS -------- #
import os
import json
import time
import string
import random
import urllib.request
from datetime import datetime
from pathlib import Path

# -------- GLOBAL VARIABLES -------- #
_version = '1.2'

# Stored plans
plans = {}
_available_days = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

# Working directory and savefile path
workdir = os.getcwd() + os.path.sep + "CodePlans"
file_path = workdir + os.path.sep + 'MainPlans.json'


# -------- FUNCTIONS -------- #
def show_welcome_message():
    bar = [
        "=--=--=--=--=--=--=--=--=--=--=--=--=--=",
        "-=--=--=--=--=--=--=--=--=--=--=--=--=--",
        "--=--=--=--=--=--=--=--=--=--=--=--=--=-"
    ]

    credz = [
        "",
        "      Made by Johan Svartdal",
        "      Made by Johan Svartdal",
        "      Made by Johan Svartdal",
        "",
        "",
        ""
    ]

    # Play welcome animation for 4 seconds
    start_time = time.time()
    i = 0
    while time.time() < start_time + 4:
        clear()
        print(bar[i % len(bar)])
        print('      Welcome to CodePlans ' + _version)
        print(credz[i % len(credz)])
        print(bar[i % len(bar)])
        time.sleep(.2)
        i += 1
    clear()


# When first starting the program.
def startup():
    # Display welcome message
    show_welcome_message()

    # Check if the workdir has any previously stored plans.
    if Path(file_path).exists():
        def found_plans():
            print("CodePlans automatically found some saved plans.")
            print("Would you like to load them? (y/n)")
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
    # Clear console
    clear()

    print("------------ MAIN MENU ------------")
    # Menu options
    menu_options = ("1) Load plans from savefile", "2) Add an event to your plans",
                    "3) Edit an event", "4) Show plans for a day", "5) Show all events for all days",
                    "6) Save all plans", "7) Download an example plan", "8) Where am I?", "9) Exit CodePlans")
    # Print menu options
    for option in menu_options:
        print(option)

    # Get user input
    print("Choose option:", end=" ")
    chosen_menu_option = input().lower()
    clear()

    # Process the user input. Which menu option did the user choose?
    if chosen_menu_option == '1':
        load_plans()  # Load
    elif chosen_menu_option == '2':
        add_plan()  # Add
    elif chosen_menu_option == '3':
        edit_plan()     # Edit
    elif chosen_menu_option == '4':
        show_plans()  # Show plan for single day
    elif chosen_menu_option == '5':
        show_all_plans()  # Show all plans
    elif chosen_menu_option == '6':
        save_plans()  # Save
    elif chosen_menu_option == '7':
        download_example_plan()  # Example plan
    elif chosen_menu_option == '8':
        print("Your working directory (the folder where the plans are saved) is at:")
        print(workdir)
        # Wait showing menu till user presses enter
        show_how_to_exit()  # Print working directory
    elif chosen_menu_option == '9' or chosen_menu_option == 'exit':
        print("Bye!")
        time.sleep(1)
        exit(0)  # Close the application
    else:
        # The user has typed in a command that is not recognized
        print('"' + chosen_menu_option + '"' + " is not listed as an option." +
              "Please type the digit in front of the menu option you want. For example '3'")

    # Show the menu again after a process is done.
    # This ensures a loop, and that the program is
    # never closed unless the user closes it.
    show_menu()


# Show all plans for a specific day
def show_plans(what_day=None, print_numbers=False, wait_before_exit=True):
    if what_day is None:
        # Ask what day to show
        what_day = get_valid_day_from_user("What day would you like to see?")

    # Check if plans dictionary contain that day? If not,
    # inform user that there are no plans for that day.
    if what_day in plans:
        print("Plans for " + what_day + ":")
        for plan in plans[what_day]:
            if print_numbers:
                print("[" + plan + "]:  ", end="")
            print(plans[what_day][plan]['start_time'] + ' - ' + plans[what_day][plan]['end_time'] + ' ' +
                  plans[what_day][plan]['title'])
    else:
        print(what_day + " has no plans")

    # Wait showing menu till user presses enter
    if wait_before_exit is True:
        show_how_to_exit()


# Show all plans for all days
def show_all_plans():
    print("------- THIS WEEKS SCHEDULE -------")
    for day in _available_days:
        print(day + ":")
        # If the day has plans: print them, if not: print "no plans"
        if day in plans.keys():
            # Get the time millis of the item
            def get_time_as_millis(item):
                # Time is valid
                time_str = '2022-01-01 ' + item[1]["start_time"] + ":00"
                time_format = '%Y-%m-%d %H:%M:%S'
                return datetime.strptime(time_str, time_format).timestamp() * 1000

            # Sort the plan by millisecond and print the plan in the correct order
            for plan in sorted(plans[day].items(), key=get_time_as_millis, reverse=False):
                print(f'    {plan[1]["start_time"]} - {plan[1]["end_time"]} {plan[1]["title"]}')
        else:
            print('    --No plans--')

    # Wait showing menu till user presses enter
    show_how_to_exit()


# Populate the plans dictionary if there are any stored plans
def load_plans(allow_filename_change=True):
    # Should we allow a custom filename?
    if allow_filename_change:
        ask_user_for_custom_file_name()

    # Load the plans from the file
    global plans
    loaded_plans = load_plans_file()
    if loaded_plans is not None:
        plans = loaded_plans


# Loads plans from filepath
def load_plans_file():
    # Does the file exist?
    try:
        # Read the file in the path
        my_file = open(file_path, "r")
        plans_txt = my_file.read()
        my_file.close()

        # Try parsing the JSON string from the file into a dict, and return the dict
        parsed_json = json.loads(plans_txt)
        print("Plans loaded!")
        time.sleep(1)
        return parsed_json
    except:
        print(f"Could not find the plans file: '{file_path}'. Does the program "
              f"have reading permission to this directory, and does the file exist?")
    time.sleep(1)

    return None


# Add a plan to plans dict
def add_plan():
    # Ask user for day
    day = get_valid_day_from_user("Which day would you like to add an event to?")

    # Ask for event start/end time
    start_time = ask_for_time("When does the event start? (e.g. 13:30)")
    end_time = ask_for_time("When does the event end? (e.g. 15:30)")

    # Ask for the plan
    print("What is the title of the event?")
    the_plan = input()

    # Does the dictionary contain the day? If not, add it
    if day not in plans:
        plans[day] = {}
    plans[day][id_generator()] = {'start_time': start_time, 'end_time': end_time, 'title': the_plan}

    print("Plan added!")
    time.sleep(1)


# -------- EDIT PLAN -------- #
_EDIT_DAY = '1'
_EDIT_START_TIME = '2'
_EDIT_END_TIME = '3'
_EDIT_TITLE = '4'
_EDIT_DELETE_EVENT = '5'
_EDIT_EXIT = '6'


# Edit a plan
def edit_plan():
    # Get a day and an event ID from that day
    day = get_valid_day_from_user("What day would you like to edit?")
    event_id = ask_for_event_id_from_day(day)
    clear()

    # Show edit menu
    what_to_change = get_edit_menu_option(day, event_id)

    # Process chosen menu option
    if what_to_change == _EDIT_DAY:
        # Ask user for a valid day
        new_day = get_valid_day_from_user("Please type in a new day")

        # Move event from previous day
        plans[new_day][event_id] = plans[day][event_id]
        if event_id in plans[day]:
            del plans[day][event_id]    # Delete event in previous day

        print(f"Successfully moved event from {day} to {new_day}")
    elif what_to_change == _EDIT_START_TIME:
        # Edit start time: Ask user for a new start time
        plans[day][event_id]['start_time'] = ask_for_time("Please type in a new start time (e.g. 15:30):")
        print("Start time successfully changed!")
        time.sleep(1)
    elif what_to_change == _EDIT_END_TIME:
        # Edit end time: Ask user for a new end time
        plans[day][event_id]['end_time'] = ask_for_time("Please type in a new end time (e.g. 15:30):")
        print("End time successfully changed!")
        time.sleep(1)
    elif what_to_change == _EDIT_TITLE:
        # Edit title: Ask user for a new title
        print("Please type in a new title: ")
        new_title = input()

        # Make sure the user input is not empty
        if new_title == '':
            print('Could not edit event. No title provided')
            time.sleep(1)
            return

        # Set the new title
        plans[day][event_id]['title'] = new_title
        print("Event edited successfully!")
        time.sleep(1)
    elif what_to_change == _EDIT_DELETE_EVENT:
        # Delete event
        print("Are you sure you want to delete this event (y/n):")  # Get a confirmation from the suer
        print(str(plans[day][event_id]['start_time']) + " - " + str(
            plans[day][event_id]['end_time']) + " " + str(plans[day][event_id]['title']))

        # Do not delete event
        if input() != 'y':
            print("No worries! Nothing was deleted")
            show_how_to_exit()
            clear()
            edit_plan()
            return

        # Delete event
        if event_id in plans[day]:
            del plans[day][event_id]
            print("Successfully deleted event!")
    elif what_to_change == _EDIT_EXIT:
        # Exit
        return

    show_how_to_exit()


# Ask user for eventID, and check if it exists
def ask_for_event_id_from_day(day):
    # Show plan, and ask user which event should be changed
    print('-----------------------------------')
    show_plans(day, print_numbers=True, wait_before_exit=False)
    print('')
    print('Please type the EventID of the event you would like to edit (e.g. \'K0U7KP\'):')
    edit_event_id = input().upper()

    # Remove '[]' symbols if present in users answer
    edit_event_id = edit_event_id.replace('[', '')
    edit_event_id = edit_event_id.replace(']', '')

    # Check if user entered valid event-id
    if edit_event_id not in plans[day]:
        print('Could not find an event with id: ' + edit_event_id)
        time.sleep(1)
        return ask_for_event_id_from_day(day)
    return edit_event_id


# Show edit menu and let user choose and option
def get_edit_menu_option(day, event_id):
    # Show the menu
    clear()
    print('Now editing: ' + str(plans[day][event_id]['start_time']) + " - " + str(
            plans[day][event_id]['end_time']) + " " + str(plans[day][event_id]['title']))
    print('-----------------------------------')
    print("What would you like to change?")
    print("1) Day")
    print("2) Start time")
    print("3) End time")
    print("4) Title")
    print("5) Delete event")
    print("6) Exit")

    # Let user choose an option
    what_to_change = input()

    # Check if user has a valid choice
    if what_to_change != '1' \
            and what_to_change != '2' and what_to_change != '3' and what_to_change != '4' \
            and what_to_change != '5' and what_to_change != '6':
        # Choice was not valid
        print(what_to_change + " is not an option in the menu!")
        time.sleep(2)
        return get_edit_menu_option(day, event_id)
    return what_to_change


# -------- END EDIT PLAN -------- #


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
    print("Name of file (without file extension)?")
    print("Just press enter for the 'main plans' file")
    wanted_file_name = input()
    global file_path
    # If user specifies filename: use it, if not: use default
    if wanted_file_name != "":
        file_path = workdir + os.path.sep + wanted_file_name + ".json"  # Custom plan
    else:
        file_path = workdir + os.path.sep + 'MainPlans.json'  # Default plan


# Store the plans dict in the filepath
def save_plans():
    # Make sure the dictionary is not empty. If empty: print 'no plans' and return
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

    # Write the content provided to the file
    try:
        my_file = open(custom_file_path, "w")
        my_file.write(content)
        my_file.close()
        return True
    except:
        return False


# Don't show the menu before the user is done reading
def show_how_to_exit():
    print()
    print("[Press enter to exit]", end="")
    input()


# Clear console
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Ask for a time, and check if it's a real time
def ask_for_time(line_to_print):
    print(line_to_print)
    chosen_time = input()
    if not time_is_valid(chosen_time):
        print(chosen_time + " is not a time")
        return ask_for_time(line_to_print)
    return chosen_time


# Ask user for a valid day
def get_valid_day_from_user(message):
    # Ask user for a valid day
    print(message)
    new_day = input().lower()

    # Check if user entered a valid day
    if new_day not in _available_days:
        print(new_day + " is not a day!")
        time.sleep(2)
        return get_valid_day_from_user(message)
    return new_day


# Check if the day submitted by the user is a real day
def day_is_real(day):
    if day not in _available_days:
        print(day + " is not a day!")
        return False
    return True


# Download the example plan, and load it
def download_example_plan():
    # Check if there are any plans, if yes: ask if user wants to overwrite
    if len(plans) != 0:
        print("Your current plan is not empty. Are you sure you want to overwrite it (y/n)?")
        print("Answer: ", end=" ")
        if input().lower() != 'y':
            print("Okay, no worries. Nothing has been overwritten")
            show_how_to_exit()
            return

    # Example plan URL
    example_plan_url = 'https://github.com/Johannett321/acit4420-oblig1/blob/main/CodePlans/ExamplePlans.json?raw=true'

    # Download the example plan
    try:
        # Download the plan data
        print("Downloading example plan...")
        response = urllib.request.urlopen(example_plan_url)
        data = response.read()
        text = data.decode('utf-8')

        # Write the downloaded data to the 'ExamplePlan.json' file
        write_to_file(workdir + os.path.sep + "ExamplePlan.json", text)
        print("Example plan downloaded! Loading the plan...")
        time.sleep(2)
    except:
        # Failed to download, return
        print("Could not download example plan. Is your computer connected to the internet?")
        time.sleep(2)
        return

    # Load exampleplan
    global file_path
    file_path = workdir + os.path.sep + 'ExamplePlan.json'
    load_plans(False)

    # Wait showing menu till user presses enter
    show_how_to_exit()


# Start the program
startup()
