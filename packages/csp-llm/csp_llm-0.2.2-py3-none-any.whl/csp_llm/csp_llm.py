#!/usr/bin/env python3

import os
import subprocess
import sys
from argparse import RawTextHelpFormatter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import constants
from check_required_tools import check_app_dependencies, find_app_path, require_java


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Launch the application", formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="ip host of the web server. Default host is 'localhost'. Use 0.0.0.0 to make app accessible on the entire network ",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="server's listening port. Default port is 8501",
    )
    parser.add_argument(
        "--llm_env",
        default=constants.ENVIRONMENTS[2],
        choices=constants.ENVIRONMENTS,
        help=f"default value is '{constants.ENVIRONMENTS[2]}' \nuse --llm_env option to specify your LLM environnement \nvalue '{constants.ENVIRONMENTS[0]}' to use local ollama installed on your computer \nvalue '{constants.ENVIRONMENTS[1]}' to use local lmstudio installed on your computer \nvalue '{constants.ENVIRONMENTS[2]}' to use external LLM + CRIL plateform",
    )

    parser.add_argument("-ev", action="store_true", help="verbose mode")

    args = parser.parse_args()

    APP_FILE = find_app_path("main.py")

    HOST = args.host  # or "0.0.0.0" for whole network access
    PORT = args.port  # default

    print("🚀 Launching the application on...")

    # Vérifier que le fichier existe
    app_path = Path(APP_FILE)
    if not app_path.exists():
        print(f"❌ Error: {APP_FILE} not found")

        return 1

    print("💡 Application dependencies")

    install_messages, are_packages_ok = check_app_dependencies()

    print("\n".join(install_messages))

    if not all(are_packages_ok):
        return 1

    if not require_java(8):
        print("❌ Java 8+ required to use pycsp3")
        return 1

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        APP_FILE,
        "--server.address",
        HOST,
        "--server.port",
        str(PORT),
        "--browser.gatherUsageStats",
        "false",
        "server.maxUploadSize",
        "5",
    ]

    # Afficher l'URL d'accès
    print(f"🌐 Application available at: http://{HOST}:{PORT}")
    os.environ["LLM_ENV"] = args.llm_env
    print(f"💡 LLM environment : { str.upper(os.environ['LLM_ENV'])}")

    print("💡 Press Ctrl+C to stop")
    print("-" * 50)

    try:

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n🛑 Application stopped")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
