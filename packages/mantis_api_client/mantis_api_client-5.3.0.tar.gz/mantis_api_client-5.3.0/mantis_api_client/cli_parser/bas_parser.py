# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import sys
import traceback
from typing import Any
from typing import Dict
from typing import List

from mantis_common_model.pagination import Pagination
from mantis_scenario_model.api_scenario_model import LabListReply
from mantis_scenario_model.lab_config_model import ContentType
from mantis_scenario_model.lab_config_model import LabConfig
from mantis_scenario_model.lab_model import Lab
from mantis_scenario_model.lab_model import ScenarioExecutionStatus

from cr_api_client import redteam_api
from mantis_api_client import scenario_api
from mantis_api_client.cli_parser.lab_parser import set_current_lab
from mantis_api_client.cli_parser.lab_parser import unset_current_lab
from mantis_api_client.cli_parser.redteam_parser import redteam_atomic_handler
from mantis_api_client.cli_parser.redteam_parser import redteam_command_execute_handler
from mantis_api_client.cli_parser.redteam_parser import redteam_command_get_handler
from mantis_api_client.cli_parser.redteam_parser import redteam_command_history_handler
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored
from mantis_api_client.utils import wait_lab


def show_bas_info(lab_id) -> None:
    # Show available BAS agents from lab infrastructure
    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if not active_profile_domain:
        print("[+] Not authenticated")
        return

    print("[+] \033[1mBAS lab infrastructure endpoint\033[0m:")
    print(
        f"  - https://app.{active_profile_domain}/proxy/ (must be reachable from the agent's execution environment)"
    )

    # Show BAS agent download URLs
    if len(redteam_api.attack_knowledge()["payloads"]) > 0:
        print("[+] \033[1mAvailable agents\033[0m:")

        for payload in redteam_api.attack_knowledge()["payloads"]:

            if payload["payload_type"] == "beacon":
                print(
                    f"  - \033[1m{payload['payload_os']}_agent\033[0m: https://app.{active_profile_domain}/proxy/{lab_id}/http/nginxserver/{payload['name']}"
                )

    # Show BAS agent sessions, if any
    attack_sessions = redteam_api.attack_sessions()
    if len(attack_sessions) > 0:
        print("[+] \033[1mAgent sessions\033[0m:")

        for session in attack_sessions:
            print(
                f"  - \033[1msession_id\033[0m: {session['identifier']} - \033[1mhost\033[0m: {session['target']['host']['hostname']} - \033[1mhost_IP\033[0m: {session['target']['ip']} - \033[1musername\033[0m: {session['username']} - \033[1msession_type\033[0m: {session['type']} - \033[1mprivilege_level\033[0m: {session['privilege_level']} - \033[1mactive\033[0m: {session['is_up']}"
            )

            print(
                f"    [hint] You can retrieve available attacks with: '$ mantis bas attack list -s {session['identifier']}'"
            )


#
# 'bas_create_handler' handler
#


def bas_create_handler(args: Any) -> None:
    # Force launching BAS lab infrastructure
    do_run: bool = True

    if not args.workspace_id:
        try:
            workspace_id = get_oidc_client().get_default_workspace(raise_exc=True)
        except Exception as e:
            print(colored(f"Error when fetching BAS API: '{e}'", "red"))
            sys.exit(1)
    else:
        workspace_id = args.workspace_id

    # Retrieve associated workspace id
    if workspace_id is None:
        print(
            colored(
                "Your subscription level does not permit to launch BAS campaigns", "red"
            )
        )
        sys.exit(1)

    # Use an empty lab config as it is currently not used in a BAS context
    lab_config_dict: Dict = {}
    lab_config = LabConfig(**lab_config_dict)

    # Launch topology
    try:

        if do_run:
            lab_id = scenario_api.run_lab_bas(lab_config, workspace_id)
        else:
            lab_id = scenario_api.create_lab_bas(lab_config, workspace_id)

        print(f"[+] \033[1mBAS campaign ID\033[0m: {lab_id}")
        print("[+] Launching BAS lab infrastructure")

        if do_run:
            # In BAS mode, stop wait loop after attack provisioning
            wait_lab(
                lab_id,
                quiet=True,
                exit_on_status=[ScenarioExecutionStatus.scenario_execution],
            )

    except Exception as e:
        print(colored(f"Error when creating BAS campaign: '{e}'", "red"))
        print(traceback.format_exc())
        sys.exit(1)

    # Set current lab
    set_current_lab(lab_id)
    try:
        show_bas_info(lab_id)
    finally:
        unset_current_lab()

    print(
        f"[hint] You can retrieve BAS agent download URLs with: '$ mantis bas info {lab_id}'"
    )


