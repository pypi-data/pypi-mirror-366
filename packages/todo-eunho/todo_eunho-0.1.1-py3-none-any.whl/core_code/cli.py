import argparse
import time
from .utils import parse_date, parse_time, format_date, format_time, sort_key
from .models import TodoItem
from .storage import add_item, load_items, save_items
from rich.console import Console
from rich.table import Table
from rich.progress import track

def main():
    parser = argparse.ArgumentParser(description="Todo CLI Tool")
    subparser = parser.add_subparsers(dest="command", required=True)

    # add 명령어
    add_parser = subparser.add_parser("add", help="Add a new todo item")
    add_parser.add_argument("title", type=str, help="Title of the todo item")
    add_parser.add_argument("--date", type=str, help="Date in format DD_MON_YYYY")
    add_parser.add_argument("--time", type=str, help="Time in format HH_MM")

    # show 명령어
    show_parser = subparser.add_parser("show", help="Show all todo items")

    # delete 명령어
    delete_parser = subparser.add_parser("delete", help="Delete todo by index")
    delete_parser.add_argument("index", type=int, help="Index to delete")

    # clear 명령어
    clear_parser = subparser.add_parser("clear", help="Clear all todo items")
    clear_parser.add_argument("--force", action="store_true", help="Skip confirmation")

    # fix 명령어
    fix_parser = subparser.add_parser("fix", help="Fix a todo item's date/time")
    fix_parser.add_argument("index", type=int)
    fix_parser.add_argument("--date", type=str)
    fix_parser.add_argument("--time", type=str)

    # mdel 명령어
    mdel_parser = subparser.add_parser("mdel", help="Delete multiple todo items")
    mdel_parser.add_argument("indexes", type=int, nargs="+", help="List of indexes to delete")

    args = parser.parse_args()

    # 1. add
    if args.command == "add":
        try:
            d = parse_date(args.date) if args.date else None
            t = parse_time(args.time) if args.time else None
            item = TodoItem(title=args.title, date_att=d, time_att=t)
            add_item(item)
            print("Todo added successfully!")
        except Exception as e:
            print(f"Error while adding todo: {e}")

    # 2. show
    elif args.command == "show":
        items = load_items()
        console = Console()
        print("\n")
        table = Table(title="ToDo List", show_lines=True)
        table.add_column("Index", style="cyan", justify="center")
        table.add_column("Title", style="bold white", justify="center")
        table.add_column("Date", style="green", justify="center")
        table.add_column("Time", style="magenta", justify="center")

        if not items:
            console.print("[bold yellow]No todo items found.[/bold yellow]")
        else:
            for idx, item in enumerate(sorted(items, key=sort_key)):
                table.add_row(
                    str(idx),
                    item.title,
                    format_date(item.date_att),
                    format_time(item.time_att)
                )
            console.print(table)
        print("\n")

    # 3. delete
    elif args.command == "delete":
        try:
            items = load_items()
            index = args.index
            if index < 0 or index >= len(items):
                print("Invalid index.")
            else:
                print(f"Deleting item at index {index}...")
                for _ in track(range(1), description="Deleting..."):
                    time.sleep(1)
                removed = items.pop(index)
                save_items(items)
                print(f"Deleted: {removed.title}")
        except Exception as e:
            print(f"Error while deleting: {e}")

    # 4. clear
    elif args.command == "clear":
        if args.force or input("Are you sure you want to clear the whole ToDo List? (y/n): ").strip().lower() == "y":
            try:
                save_items([])
                print("All todo items cleared.")
            except Exception as e:
                print(f"Error while clearing: {e}")
        else:
            print("Cancelled. Nothing was cleared.")

    # 5. fix
    elif args.command == "fix":
        try:
            items = load_items()
            index = args.index
            if index < 0 or index >= len(items):
                print("Invalid index.")
            else:
                item: TodoItem = items[index]
                if args.date:
                    item.date_att = parse_date(args.date)
                if args.time:
                    item.time_att = parse_time(args.time)
                save_items(items)
                print(f"Updated item: {item.title}")
        except Exception as e:
            print(f"Error while fixing: {e}")

    # 6. mdel
    elif args.command == "mdel":
        try:
            items = load_items()
            indexes = sorted(set(args.indexes), reverse=True)
            print("Deleting multiple items...")
            for idx in track(indexes, description="Deleting..."):
                time.sleep(0.2)
                if 0 <= idx < len(items):
                    removed = items.pop(idx)
                    print(f"Deleted: {removed.title}")
                else:
                    print(f"Invalid index skipped: {idx}")
            save_items(items)
        except Exception as e:
            print(f"Error during multiple delete: {e}")