import os
import sys
import argparse
from yoyo import read_migrations, get_backend
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ANSI Color Styles
class Style:
    SUCCESS = "\033[92m"  # Green
    INFO = "\033[94m"  # Blue
    WARNING = "\033[93m"  # Yellow
    FAIL = "\033[91m"  # Red
    BOLD = "\033[1m"  # Bold
    RESET = "\033[0m"  # Reset colors


# --- Logging Helpers ---
def log_info(message):
    print(f"{Style.INFO}{message}{Style.RESET}")


def log_success(message):
    print(f"{Style.SUCCESS}{message}{Style.RESET}")


def log_warning(message):
    print(f"{Style.WARNING}{message}{Style.RESET}")


def log_error(message):
    print(f"{Style.FAIL}Error: {message}{Style.RESET}")


def log_bold(message):
    print(f"{Style.BOLD}{message}{Style.RESET}")


# --- Core Logic ---
def get_url():
    """Builds the database URL from environment variables."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")

    if not all([user, password, host, port, name]):
        log_error("Missing DB variables in .env file")
        sys.exit(1)

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def apply_migrations():
    """Applies new SQL migrations to the database."""
    try:
        backend = get_backend(get_url())
        all_migrations = read_migrations("./migrations")
        to_apply = backend.to_apply(all_migrations)

        if len(to_apply) == 0:
            log_info("Database is up to date. No new migrations.")
            return

        log_bold(f"Found {len(to_apply)} new migrations. Applying...")

        with backend.lock():
            backend.apply_migrations(to_apply)

        log_success(f"Success! Applied {len(to_apply)} new migrations.")
    except Exception as e:
        log_error(f"While applying migrations: {e}")
        sys.exit(1)


def rollback_migrations(target_id):
    """Rolls back the last applied migrations."""
    try:
        backend = get_backend(get_url())
        all_migrations = read_migrations("./migrations")
        applied = backend.to_rollback(all_migrations)

        if len(applied) == 0:
            log_warning("No migrations to rollback.")
            return

        if target_id:
            target = []
            found = False
            for m in applied:
                if m.id == target_id:
                    found = True
                    break
                target.append(m)

            if not found:
                log_error(f"Migration '{target_id}' not found in applied migrations.")
                return

            if not target:
                log_info(f"Database is already at migration '{target_id}'.")
                return
        else:
            # Default: rollback only the last one
            target = applied[:1]
        log_bold(f"Rolling back {len(target)} migration(s)...")

        with backend.lock():
            backend.rollback_migrations(target)

        log_success("Success! Rollback completed.")
    except Exception as e:
        log_error(f"During rollback: {e}")
        sys.exit(1)


def show_current():
    """Displays the list of applied migrations and highlights the latest one."""
    try:
        backend = get_backend(get_url())
        all_migrations = read_migrations("./migrations")

        # Get migrations that are already in the database
        applied = backend.to_rollback(all_migrations)

        if not applied:
            log_warning("No migrations have been applied to the database yet.")
            return

        log_bold("Applied migrations (Latest on top):")

        for i, m in enumerate(applied):
            prefix = f"{Style.SUCCESS}* {Style.RESET}" if i == 0 else "  "
            line_style = Style.BOLD if i == 0 else ""
            print(f"{prefix}{line_style}{m.id}{Style.RESET}")

    except Exception as e:
        log_error(f"Could not fetch migration status: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQL Migration Management Tool.")

    parser.add_argument(
        "action",
        choices=["apply", "rollback", "status"],
        default="apply",
        nargs="?",
        help="Action: apply, rollback, or status (default: status)",
    )

    parser.add_argument(
        "revision", nargs="?", help="Optional: Migration ID to rollback to"
    )

    args = parser.parse_args()

    if args.action == "status":
        show_current()
    elif args.action == "rollback":
        rollback_migrations(target_id=args.revision)
    else:
        apply_migrations()
