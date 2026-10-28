from pathlib import Path
import sys
import json
from datetime import datetime

def edit_distance(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = list(range(n + 1))

    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            tmp = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(dp[j] + 1,        # deletion
                        dp[j - 1] + 1,    # insertion
                        prev + cost)      # substitution
            prev = tmp
    return dp[n]

def lexicographic_comparison_function(a : str, b : str) -> bool:
    THRESHOLD = 2
    return edit_distance(a, b) <= THRESHOLD

def dateTime() -> str:
    return str(datetime.now()).split('.')[0]

def printTodolist(object : dict) -> None:
    for (task, (description, date)) in object.items():
        print(f"Task : {task} | Created at {date}")
        print(f"Description : {description}")

actions = {
    "done" : {
        "mutate"        : lambda obj, x: obj.pop(x),
        "valid"         : lambda obj, x: x in obj,
        "args"          : 2,
    },
    "do"   : {
        "mutate"        : lambda obj, x: obj.update({x.split(':')[0].strip() : (x.split(':')[1].strip(), dateTime())}),
        "valid"         : lambda obj, x: len(x.split(':')) >= 2,
        "args"          : 2,
    },
    "dump" : {
        "mutate"        : lambda obj, x: obj.clear(),
        "valid"         : lambda obj, x: True,    
        "args"          : 1,
    },
    "list" :  {
        "mutate"        : lambda obj, x: printTodolist(obj),
        "valid"         : lambda obj, x: True,    
        "args"          : 1,
    },
}

file_path = Path.home() / ".todo.jsonc"

file_path.touch()

if (file_path.stat().st_size == 0):
    file_path.write_text("{}")

writeToFile = False

with open(file_path, "r+") as f:
    todolist = json.load(f)

    args = sys.argv

    if len(args) <= 1:
        print(f"Failure! Usage: {args[0]} <{'|'.join(list(actions.keys()))}> [task]")
    else:
        action = args[1].lower()

        if action not in actions:
            similar = list(filter(lambda x: lexicographic_comparison_function(action, x), actions.keys()))
            if len(similar) == 0:
                print(f"Sorry, {action} is not a recognized action. Recognized actions are: {'|'.join(actions.keys())}")
            else:
                print(f"Sorry, {action} is not a recognized action. Did you mean: {'|'.join(similar)}")
        elif len(args) > actions[action]["args"]:
            task = "" if actions[action]["args"] == 1 else args[2].lower()

            fm = actions[action]
            if fm["valid"](todolist, task):
                fm["mutate"](todolist, task)
                writeToFile = True
            else:
                similar = list(filter(lambda x: lexicographic_comparison_function(task, x), todolist.keys())) 
                if len(similar) == 0:
                    print(f"Sorry, {task} is an unknown or invalid task.")
                else:
                    print(f"Sorry, {task} is an unknown or invalid task. Did you mean to reference {'|'.join(similar)}")
        else:
            print(f"Sorry, {action} requires {actions[action]["args"]-1} additional parameters but {"None" if len(args) == 2 else len(args)-2} were provided")

if writeToFile:
    with open(file_path, "w") as f:
        json.dump(todolist, f)

