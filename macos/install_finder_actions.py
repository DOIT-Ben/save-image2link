"""Install macOS Finder Quick Actions for SaveImageToLink.

This script writes Automator workflow bundles into ~/Library/Services.
Run it on macOS after installing dependencies.
"""
from __future__ import annotations

import argparse
import os
import plistlib
import stat
import sys
from pathlib import Path


APP_NAME = "SaveImageToLink"
SERVICE_DIR = Path.home() / "Library" / "Services"
SCRIPT_PATH = Path(__file__).with_name("save_image_to_link_macos.py").resolve()


def shell_script_for_default() -> str:
    return f'{sys.executable} "{SCRIPT_PATH}" --save-default --copy\n'


def shell_script_for_selected_folder() -> str:
    return f'''for f in "$@"
do
  if [ -d "$f" ]; then
    {sys.executable} "{SCRIPT_PATH}" --save-here "$f" --copy
    exit $?
  fi
done
{sys.executable} "{SCRIPT_PATH}" --save-default --copy
'''


def workflow_plist(name: str, shell_script: str, receives_input: bool) -> dict:
    input_type = "com.apple.Automator.nothing" if not receives_input else "com.apple.Automator.fileSystemObject"
    return {
        "AMApplicationBuild": "523",
        "AMApplicationVersion": "2.10",
        "AMDocumentVersion": "2",
        "actions": [
            {
                "action": {
                    "AMAccepts": {"Container": "List", "Optional": True, "Types": [input_type]},
                    "AMActionVersion": "2.0.3",
                    "AMApplication": ["Automator"],
                    "AMParameterProperties": {},
                    "AMProvides": {"Container": "List", "Types": ["com.apple.Automator.nothing"]},
                    "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "COMMAND_STRING": shell_script,
                        "CheckedForUserDefaultShell": True,
                        "inputMethod": 1 if receives_input else 0,
                        "shell": "/bin/zsh",
                    },
                    "BundleIdentifier": "com.apple.RunShellScript",
                    "CFBundleVersion": "2.0.3",
                    "CanShowSelectedItemsWhenRun": False,
                    "CanShowWhenRun": True,
                    "Category": ["AMCategoryUtilities"],
                    "Class Name": "RunShellScriptAction",
                    "InputUUID": "input",
                    "Keywords": ["Shell", "Script", "Command", "Run"],
                    "OutputUUID": "output",
                    "UUID": name.replace(" ", "-"),
                    "UnlocalizedApplications": ["Automator"],
                    "arguments": {"0": {"default value": 0, "name": "inputMethod", "required": "0", "type": "0"}},
                    "isViewVisible": True,
                    "location": "857.000000:610.000000",
                    "nibPath": "/System/Library/Automator/Run Shell Script.action/Contents/Resources/English.lproj/main.nib",
                },
                "isViewVisible": True,
            }
        ],
        "connectors": {},
        "workflowMetaData": {
            "applicationBundleIDsByPath": {},
            "applicationPaths": [],
            "inputTypeIdentifier": input_type,
            "outputTypeIdentifier": "com.apple.Automator.nothing",
            "presentationMode": 15,
            "processesInput": receives_input,
            "serviceApplicationBundleID": "com.apple.finder",
            "serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
            "serviceInputTypeIdentifier": input_type,
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
        },
    }


def write_workflow(name: str, shell_script: str, receives_input: bool) -> Path:
    workflow_dir = SERVICE_DIR / f"{name}.workflow" / "Contents"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    document = workflow_dir / "document.wflow"
    with document.open("wb") as handle:
        plistlib.dump(workflow_plist(name, shell_script, receives_input), handle)
    os.chmod(document, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    return workflow_dir.parent


def install() -> list[Path]:
    return [
        write_workflow("Save Image and Copy Link", shell_script_for_default(), receives_input=False),
        write_workflow("Save Image to Selected Folder", shell_script_for_selected_folder(), receives_input=True),
    ]


def uninstall() -> list[Path]:
    removed: list[Path] = []
    for name in ["Save Image and Copy Link", "Save Image to Selected Folder"]:
        workflow = SERVICE_DIR / f"{name}.workflow"
        if workflow.exists():
            import shutil

            shutil.rmtree(workflow)
            removed.append(workflow)
    return removed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install or uninstall SaveImageToLink Finder Quick Actions.")
    parser.add_argument("--uninstall", action="store_true", help="Remove installed Finder Quick Actions.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    paths = uninstall() if args.uninstall else install()
    for path in paths:
        print(path)
