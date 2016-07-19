# /showmehow/showmehow.py
#
# showmehow - entrypoint
#
# Copyright (c) 2016 Endless Mobile Inc.
# All rights reserved.
"""Entry point for showmehow."""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap


def interactive_process(shell, env=None):
    """Interact with a process."""
    environment = os.environ.copy()
    if env:
        environment.update(env)
    return subprocess.Popen([shell],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            env=environment)


def run_in_shell(shell, cmd, env=None):
    """Run a process in a shell, then return."""
    return interactive_process(shell,
                               env=env).communicate("{}; exit 0".format(cmd)
                                                                .encode())


def practice_task(task):
    """Practice the task named :task:"""
    for lesson_spec in task["practice"]:
        print(lesson_spec["task"])
        all_output = ""
        n_failed = 0
        while not re.match(lesson_spec["expected"],
                           all_output,
                           flags=re.MULTILINE):
            if n_failed > 0:
                print(lesson_spec["fail"])
            if os.environ.get("NONINTERACTIVE", None):
                output = "$ ".encode("utf-8")
                error = "".encode("utf-8")
                break
            else:
                (output,
                 error) = run_in_shell("bash",
                                       input("$ "),
                                       env=lesson_spec.get("environment",
                                                           None))

            all_output = (textwrap.indent(output.decode(), "> ") +
                          textwrap.indent(error.decode(), "> "))
            n_failed += 1
        
        print("\n".join(textwrap.wrap(lesson_spec["success"])))

    print("---")
    print("\n".join(textwrap.wrap(task["done"])))


def show_tasks(tasks):
    """Show tasks that can be done in the terminal."""
    print("Hey, how are you? I can tell you about the following tasks:")
    for task in tasks:
        print("[{task[name]}] - {task[desc]}".format(task=task))


def main(argv=None):
    """Entry point. Parse arguments and start the application."""
    parser = argparse.ArgumentParser('showmehow - Show me how to do things')
    parser.add_argument('task',
                        nargs='?',
                        metavar='TASK',
                        help='TASK to perform',
                        type=str)
    parser.add_argument('--tasks-to-do',
                        metavar='JSON',
                        help='JSON file containing tasks',
                        default='tasks.json',
                        type=str)

    arguments = parser.parse_args(argv or sys.argv[1:])
    with open(arguments.tasks_to_do, "r") as tasks_json_fileobj:
        tasks = json.loads(tasks_json_fileobj.read())

    try:
        task = [t for t in tasks if t["name"] == arguments.task][0]
    except IndexError:
        if arguments.task:
            print("I don't know how to do task {}".format(arguments.task))
        return show_tasks(tasks)

    return practice_task(task)