def fetch_bas_labs(all_labs: bool = False) -> List[Lab]:
    """Return BAS labs.

    By default, only return active campaigns.

    If 'all_labs' is set to True, also returns non active campaigns
    (i.e. lab infrastructure is not running)

    """

    try:
        offset = 100
        labs_to_list: List[Lab] = []
        page: int = 1

        while True:
            pagination: Pagination = Pagination(**{"page": page, "limit": offset})
            labs: LabListReply = scenario_api.fetch_labs(
                all_labs=all_labs, pagination=pagination
            )
            labs_to_list.extend(
                [
                    Lab(**lab)
                    for lab in labs["data"]
                    if lab["content_type"] == ContentType.BAS
                ]
            )

            if page * offset >= labs["pagination"]["total_records"]:
                break

            page += 1

    except Exception as e:
        print(f"Error when fetching labs: '{e}'")
        sys.exit(1)

    return labs_to_list


#
# 'bas_list_handler' handler
#


def bas_list_handler(args: Any) -> None:
    all_labs = args.all_labs

    bas_labs: List[Lab] = fetch_bas_labs(all_labs=all_labs)

    print("[+] BAS campaigns:")
    for lab in bas_labs:
        lab_creation_timestamp = (
            datetime.datetime.fromtimestamp(
                lab.lab_creation_timestamp, datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            + " UTC"
        )

        print(f"  [+] \033[1mID\033[0m: {lab.runner_id}")
        print(f"    - \033[1mCampaign creation time\033[0m: {lab_creation_timestamp}")
        print(f"    - \033[1mStatus\033[0m: {lab.status}")


#
# 'bas_info_handler' handler
#


def bas_info_handler(args: Any) -> None:
    # Parameters
    campaign_id = args.campaign_id

    # Set current lab
    set_current_lab(campaign_id)
    try:
        show_bas_info(campaign_id)
    finally:
        unset_current_lab()


#
# 'bas_stop_handler' handler
#


def bas_stop_handler(args: Any) -> None:
    # Parameters
    campaign_id = args.campaign_id

    try:
        scenario_api.stop_lab(campaign_id)
    except Exception as e:
        print(f"Error when stopping BAS campaign: '{e}'")
        sys.exit(1)

    print(f"[+] Ths BAS campaign '{campaign_id}' has been stopped")


def show_available_attacks(session_id: str, filter_tactic: str, filter_technique: str):
    print(f"[+] \033[1mAvailable attacks for BAS agent session\033[0m: {session_id}")

    attacks = redteam_api.list_attacks()
    for attack in attacks:

        # Check if the attack is runnable
        if attack["status"] != "runnable":
            continue

        # Check if the attack is BAS compatible
        if (
            ("worker" not in attack)
            or ("bas_compat" not in attack["worker"])
            or (attack["worker"]["bas_compat"] is False)
        ):
            continue

        # FIXME: attack['values'] is currently a string! Do not provide string dict from REST API
        dict_values = json.loads(attack["values"])
        if not isinstance(dict_values, dict):
            continue

        # Check if the attack is part of the current agent session
        if "attack_session_id" not in dict_values:
            continue
        attack_session_id = dict_values["attack_session_id"]
        if attack_session_id != session_id:
            continue

        # Filter list by technique or tactic
        select = True
        if filter_tactic is not None:
            select = False
            for tactic in attack["worker"]["mitre_data"]["tactics"]:
                if filter_tactic.lower() in [
                    tactic["name"].lower(),
                    tactic["id"].lower(),
                ]:
                    if filter_technique is not None:
                        if (
                            filter_technique
                            == attack["worker"]["mitre_data"]["technique"]["id"]
                        ):
                            select = True
                    else:
                        select = True
        else:
            # No filter_tactic
            if filter_technique is not None:
                select = False
                if (
                    filter_technique
                    == attack["worker"]["mitre_data"]["technique"]["id"]
                ):
                    select = True

        if not select:
            continue

        # Retrieve attacks values, after removing redondant attack session infos
        attack_values = dict_values.copy()
        attack_values.pop("attack_session_type", None)
        attack_values.pop("attack_session_source", None)
        attack_values.pop("attack_session_id", None)

        if attack["worker"]["mitre_data"]["subtechnique"]:
            technique_id = attack["worker"]["mitre_data"]["subtechnique"]["id"]
        else:
            technique_id = attack["worker"]["mitre_data"]["technique"]["id"]

        mitre_attack_tactics = ", ".join(
            [tactic["id"] for tactic in attack["worker"]["mitre_data"]["tactics"]]
        )
        mitre_attack_infos = f"{technique_id} [{mitre_attack_tactics}]"

        print(
            f"  - \033[1mattack_name\033[0m: {attack['worker']['name']:<30} - \033[1mATT&CK\033[0m: {mitre_attack_infos:<18} - \033[1mdescription\033[0m: {attack['worker']['title']} - \033[1mattack_parameters\033[0m:{attack_values}"
        )


def find_bas_lab_from_session_id(session_id: str):
    """Search in active campaigns the agent session ID.

    Returns the lab id that matches.

    """
    bas_labs: List[Lab] = fetch_bas_labs(all_labs=False)

    bas_lab_id = None
    for bas_lab in bas_labs:

        # Check if session_id exists in current lab
        set_current_lab(bas_lab.runner_id)
        try:
            for session in redteam_api.attack_sessions():
                if session["identifier"] == session_id:
                    bas_lab_id = bas_lab.runner_id
                    break

        finally:
            unset_current_lab()

        if bas_lab_id is not None:
            break
    else:
        print("No active BAS campaign with this agent session ID")
        sys.exit(1)

    return bas_lab_id


#
# 'bas_attack_list_handler' handler
#


def bas_attack_list_handler(args: Any) -> None:
    # Parameters
    session_id = args.session_id
    filter_tactic = args.filter_tactic
    filter_technique = args.filter_technique

    # Retrieve matching bas lab
    lab_id = find_bas_lab_from_session_id(session_id)

    # Set current lab
    set_current_lab(lab_id)
    try:
        show_available_attacks(session_id, filter_tactic, filter_technique)
    finally:
        unset_current_lab()

    print(
        f"[hint] You can launch an attack with: '$ mantis bas attack run -s {session_id} -a ATTACK_NAME'"
    )


def run_attack(
    session_id: str,
    attack_name: str,
    show_output: bool,
    params: Dict[str, str],
):
    # Retrieve matching attacks according to input attack name
    matching_attacks = redteam_api.get_attacks_by_values(
        attack_name=attack_name,
        attack_session_identifier=session_id,
    )

    if not matching_attacks:
        print(f"No matching attack '{attack_name}'")
        sys.exit(1)

    # Retrieve runnable attacks
    runnable_attacks = []
    for attack in matching_attacks:
        if attack["status"] == "runnable":
            runnable_attacks.append(attack)

    if not runnable_attacks:
        print(f"No matching attack '{attack_name}' can be run")
        sys.exit(1)

    if len(runnable_attacks) > 1:
        print(
            f"[+] Multiple attacks match '{attack_name}'. Please choose the ID to run:"
        )

        # FIXME: attack['values'] is currently a string! Do not provide string dict from REST API
        dict_values = json.loads(attack["values"])

        # Retrieve attacks values, after removing redondant attack session infos
        attack_values = dict_values.copy()
        attack_values.pop("attack_session_type", None)
        attack_values.pop("attack_session_source", None)
        attack_values.pop("attack_session_id", None)

        mitre_attack_tactics = ", ".join(
            [tactic["id"] for tactic in attack["worker"]["mitre_data"]["tactics"]]
        )
        mitre_attack_infos = f"{attack['worker']['mitre_data']['technique']['id']} {attack['worker']['mitre_data']['technique']['name']} [{mitre_attack_tactics}]"

        for idx, attack in enumerate(runnable_attacks, start=1):
            print(
                f" \033[1mID\033[0m: {idx:>3} - - \033[1mattack_name\033[0m: {attack['worker']['name']} - \033[1mDescription\033[0m: {attack['worker']['title']} \033[1mATT&CK\033[0m: {mitre_attack_infos} - \033[1mattack_parameters\033[0m:{attack_values}"
            )

        selected_idx_str = input("Selected ID: ")

        try:
            selected_idx = int(selected_idx_str)
        except ValueError:
            print(f"'{selected_idx_str}' is not a valid ID type")
            sys.exit(1)

        if selected_idx not in list(range(1, idx + 1)):
            print(f"'{selected_idx_str}' is not a valid ID")
            sys.exit(1)

        selected_idx = (
            selected_idx - 1
        )  # -1 to handle the shift in the above enumerate()

    else:
        selected_idx = 0

    # Retrieve attack structure based on the selected one
    attack = runnable_attacks[selected_idx]

    # Disable logs emitted by cr_api_client.redteam_api, as we want to rewrite output
    from loguru import logger

    logger.disable("cr_api_client.redteam_api")

    print(f"[+] \033[1mPlaying attack\033[0m: {attack_name}")

    try:
        attack_id = redteam_api.execute_attack_by_id(
            id_attack=attack["idAttack"],
            name=attack["worker"]["name"],
            title=attack["worker"]["title"],
            allow_to_failed=True,
            options=params,
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        logger.enable("cr_api_client.redteam_api")

    # Show attack result
    attack_result = redteam_api.attack_infos(attack_id)
    print(f"[+] \033[1mResult\033[0m: {attack_result['status']}")
    print("[+] \033[1mTimestamps\033[0m:")
    print(f"  - \033[1mstart\033[0m: {attack_result['started_date']} UTC")
    print(f"  - \033[1mend\033[0m:   {attack_result['last_update']} UTC")
    print("[+] \033[1mExecuted commands\033[0m:")
    for command in attack_result["commands"]:
        for k, v in command.items():
            print(f"  - {k}: {v}")
    if show_output:
        print("[+] \033[1mOutput\033[0m:")
        for elt in attack_result["output"]:
            print(f"  - {elt}")


#
# 'bas_attack_run_handler' handler
#


def bas_attack_run_handler(args: Any) -> None:
    # Parameters
    session_id = args.session_id
    attack_name = args.attack_name
    show_output = args.show_output
    params = args.params

    # Parse options to create a dict expected by the redteam API
    def parse_var(s):
        """
        Parse a key, value pair, separated by '='
        That's the reverse of ShellArgs.

        On the command line (argparse) a declaration will typically look like:
            foo=hello
        or
            foo="hello world"
        """
        items = s.split("=")
        key = items[0].strip()  # we remove blanks around keys, as is logical
        if len(items) > 1:
            # rejoin the rest
            value = "=".join(items[1:])
        return (key, value)

    def parse_vars(items):
        """
        Parse a series of key-value pairs and return a dictionary
        """
        d = {}

        if items:
            for item in items:
                key, value = parse_var(item)
                d[key] = value
        return d

    params = parse_vars(params)

    # Retrieve matching bas lab
    lab_id = find_bas_lab_from_session_id(session_id)

    # Set current lab
    set_current_lab(lab_id)
    try:
        run_attack(session_id, attack_name, show_output, params)
    finally:
        unset_current_lab()


def bas_attack_history_handler(args):
    # Parameters
    session_id = args.session_id
    show_output = args.show_output

    attacks = redteam_api.list_attacks()
    for attack in attacks:

        # Check if the attack has been previously executed
        if attack["status"] in ["runnable"]:
            continue

        # Check if the attack is BAS compatible
        if (
            ("worker" not in attack)
            or ("bas_compat" not in attack["worker"])
            or (attack["worker"]["bas_compat"] is False)
        ):
            continue

        # FIXME: attack['values'] is currently a string! Do not provide string dict from REST API
        dict_values = json.loads(attack["values"])
        if not isinstance(dict_values, dict):
            continue

        # Check if the attack is part if the current agent session
        if "attack_session_id" not in dict_values:
            continue
        attack_session_id = dict_values["attack_session_id"]
        if attack_session_id != session_id:
            continue

        # Show attack result
        attack_result = redteam_api.attack_infos(attack["idAttack"])
        print(f"[+] \033[1mAttack\033[0m: {attack_result['worker']['name']}")
        print(f"[+] \033[1mResult\033[0m: {attack_result['status']}")
        print("[+] \033[1mTimestamps\033[0m:")
        print(f"  - \033[1mstart\033[0m: {attack_result['started_date']} UTC")
        print(f"  - \033[1mend\033[0m:   {attack_result['last_update']} UTC")
        print("[+] \033[1mExecuted commands\033[0m:")
        for command in attack_result["commands"]:
            for k, v in command.items():
                print(f"  - {k}: {v}")
        if show_output:
            print("[+] \033[1mOutput\033[0m:")
            for elt in attack_result["output"]:
                print(f"  - {elt}")
        print("----")


#
# 'bas_attack_custom_run_handler' handler
#


def bas_attack_custom_run_handler(args: Any) -> None:
    # Parameters
    session_id = args.session_id
    command = args.command
    atr_file = args.atr_file
    background = args.background

    # Sanity check
    if command is None and atr_file is None:
        print("Either --command or --atr_file should be used")
        sys.exit(1)

    if command is not None and atr_file is not None:
        print("Either --command or --atr_file should be used, but not both")
        sys.exit(1)

    if atr_file is not None and background is True:
        print("--background is not compatible with --atr_file option")
        sys.exit(1)

    # Retrieve matching bas lab
    lab_id = find_bas_lab_from_session_id(session_id)

    # Set current lab
    set_current_lab(lab_id)
    try:
        if command is not None:
            redteam_command_execute_handler(args)
        else:
            redteam_atomic_handler(args)

            print(
                f"[hint] You can retrieve test results with: '$ mantis bas attack-custom history -s {session_id}'"
            )
    finally:
        unset_current_lab()


#
# 'bas_attack_custom_history_handler' handler
#


def bas_attack_custom_history_handler(args: Any) -> None:
    # Parameters
    session_id = args.session_id

    # Retrieve matching bas lab
    lab_id = find_bas_lab_from_session_id(session_id)

    # Set current lab
    set_current_lab(lab_id)
    try:
        redteam_command_history_handler(args)
    finally:
        unset_current_lab()


#
# 'bas_attack_custom_get_handler' handler
#


def bas_attack_custom_get_handler(args: Any) -> None:
    # Parameters
    session_id = args.session_id

    # Retrieve matching bas lab
    lab_id = find_bas_lab_from_session_id(session_id)

    # Set current lab
    set_current_lab(lab_id)
    try:
        redteam_command_get_handler(args)
    finally:
        unset_current_lab()


def add_bas_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # --------------------
    # --- Scenario API options (bas)
    # --------------------

    parser_bas = subparsers.add_parser(
        "bas",
        help="BAS API related commands",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_bas = parser_bas.add_subparsers()

    # 'bas_create' command
    parser_bas_create = subparsers_bas.add_parser(
        "create",
        help="Create a BAS campaign and launch its infrastructure",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_create.set_defaults(func=bas_create_handler)
    parser_bas_create.add_argument(
        "--workspace_id",
        dest="workspace_id",
        help="The workspace ID on which you want to create the BAS lab infrastructure",
    )

    # 'bas_list' command
    parser_bas_list = subparsers_bas.add_parser(
        "list",
        help="List BAS campaigns (by default, only active campaigns are displayed)",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_list.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="all_labs",
        help="Include non active BAS campaigns",
    )
    parser_bas_list.set_defaults(func=bas_list_handler)

    # 'bas_info' command
    parser_bas_info = subparsers_bas.add_parser(
        "info",
        help="Info of BAS campaign",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_info.set_defaults(func=bas_info_handler)
    parser_bas_info.add_argument("campaign_id", type=str, help="The BAS campaign ID")

    # 'bas_stop' command
    parser_bas_stop = subparsers_bas.add_parser(
        "stop",
        help="Stop an active BAS campaign",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_stop.set_defaults(func=bas_stop_handler)
    parser_bas_stop.add_argument("campaign_id", type=str, help="The BAS campaign ID")

    # bas attack subparser
    parser_bas_attack = subparsers_bas.add_parser(
        "attack",
        help="BAS attack related commands",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_bas_attack = parser_bas_attack.add_subparsers()
    parser_bas_attack.set_defaults(func=lambda _: parser_bas_attack.print_help())

    # 'bas_attack_list' command
    parser_bas_attack_list = subparsers_bas_attack.add_parser(
        "list",
        help="Show available attacks for a specific BAS agent session",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_attack_list.set_defaults(func=bas_attack_list_handler)
    parser_bas_attack_list.add_argument(
        "--session_id",
        "-s",
        type=str,
        help="The BAS agent session ID",
        required=True,
    )
    parser_bas_attack_list.add_argument(
        "-T",
        "--tactic",
        action="store",
        nargs="?",
        dest="filter_tactic",
        help="Filter attack according to ATT&CK tactics, either a name or its ID",
    )
    parser_bas_attack_list.add_argument(
        "-t",
        "--technique",
        action="store",
        nargs="?",
        dest="filter_technique",
        help="Filter attack according to ATT&CK technique ID",
    )

    # 'bas_attack_run' command
    parser_bas_attack_run = subparsers_bas_attack.add_parser(
        "run",
        help="Run an attack on a specific BAS agent session",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_attack_run.set_defaults(func=bas_attack_run_handler)
    parser_bas_attack_run.add_argument(
        "--session_id",
        "-s",
        type=str,
        help="The BAS agent session ID",
        required=True,
    )
    parser_bas_attack_run.add_argument(
        "--attack_name",
        "-a",
        type=str,
        help="The attack name to run (from 'mantis bas attack list' command)",
        required=True,
    )
    parser_bas_attack_run.add_argument(
        "--show_output",
        "-o",
        help="Display attack output (can result in lengthy output)",
        action="store_true",
    )
    parser_bas_attack_run.add_argument(
        "--params",
        "-p",
        metavar="KEY=VALUE",
        nargs="+",
        help="Set a number of key-value attack parameters "
        "in the form '--params key1=var1 key2=var2'. "
        "If a value contains spaces, you should use double quotes: "
        'key="a var".',
    )

    # 'bas_attack_history' command
    parser_bas_attack_history = subparsers_bas_attack.add_parser(
        "history",
        help="Attack history on a specific BAS agent session",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_attack_history.set_defaults(func=bas_attack_history_handler)
    parser_bas_attack_history.add_argument(
        "--session_id",
        "-s",
        type=str,
        help="The BAS agent session ID",
        required=True,
    )
    parser_bas_attack_history.add_argument(
        "--show_output",
        "-o",
        help="Display attack output (can result in lengthy output)",
        action="store_true",
    )

    # bas attack-custom subparser
    parser_bas_attack_custom = subparsers_bas.add_parser(
        "attack-custom",
        help="BAS attack-custom related commands",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_bas_attack_custom = parser_bas_attack_custom.add_subparsers()
    parser_bas_attack_custom.set_defaults(
        func=lambda _: parser_bas_attack_custom.print_help()
    )

    # 'bas_attack_custom_run' command
    parser_bas_attack_custom_run = subparsers_bas_attack_custom.add_parser(
        "run",
        help="Execute custom command on agent session",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_attack_custom_run.add_argument(
        "--session_id",
        "-s",
        help="Attack session identifier",
        required=True,
    )
    parser_bas_attack_custom_run.add_argument(
        "--atr_file",
        "-f",
        help="Import and execute an ATR (Atomic Red Team) file containing commands",
    )
    parser_bas_attack_custom_run.add_argument(
        "--command",
        "-c",
        help="Command to execute, must be surrounded by quotation marks",
    )
    parser_bas_attack_custom_run.add_argument(
        "--background",
        "-b",
        help="Execute command in background or not (Invoke-WmiMethod on Windows and & on Linux.)",
        default="false",
    )
    parser_bas_attack_custom_run.add_argument(
        "--timeout",
        "-t",
        help="Maximum time (seconds) to wait result command before timeout",
        default=60,
    )
    parser_bas_attack_custom_run.set_defaults(func=bas_attack_custom_run_handler)

    # 'bas_attack_custom_history' command
    parser_bas_attack_custom_history = subparsers_bas_attack_custom.add_parser(
        "history",
        help="Custom attack history on a specific BAS agent session",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_attack_custom_history.add_argument(
        "--session_id",
        "-s",
        help="Attack session identifier",
        required=True,
    )
    parser_bas_attack_custom_history.add_argument(
        "--show_output",
        "-o",
        help="Display attack output (can result in lengthy output)",
        action="store_true",
    )
    parser_bas_attack_custom_history.set_defaults(
        func=bas_attack_custom_history_handler
    )

    # 'bas_attack_custom_get' command
    parser_bas_attack_custom_get = subparsers_bas_attack_custom.add_parser(
        "get",
        help="Get information regarding a specific custom command",
        formatter_class=root_parser.formatter_class,
    )
    parser_bas_attack_custom_get.set_defaults(func=bas_attack_custom_get_handler)
    parser_bas_attack_custom_get.add_argument(
        "--session_id",
        "-s",
        help="Attack session identifier",
        required=True,
    )
    parser_bas_attack_custom_get.add_argument(
        "--command_id",
        "-i",
        help="The command ID",
        type=str,
        required=True,
    )
    parser_bas_attack_custom_get.add_argument(
        "--show_output",
        "-o",
        help="Display attack output (can result in lengthy output)",
        action="store_true",
    )

    parser_bas.set_defaults(func=lambda _: parser_bas.print_help())
