import contextlib
import io
import os
import shutil
import subprocess
import unittest

from pymetacode import cli, configuration, utils


class TestCli(unittest.TestCase):
    def setUp(self):
        self.cli = cli.Cli()
        self.config_filename = "package_config.yaml"
        self.package_name = "foo"

    def tearDown(self):
        if os.path.exists(self.config_filename):
            os.remove(self.config_filename)
        if os.path.exists(self.package_name):
            shutil.rmtree(self.package_name)

    def test_instantiate_class(self):
        pass

    def test_call_with_command_sets_command_property(self):
        command = "help"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command=command)
        self.assertEqual(command, self.cli.command)

    def test_call_with_options_sets_options_property(self):
        options = "config"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(options=options)
        self.assertEqual(options, self.cli.options)

    def test_call_without_command_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call()
        content = stdout.getvalue()
        self.assertIn("General usage:", content)

    def test_call_with_unknown_command_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="foo")
        content = stdout.getvalue()
        self.assertIn("General usage:", content)

    def test_call_with_help_command_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="help")
        content = stdout.getvalue()
        self.assertIn("General usage:", content)

    def test_call_help_write_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="help", options=["write"])
        content = stdout.getvalue()
        self.assertIn("Usage for write command:", content)

    def test_call_help_create_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="help", options=["create"])
        content = stdout.getvalue()
        self.assertIn("Usage for create command:", content)

    def test_call_help_add_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="help", options=["add"])
        content = stdout.getvalue()
        self.assertIn("Usage for add command:", content)

    def test_call_write_writes_config(self):
        self.cli.call(
            command="write",
            options=["config", "to", self.config_filename],
        )
        self.assertTrue(os.path.exists(self.config_filename))

    def test_call_write_with_wrong_options_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="write", options=["foo", "bar", self.config_filename]
            )
        content = stdout.getvalue()
        self.assertIn("Usage for write command:", content)
        self.assertFalse(os.path.exists(self.config_filename))

    def test_call_write_without_options_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="write")
        content = stdout.getvalue()
        self.assertIn("Usage for write command:", content)
        self.assertFalse(os.path.exists(self.config_filename))

    def test_call_write_config_without_destination_uses_default_name(self):
        self.cli.call(command="write", options=["config"])
        self.assertTrue(os.path.exists(self.config_filename))

    def test_call_write_logs_success_message(self):
        with self.assertLogs(__package__, level="INFO") as cm:
            self.cli.call(command="write", options=["config"])
        self.assertIn(
            'Wrote configuration to file "{}"'.format(self.cli.conf_file),
            cm.output[0],
        )

    def test_call_create_creates_package(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        self.assertTrue(
            os.path.exists(os.path.join(self.package_name, self.package_name))
        )

    def test_call_create_copies_package_config_to_package(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        self.assertTrue(
            os.path.exists(
                os.path.join(self.package_name, ".package_config.yaml")
            )
        )

    def test_call_create_with_wrong_options_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["foo", "bar", self.config_filename],
            )
        content = stdout.getvalue()
        self.assertIn("Usage for create command:", content)
        self.assertFalse(
            os.path.exists(os.path.join(self.package_name, self.package_name))
        )

    def test_call_create_without_options_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="create")
        content = stdout.getvalue()
        self.assertIn("Usage for create command:", content)
        self.assertFalse(
            os.path.exists(os.path.join(self.package_name, self.package_name))
        )

    def test_call_create_logs_success_message(self):
        with self.assertLogs(__package__, level="INFO") as cm:
            conf = configuration.Configuration()
            conf.package["name"] = self.package_name
            conf.to_file(self.config_filename)
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        self.assertIn(
            'Created package "{}" in directory "{}"'.format(
                self.package_name, self.package_name
            ),
            cm.output[0],
        )

    def test_call_add_module_adds_module(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            module_name = "bar"
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["module", module_name])
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.package_name, module_name + ".py")
                )
            )

    def test_call_add_module_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            module_name = "bar"
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(command="add", options=["module", module_name])
        self.assertIn('Added module "{}"'.format(module_name), cm.output[0])

    def test_call_add_with_wrong_options_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="add", options=["foo", "module_name"])
        content = stdout.getvalue()
        self.assertIn("Usage for add command:", content)

    def test_call_add_without_options_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(command="add")
        content = stdout.getvalue()
        self.assertIn("Usage for add command:", content)

    def test_call_add_class_adds_class(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            class_name = "FooBar"
            module_name = "bar"
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["module", module_name])
                self.cli.call(
                    command="add",
                    options=["class", class_name, "to", module_name],
                )
            module_path = os.path.join(self.package_name, module_name + ".py")
            with open(module_path) as file:
                contents = file.read()
            self.assertIn("class {}:\n".format(class_name), contents)

    def test_call_add_class_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            class_name = "FooBar"
            module_name = "bar"
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["module", module_name])
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(
                    command="add",
                    options=["class", class_name, "to", module_name],
                )
        self.assertIn(
            'Added class "{}" to module "{}"'.format(class_name, module_name),
            cm.output[0],
        )

    def test_call_add_function_adds_function(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            function_name = "foo_bar"
            module_name = "bar"
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(
                    command="add",
                    options=["module", module_name],
                )
                self.cli.call(
                    command="add",
                    options=["function", function_name, "to", module_name],
                )
            module_path = os.path.join(self.package_name, module_name + ".py")
            with open(module_path) as file:
                contents = file.read()
            self.assertIn(
                'def {}():\n    """'.format(function_name), contents
            )

    def test_call_add_function_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            function_name = "foo_bar"
            module_name = "bar"
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["module", module_name])
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(
                    command="add",
                    options=["function", function_name, "to", module_name],
                )
        self.assertIn(
            'Added function "{}" to module "{}"'.format(
                function_name, module_name
            ),
            cm.output[0],
        )

    def test_call_add_gui_adds_gui(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["gui"])
            self.assertTrue(
                os.path.exists(os.path.join(self.package_name, "gui"))
            )

    def test_call_add_gui_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(command="add", options=["gui"])
        self.assertIn("Added GUI", cm.output[0])

    def test_call_add_window_adds_window(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["gui"])
                self.cli.call(command="add", options=["window", "test"])
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.package_name, "gui", "testwindow.py")
                )
            )

    def test_call_add_window_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(command="add", options=["gui"])
                self.cli.call(command="add", options=["window", "test"])
        self.assertIn("Added testwindow to GUI", cm.output[1])

    def test_call_add_subpackage_adds_subpackage(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["subpackage", "foo"])
            self.assertTrue(
                os.path.exists(os.path.join(self.package_name, "foo"))
            )

    def test_call_add_subpackage_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(command="add", options=["subpackage", "foo"])
        self.assertIn('Added subpackage "foo"', cm.output[0])

    def test_call_add_widget_adds_widget(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["gui"])
                self.cli.call(command="add", options=["widget", "test"])
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.package_name, "gui", "test_widget.py")
                )
            )

    def test_call_add_widget_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(command="add", options=["gui"])
                self.cli.call(command="add", options=["widget", "test"])
        self.assertIn("Added test_widget to GUI", cm.output[1])

    def test_call_add_dialog_adds_widget(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with contextlib.redirect_stdout(io.StringIO()):
                self.cli.call(command="add", options=["gui"])
                self.cli.call(command="add", options=["dialog", "test"])
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.package_name, "gui", "test_dialog.py")
                )
            )

    def test_call_add_dialog_logs_success_message(self):
        conf = configuration.Configuration()
        conf.package["name"] = self.package_name
        conf.to_file(self.config_filename)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cli.call(
                command="create",
                options=["package", "from", self.config_filename],
            )
        with utils.change_working_dir(self.package_name):
            with self.assertLogs(__package__, level="INFO") as cm:
                self.cli.call(command="add", options=["gui"])
                self.cli.call(command="add", options=["dialog", "test"])
        self.assertIn("Added test_dialog to GUI", cm.output[1])


class TestConsoleEntryPoint(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(cli.Cli().conf_file):
            os.remove(cli.Cli().conf_file)

    def test_call_without_command_prints_help(self):
        result = subprocess.run(["pymeta"], capture_output=True, text=True)
        self.assertIn("General usage:", result.stdout)

    def test_call_help_prints_help(self):
        result = subprocess.run(
            ["pymeta", "help"], capture_output=True, text=True
        )
        self.assertIn("General usage:", result.stdout)

    def test_call_help_write_prints_help(self):
        result = subprocess.run(
            ["pymeta", "help", "write"], capture_output=True, text=True
        )
        self.assertIn("Usage for write command:", result.stdout)

    def test_call_write_prints_log_info(self):
        result = subprocess.run(
            ["pymeta", "write", "config"], capture_output=True, text=True
        )
        self.assertIn("Wrote configuration to file", result.stdout)
