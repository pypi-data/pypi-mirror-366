# Copyright (c) 2024, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html


import os
import sys
import argparse
import json
import importlib.metadata
import difflib
import shutil
import tempfile

import copykitten


try:
    __version__ = f"fetchy {importlib.metadata.version('fetchy_cli')} from fetchy_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."

# Set file paths
storage_folder = os.path.expanduser("~/.local/share/fetchy/")
storage_file = "fetchy.json"
storage_path = storage_folder + storage_file


# Check if storage folder exists, create it if missing.
if os.path.exists(os.path.expanduser(storage_folder)) == False:
    os.makedirs(storage_folder)

# Check if storage file exists, create it if missing.
if os.path.exists(storage_path) == False:
    with open(storage_path, 'w', encoding='utf-8') as file:
        json.dump({}, file)

# read storage file
try:
    with open(storage_path, 'r') as file:
        data = json.load(file)
except ValueError:
    print(f"Error reading {storage_path}! Try deleting the file :(")
    sys.exit(1)


supported_editors =  [
    'vim',
    'nano',
    'emacs',
    'micro',
    'ne',
    'joe',
    'ed',
    'kak'
]

# Set argument parsing
parser = argparse.ArgumentParser(
    description="Fetchy: Fetch strings from your system rather than your own memory!",
    epilog="(fet with no arguments will list entries)\n\nExample:\n> fet -n pi 3.14159265359\n> fet pi\n3.14159265359\n\nHomepage: https://github.com/espehon/fetchy-cli",
    allow_abbrev=False,
    add_help=False,
    usage="fet [Name] [-n Name Value] [-c Name] [-d Name1 ...] [-r OldName NewName] [-l] [-?] ",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('-v', '--version', action='version', version=__version__, help="Show package version and exit.")
parser.add_argument('-c', '--copy', nargs=1, metavar='N', action='store', type=str, help='Copy the value of [N] to the clipboard.')
parser.add_argument('-l', '--list', action='store_true', help='List saved entry names and values.')
parser.add_argument('-n', '--new', nargs=2, type=str, metavar=('N', 'V'), action='store', help='Create [N] with the value of [V]. (Overwrite existing)')
parser.add_argument('-d', '--delete', nargs='+', metavar=('N1', 'N2'), action='store', type=str, help='Delete [N1] etc.')
parser.add_argument('-r', '--rename', nargs=2, type=str, metavar=('O', 'N'), action='store', help='Rename [O] to [N].')
parser.add_argument('-e', '--edit', nargs=1, type=str, metavar='N', action='store', help="Edit the value of [N] in a text editor.")
parser.add_argument("name", nargs='?', help="Name of entry to fetch. (Case sensitive)")


def sort_dict(dictionary) -> dict:
    sorted_dict = dict(sorted(dictionary.items()))
    return sorted_dict


def save_data(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(sort_dict(dictionary), file, indent=4)


def find_best_match(user_input, dictionary, cutoff=0.7):
    """Usage:
    key = find_best_match(user_input, data)
    if key:
        print(data[key])
    else:
        print("No close match found.")"""
    
    keys = list(dictionary.keys())
    # Normalize keys to lowercase for matching
    keys_lower = [k.lower() for k in keys]
    input_lower = user_input.lower()
    # Find close matches
    matches = difflib.get_close_matches(input_lower, keys_lower, n=1, cutoff=cutoff)
    if matches:
        # Return the original key (not lowercased)
        matched_index = keys_lower.index(matches[0])
        return keys[matched_index]
    return None


def edit_entry(dictionary, entry_name):
    if entry_name not in dictionary:
        print(f"Entry '{entry_name}' does not exist.")
        return

    # Write current value to a temp file
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.txt') as tmp:
        tmp.write(str(dictionary[entry_name]))
        tmp.flush()
        tmp_name = tmp.name

    try:
        # Find an editor
        editor = None
        for editor_name in supported_editors:
            if shutil.which(editor_name) is not None:
                editor = editor_name
                break
        if editor is None:
            editor = os.environ.get('EDITOR') or 'notepad'

        # Open editor
        os.system(f"{editor} \"{tmp_name}\"")

        # Read edited value
        with open(tmp_name, 'r') as f:
            new_value = f.read().rstrip()

        if new_value != str(dictionary[entry_name]):
            dictionary[entry_name] = new_value
            save_data(dictionary, storage_path)
            print(f"Entry '{entry_name}' updated.")
        else:
            print("No changes made.")

    except Exception as e:
        print("An error occurred while editing the entry.")
        print(e)
    finally:
        try:
            os.remove(tmp_name)
        except Exception:
            pass


def overwrite_note(dictionary, note_name, note_value):
    if note_name in dictionary:
        user = str.lower(input(f"{note_name} already exists; do you want to overwrite it? (N/y): "))
        if user[0] == 'y':
            dictionary[note_name] = note_value
            save_data(data, storage_path)
            print("Note has been overwritten.")
        else:
            print("No changes were made.")
    else:
        print(f"Error: {note_name} does not exist!")


def new_note(dictionary, note_name, note_value):
    if note_name in dictionary:
        overwrite_note(dictionary, note_name, note_value)
    else:
        dictionary[note_name] = note_value
        save_data(data, storage_path)
        print("Note created.")


def delete_notes(dictionary, note_name_list: list):
    items_deleted = 0
    print("Matched entries:")
    for i in note_name_list:
        print(f"\t{i}")
    user = input("\nAre you sure you want to delete these entries? (y/N) > ").strip()
    if len(user) > 0 and str(user[0]).lower() == "y":
        for note_name in note_name_list:
            if note_name in dictionary:
                dictionary.pop(note_name)
                items_deleted += 1
                print(F"{note_name} marked for removal.")
            else:
                print(f"{note_name} is not an entry.")
        if items_deleted > 0:
            save_data(dictionary, storage_path)
            print(f"{items_deleted} entries deleted.")
        else:
            print("No changes were made.")
    else:
        print("Deletion canceled.")


def rename_note(dictionary, old_name, new_name):
    if old_name in dictionary:
        dictionary[new_name] = dictionary[old_name]
        dictionary.pop(old_name)
        save_data(dictionary, storage_path)
        print("Entry renamed.")
    else:
        print(f"{old_name} is not an entry.")

def list_items(dictionary):
    if len(dictionary) == 0:
        print("No entries. Try 'fet -?' for help.")
        return
    indent = 4
    print(f"{len(dictionary)} entries:")
    for key in dictionary:
        print(f"{' ' * indent}{key}")


def long_list_items(dictionary):
    if len(dictionary) == 0:
        print("No entries. Try 'fet -?' for help.")
        return
    indent = 4
    ellipsis = "..."
    width_1 = len(str(max(dictionary.keys(), key=lambda k: len(str(k))))) + indent
    width_2 =max([os.get_terminal_size().columns - width_1 - indent - len(ellipsis), 16])
    print(f"{len(dictionary)} entries:")
    for key in dictionary:
        if len(repr(str(dictionary[key]))) > width_2:
            print(f"{str.rjust(key, width_1)}{' ' * indent}{repr(str(dictionary[key]))[0:width_2]}{ellipsis}")
        else:
            print(f"{str.rjust(key, width_1)}{' ' * indent}{repr(str(dictionary[key]))}")


def copy_to_clipboard(dictionary, note_name):
    if note_name in dictionary:
        copykitten.copy(dictionary[note_name])
        print(f"{note_name} copied to clipboard √")
    else:
        print(f"No item matched {note_name}")


def fetch(dictionary, note_name):
    try:
        print(dictionary[note_name])
    except ValueError:
        print(f"No item matched {note_name}")


def cli(argv=None):
    args = parser.parse_args(argv) #Execute parse_args()
    if len(sys.argv) == 1:
        list_items(data)
    elif args.new:
        new_note(data, args.new[0], args.new[1])
    elif args.list:
        long_list_items(data)
    elif args.copy:
        key_name = find_best_match(args.copy[0], data)
        if key_name:
            copy_to_clipboard(data, key_name)
        else:
            print(f"'{args.copy[0]}' did not match any entries :(")
    elif args.rename:
        key_name = find_best_match(args.rename[0], data)
        if key_name:
            rename_note(data, key_name, args.rename[1])
        else:
            print(f"'{args.copy[0]}' did not match any entries :(")
    elif args.edit:
        key_name = find_best_match(args.edit[0], data)
        if key_name:
            edit_entry(data, key_name)
        else:
            print(f"'{args.edit[0]}' did not match any entries :(")
    elif args.delete:
        key_list = []
        for i in args.delete:
            key_name = find_best_match(i, data)
            if key_name:
                key_list.append(key_name)
            else:
                print(f"'{i}' did not match any entries.")
        if len(key_list) > 0:
            delete_notes(data, key_list)
        else:
            print(f"No entries matched :(")
    elif args.name:
        key_name = find_best_match(args.name, data)
        if key_name:
            print(f"{key_name}:\n{data[key_name]}")
        else:
            print(f"'{args.name}' did not match any entries :(")
