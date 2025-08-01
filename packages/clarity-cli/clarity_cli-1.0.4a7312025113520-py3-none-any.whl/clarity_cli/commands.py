from clarity_cli.outputs import CliOutput, CliTable
from clarity_cli.input import CliInputs
from clarity_cli.helpers import (is_logged_in, get_tests, trigger_test_execution, write_new_profile_to_config,
                                 get_profile_configuration, get_clarity_access_token, get_devices, format_device_state, format_finding_type,
                                 get_params, parse_and_upload_poetry_package, show_test_list, show_plan_list, get_all_executions, get_execution_findings)
from clarity_cli.defs import TableColumn, ThemeColors, CONFIG_FILE, ProfileConfig, InputTypes
from clarity_cli.exceptions import StopCommand
import json


class CliCommands():
    def __init__(self):
        self.out = CliOutput()
        self.input = CliInputs()

    def _get_current_profile_and_config(self, profile=None, override_config_path=None):
        config, profile_name = self.out.run_sync_function("Validate profile...",
                                                          get_profile_configuration, profile=profile, override_config_path=override_config_path)
        return config, profile_name

    def execute(self, ctx, plan_id=None, test_id=None, profile=None, override_config_path=None, project=None, workspace=None, agent_id=None, parameters_file=None):
        """Execute a test from the available tests"""
        self.out.setup_context(ctx)
        self.input.setup_context(ctx)
        config, profile_name = self._get_current_profile_and_config(
            profile, override_config_path)
        web_token = is_logged_in(profile_name)

        project = project or config.project
        workspace = workspace or config.workspace
        agent_id = agent_id or config.agent

        if not project:
            self.out.vprint("project wasn't provided, asking user")
            project = self.input.ask_for_text_input("Project id")
        if not workspace:
            self.out.vprint("workspace id wasn't provided, asking user")
            workspace = self.input.ask_for_text_input("Workspace id")

        self.out.main_message("Test Execution")
        # fetch all available tests/plans
        available_tests_plans, params = self.out.run_sync_function(
            "Getting Tests and Plans...", get_tests, token=web_token, workspace_id=workspace, domain=config.domain)
        self.results, selected_test, selected_plan = self.list_execution_options(
            available_tests_plans, plan_id, test_id)

        execution = selected_test or selected_plan

        self.check_if_iot_required(
            execution, agent_id, web_token, workspace, config.domain)

        test_plan_config = self.configure_flow_params(
            parameters_file, params)
        self.execute_required_action(
            profile_name, execution, config.domain, workspace, project, agent_id, test_plan_config)

    def write_profile_to_config(self, ctx, profile_name=None, client_id=None, client_secret=None, token_endpoint=None,
                                scope=None, project=None, workspace=None, agent_id=None, domain=None, default=None):
        self.out.setup_context(ctx)
        self.input.setup_context(ctx)
        self.out.main_message("New Profile")
        if not profile_name:
            self.out.vprint("profile name wasn't provided, asking user")
            profile_name = self.input.ask_for_text_input("Profile name")
        if not client_id:
            self.out.vprint("client_id wasn't provided, asking user")
            client_id = self.input.ask_for_text_input("Client id")
        if not client_secret:
            self.out.vprint("client_secret wasn't provided, asking user")
            client_secret = self.input.ask_for_password_input("Client secret")
        if not token_endpoint:
            self.out.vprint("token endpoint wasn't provided, asking user")
            token_endpoint = self.input.ask_for_password_input(
                "Token endpoint")
        if not scope:
            self.out.vprint("scope wasn't provided, asking user")
            scope = self.input.ask_for_password_input("Scope")
        if not domain:
            self.out.vprint("domain wasn't provided, asking user")
            domain = self.input.ask_for_text_input("Clarity domain")
        if not project:
            self.out.vprint("project wasn't provided, asking user")
            project = self.input.ask_for_text_input(
                "Project id", optional=True)
        if not workspace:
            self.out.vprint("workspace provided, asking user")
            workspace = self.input.ask_for_text_input(
                "Workspace id", optional=True)
        if not agent_id:
            self.out.vprint("agent_id wasn't provided, asking user")
            agent_id = self.input.ask_for_text_input("Agent id", optional=True)
        if default is None:
            default = self.input.ask_for_confirmation(
                "Set this profile as default?", default=False)
        if profile_name and client_id and client_secret and token_endpoint and scope and domain:
            columns = [TableColumn("Property", ThemeColors.CYAN), TableColumn(
                "Value", ThemeColors.GREEN)]
            table = CliTable("New Profile", columns)
            table_data = [
                {"property": "Profile name", "value": profile_name},
                {"property": "Client id", "value": client_id},
                {"property": "Client secret", "value": client_secret},
                {"property": "Clarity domain", "value": domain},
                {"property": "Default Project id", "value": project},
                {"property": "Default workspace id", "value": workspace},
                {"property": "Default agent id", "value": agent_id},
                {"property": "Is default", "value": str(default)}
            ]
            table.add_data(table_data, headers_mapping={
                           "Property": "property", "Value": "value"})
            table.print_table()
            self.input.ask_for_confirmation(
                "Setup the new profile?", default=True, hard_stop=True)
        else:
            raise StopCommand("Missing property")

        config = ProfileConfig(client_id=client_id, client_secret=client_secret, domain=domain, token_endpoint=token_endpoint, scope=scope,
                               project=project, workspace=workspace, agent_id=agent_id)
        self.out.run_sync_function(f"Configuring new profile {profile_name}...",
                                   write_new_profile_to_config, profile_name=profile_name, default=default, config=config)
        self.out.ok(
            f"New profile {CliOutput.bold(profile_name)} successfully configured")
        self.out.vprint(f"All profiles can be found at: {CONFIG_FILE}")

    def login_using_config_file(self, ctx, profile=None, override_config_path=None):
        self.out.setup_context(ctx)
        self.input.setup_context(ctx)
        config, profile = self._get_current_profile_and_config(
            profile, override_config_path)
        self.out.run_sync_function("Logging in", get_clarity_access_token, profile=profile, client_id=config.client_id,
                                   client_secret=config.client_secret, token_endpoint=config.token_endpoint, scope=config.scope)
        self.out.ok("Successfully logged in!")

    def upload_component_from_package(self, ctx, profile=None, override_config_path=None, component_path=None, default_entrypoint=None, default_running_env=None, pyc=None):
        self.out.setup_context(ctx)
        self.input.setup_context(ctx)
        config, profile_name = self._get_current_profile_and_config(
            profile, override_config_path)
        web_token = is_logged_in(profile_name)
        if not component_path:
            self.out.vprint("component path wasn't provided, asking user")
            component_path = self.input.ask_for_text_input(
                "Component path (path to poetry project directory)")
        parse_and_upload_poetry_package(package_dir=component_path, domain=config.domain, workspace_id=config.workspace,
                                        auth_token=web_token, default_entrypoint=default_entrypoint, default_running_env=default_running_env, pyc=pyc)

    def list_execution_options(self, available_tests_plans, plan_id, test_id):
        # Display available tests in a table
        selected_test = None
        selected_plan = None
        self.selected_test_id = None
        self.selected_plan_id = None
        # If test ID /Plan ID are provided directly, use it
        if plan_id:
            selected_plan = next(
                (plan for plan in available_tests_plans['plans'] if plan["plan_id"] == plan_id), None)
            if not selected_plan:
                raise StopCommand(f"Error: Test with ID '{plan_id}' not found")
            self.input.ask_for_confirmation(
                f"Execute test '{selected_plan['plan_name']}' ({plan_id})?")
            self.selected_plan_id = plan_id
        elif test_id:
            selected_test = next(
                (test for test in available_tests_plans['tests'] if test["test_id"] == test_id), None)
            if not selected_test:
                raise StopCommand(f"Error: Test with ID '{test_id}' not found")

            self.input.ask_for_confirmation(
                f"Execute test '{selected_test['test_name']}' ({test_id})?")
            self.selected_test_id = [test_id]

        # If no test ID provided, use interactive selection
        else:
            show_test_list(available_tests_plans['tests'])
            show_plan_list(available_tests_plans['plans'])
        # Create choices for the test selection
            test_choices = [
                f"{test['test_id']} - {test['test_name']}, {test['test_version']}" for test in available_tests_plans['tests']]
            plan_choices = [
                f"{test['plan_id']} - {test['plan_name']}" for test in available_tests_plans['plans']]
            choices = plan_choices+test_choices
            selected = self.input.ask_for_input_from_list(
                "Select a test or plan to execute", choices)
            # Get the selected test ID
            selected_id = selected.split(' - ')[0]
            selected_test = next(
                (test for test in available_tests_plans['tests'] if test["test_id"] == selected_id), None)
            selected_plan = next(
                (test for test in available_tests_plans['plans'] if test["plan_id"] == selected_id), None)
            if selected_test is None and selected_plan is None:
                raise StopCommand("Error: Could not find what to execute")
            elif selected_test:
                self.selected_test_id = [selected_test['test_id']]
            elif selected_plan:
                self.selected_plan_id = selected_plan['plan_id']
        if self.selected_plan_id is not None:
            self.selected_test_id = selected_plan.get("plan", [])
            self.results = []
            for choice in test_choices:
                for selected_test_plan in self.selected_test_id:
                    if selected_test_plan in choice:
                        # construct a new list
                        test_identity = choice.split(' - ')
                        if len(test_identity) >= 2:
                            name = test_identity[1].strip()
                            self.results.append((selected_test_plan, name))
        return self.results, selected_test, selected_plan

    def check_if_iot_required(self, execution, agent_id, web_token, workspace, domain):
        if (execution or {}).get('iot_device_required'):
            self.out.vprint(f"running the following execution{execution}")
            if not agent_id:
                self.out.vprint("agent id wasn't provided, asking user")
                devices_column = [TableColumn("Name", ThemeColors.CYAN),
                                  TableColumn("ID"),
                                  TableColumn("Version"),
                                  TableColumn("Status")]
                available_devices = self.out.run_sync_function(
                    "Getting devices...", get_devices, token=web_token, workspace_id=workspace, domain=domain)
                devices_by_name = {}
                for device in available_devices:
                    format_device_state(device)
                    devices_by_name[device['device_name']] = device
                devices_table = CliTable("Available Devices", devices_column)
                devices_table.add_data(available_devices,
                                       headers_mapping={"ID": "device_id", "Name": "device_name", "Version": "iot_client_version", "Status": "state"})
                devices_table.print_table()
                agent_name = self.input.ask_for_input_from_list(
                    "Please select an agent id", devices_by_name.keys())
                agent_id = devices_by_name.get(agent_name)
                if 'disconnected' in agent_id.get('state', '').lower():
                    raise StopCommand("Your Device is disconnected")
            if not agent_id:
                raise StopCommand("Agent was not provided, please ")

    def configure_flow_params(self, parameters_file, params):
        if parameters_file:
            self.out.vprint(f"Loading parameters file: {parameters_file}")
            params_from_config = get_params(parameters_file)
        else:
            params_from_config = {}
        test_plan_config = []
        for test in self.results:
            self.out.main_message(
                f"Configure flow parameters for test : {test}")
            test = test[0]
            self.out.vprint(
                f"test flow param config:\n{params[test].get('properties', {})}")
            for param_name, param in params[test].get('properties', {}).items():
                if param.get('type') in list(InputTypes.__members__):
                    input_value = self.input.ask_for_text_input(
                        param_name, default=param.get('default'))
                    if input_value:
                        if params_from_config.get(param_name):
                            self.out.vprint(
                                f"Got param: {param_name} from file, value: {params_from_config[param_name]}")
                            param['default'] = params_from_config[param_name]
                        else:
                            self.out.vprint(
                                f"Got param: {param_name} user: { InputTypes[param['type']].value(input_value)}")
                            param['default'] = InputTypes[param['type']].value(
                                input_value)
            test_plan_config.append({
                "params_config": {},
                "test_id": test,
                "test_config": {"variables_config": params[test]},
            })
            if not params[test]:
                self.out.warning("Flow variables weren't found")
        return test_plan_config

    def execute_required_action(self, profile_name, execution, domain, workspace, project, agent_id, test_plan_config):
        # Execute the test (in a real app, this would trigger an actual test)
        web_token = is_logged_in(profile_name)
        name = execution.get('test_name') or execution.get('plan_name')
        execution_url = self.out.run_sync_function(f"Executing: {name}...",
                                                   function=trigger_test_execution, domain=domain, token=web_token, workspace=workspace,
                                                   project_id=project, agent_id=agent_id, test_plan_config=test_plan_config)
        self.out.ok(
            f"Successfully executed test: {CliOutput.bold(name)}")
        self.out.print(
            f"[dim]Results will be available in the dashboard: {execution_url}[/dim]")

    def view_all_executions(self, ctx, project_id=None, output_type='table', file_path=None, profile=None, override_config_path=None):
        """View all executions for a project"""
        self.out.setup_context(ctx)
        self.input.setup_context(ctx)
        config, profile_name = self._get_current_profile_and_config(
            profile, override_config_path)
        web_token = is_logged_in(profile_name)

        project_id = project_id or config.project

        if not project_id:
            self.out.vprint("project_id wasn't provided, asking user")
            project_id = self.input.ask_for_text_input("Project ID")

        self.out.main_message("All Executions View")

        # Fetch all executions
        executions_data = self.out.run_sync_function(
            "Getting all executions...", get_all_executions,
            token=web_token, workspace_id=config.workspace, domain=config.domain, project_id=project_id)

        # Save as JSON if file path provided
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(executions_data, f, indent=2)
                self.out.ok(f"Executions data saved to {file_path}")
            except Exception as e:
                self.out.error(f"Failed to save to file: {str(e)}")
                raise StopCommand(f"Failed to save executions data to {file_path}")

        # Display output based on format
        if output_type == 'json':
            self.out.print(json.dumps(executions_data, indent=2))
        else:  # table format
            self._display_executions_table(executions_data)

    def _display_executions_table(self, executions):
        """Display executions data in table format"""
        if not executions:
            self.out.warning("No executions found.")
            return

        execution_columns = [
            TableColumn("Execution number", ThemeColors.RED),
            TableColumn("Execution ID", ThemeColors.CYAN),
            TableColumn("Status", ThemeColors.GREEN),
            TableColumn("Start Time", ThemeColors.YELLOW),
            TableColumn("End Time", ThemeColors.YELLOW)
        ]

        executions_table = CliTable("All Executions", execution_columns)
        executions_table.add_data(
            executions,
            headers_mapping={
                "Execution number": "execution_counter",
                "Execution ID": "execution_id",
                "Status": "execution_status",
                "Start Time": "start_time",
                "End Time": "end_time"
            },
        )
        executions_table.print_table()

    def get_findings(self, ctx, execution_id=None, output_type='table', file_path=None, profile=None, override_config_path=None):
        """Get findings for a specific execution"""
        self.out.setup_context(ctx)
        self.input.setup_context(ctx)
        config, profile_name = self._get_current_profile_and_config(
            profile, override_config_path)
        web_token = is_logged_in(profile_name)

        if not execution_id:
            self.out.vprint("execution_id wasn't provided, asking user")
            execution_id = self.input.ask_for_text_input("Execution ID")

        self.out.main_message("Execution Findings")

        # Fetch execution findings
        findings_data = self.out.run_sync_function(
            "Getting execution findings...", get_execution_findings,
            token=web_token, workspace_id=config.workspace, domain=config.domain, execution_id=execution_id)

        # Save as JSON if file path provided
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(findings_data, f, indent=2)
                self.out.ok(f"Findings data saved to {file_path}")
            except Exception as e:
                self.out.error(f"Failed to save to file: {str(e)}")
                raise StopCommand(f"Failed to save findings data to {file_path}")

        # Display output based on format
        if output_type == 'json':
            self.out.print(json.dumps(findings_data, indent=2))
        else:  # table format
            self._display_findings_table(findings_data)

    def _display_findings_table(self, findings_data):
        """Display findings data in table format"""
        findings = findings_data.get('findings', [])
        if not findings:
            self.out.warning("No findings found.")
            return
        finding_to_display = []
        for finding in findings:
            finding_to_display.append({
                "finding_type": format_finding_type(finding['type']),
                "step_name": finding['step_name'],
                "purpose": finding['data']['purpose'],
                "description": finding['data']['description'],
                "topic": finding['data']['topic'],
            })
        findings_columns = [
            TableColumn("Finding type"),
            TableColumn("Step name", ThemeColors.CYAN),
            TableColumn("Purpose", ThemeColors.GREEN),
            TableColumn("Description", ThemeColors.YELLOW),
            TableColumn("Topic", ThemeColors.GREEN),
        ]

        findings_table = CliTable("Execution Findings", findings_columns)
        findings_table.add_data(
            finding_to_display,
            headers_mapping={
                "Finding type": "finding_type",
                "Step name": "step_name",
                "Purpose": "purpose",
                "Description": "description",
                "Topic": "topic",
            },
        )
        findings_table.print_table()
