# -*- coding: utf-8 -*-
import base64
import math
import os
from pathlib import Path

import robot
import inspect
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.mobilecommand import MobileCommand as Command
from robot.utils import abspath
from selenium.common import InvalidArgumentException

from AppiumLibrary.utils import ApplicationCache
from .keywordgroup import KeywordGroup

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class _ApplicationManagementKeywords(KeywordGroup):
    def __init__(self):
        self._cache = ApplicationCache()
        self._timeout_in_secs = float(5)

    # Public, open and close
    def appium_get_current_application(self):
        current = self._cache.current
        if current is self._cache._no_current:
            return None
        return current

    def appium_get_session_index(self):
        current_index = self._cache.current_index
        return current_index

    def appium_close_application(self, ignore_fail=False, quit_app=True):
        self._cache.close(ignore_fail, quit_app)

    def appium_close_all_applications(self, ignore_fail=True, quit_app=True):
        self._cache.close_all(ignore_fail, quit_app)

    def appium_save_source(self, file_path='file_source.txt'):
        page_source = self.get_source()
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(page_source)

    def appium_execute_powershell_command(self, command, handle_exception=False):
        """
        Executes a PowerShell command using Appium's execute_script method.

        Note:
            PowerShell command execution must be allowed on the Appium server.
            For this, Appium must be started with the `--relaxed-security` flag:
                appium --relaxed-security

        Args:
            command (str): The PowerShell command to be executed.
            handle_exception (bool): If True, return the exception object on error. Otherwise, return None.

        Returns:
            str | dict | Exception: The result of the execution or the exception object.

        Raises:
            Exception: If handle_exception is False and an error occurs.
        """
        try:
            driver = self._current_application()
            result = driver.execute_script("powerShell", {"command": command})
            return result
        except Exception as exc:
            if handle_exception:
                return exc
            raise

    def appium_execute_powershell_script(self, ps_script=None, file_path=None, handle_exception=False):
        """
        Executes a PowerShell script using Appium's execute_script method.

        Note:
            PowerShell command execution must be allowed on the Appium server.
            For this, Appium must be started with the `--relaxed-security` flag:
                appium --relaxed-security

        Args:
            ps_script (str): The full PowerShell script to be executed.
            file_path (str): The file ps1 to be executed.
            handle_exception (bool): If True, return the exception object on failure. If False, return None on failure.

        Returns:
            str | dict | Exception: The result of the script execution or the exception object.

        Raises:
            Exception: If handle_exception is False and an error occurs.
        """
        try:
            if file_path:
                file_path = self._absnorm(file_path)
                with open(file_path, encoding='UTF-8', errors='strict', newline="") as f:
                    ps_script = f.read().replace("\r\n", "\n")
            driver = self._current_application()
            result = driver.execute_script("powerShell", {"script": ps_script})
            return result
        except Exception as exc:
            if handle_exception:
                return exc
            raise

    def appium_pull_file(self, path: str, save_path: str = None) -> str:
        """Retrieves the file at `path`.

        Powershell command must be allowed. eg: appium --relaxed-security

        Args:
            path: the path to the file on the device, eg: c:/users/user1/desktop/screenshot_file.png
            save_path: path to save, eg: /Users/user1/desktop/screenshot.png

        Returns:
            The file's contents encoded as Base64.
        """

        # base64data = self._current_application().pull_file(path)
        base64data = self._current_application().execute(Command.PULL_FILE, {'path': path})['value']

        if save_path:
            with open(save_path, "wb") as file:
                file.write(base64.b64decode(base64data))

        return base64data

    def appium_pull_folder(self, path: str, save_path_as_zip: str = '') -> str:
        """Retrieves a folder at `path`.

        Powershell command must be allowed. eg: appium --relaxed-security

        Args:
            path: the path to the folder on the device. eg: c:/users/user1/desktop/folder1
            save_path_as_zip: zip file. eg: /Users/user1/desktop/file.zip

        Returns:
            The folder's contents zipped and encoded as Base64.
        """
        # base64data = self._current_application().pull_folder(path)
        base64data = self._current_application().execute(Command.PULL_FOLDER, {'path': path})['value']

        if save_path_as_zip:
            with open(save_path_as_zip, "wb") as file:
                file.write(base64.b64decode(base64data))

        return base64data

    def appium_push_file(self, destination_path: str, source_path: str = None, base64data: str = None):
        """Puts the data from the file at `source_path`, encoded as Base64, in the file specified as `path`.

        Specify either `base64data` or `source_path`, if both specified default to `source_path`

        Powershell command must be allowed. eg: appium --relaxed-security

        Args:
            destination_path: the location on the device/simulator where the local file contents should be saved.
            eg: c:/users/user1/desktop/screenshot_file.png
            base64data: file contents, encoded as Base64, to be written
            to the file on the device/simulator. Eg: iVBORw0KGgoAAAANSUh...
            source_path: local file path for the file to be loaded on device. Eg: /Users/user1/desktop/source_file.png

        Returns:
            base64data
        """
        if source_path is None and base64data is None:
            raise InvalidArgumentException('Must either pass base64 data or a local file path')

        if source_path is not None:
            try:
                with open(source_path, 'rb') as f:
                    file_data = f.read()
            except IOError as e:
                message = f'source_path "{source_path}" could not be found. Are you sure the file exists?'
                raise InvalidArgumentException(message) from e
            base64data = base64.b64encode(file_data).decode('utf-8')

        # result = self._current_application().push_file(destination_path, base64data, source_path)

        self._current_application().execute(Command.PUSH_FILE, {'path': destination_path, 'data': base64data})

        return base64data

    def appium_transfer_file(self, file_path, remote_path):
        """
        Streams a binary file, base64-encodes it chunk by chunk,
        and sends it directly to a remote machine via PowerShell commands.

        Powershell command must be allowed. eg: appium --relaxed-security

        file_path: source file path, eg: c:/users/user1/desktop/screenshot_file.png
        remote_path: destination path, eg: c:/users/user1/download/screenshot_file.png
        """
        file_path = Path(file_path)
        remote_path = str(remote_path)
        remote_b64_path = remote_path + ".b64.tmp"
        chunk_size = 6000  # chunk size in raw bytes (will expand when base64 encoded)

        # 1. Ensure remote parent directory exists
        remote_directory = str(Path(remote_path).parent)
        mkdir_cmd = f'New-Item -Path "{remote_directory}" -ItemType Directory -Force'
        self.execute_script("powerShell", command=mkdir_cmd)
        self._info(f"Ensured remote directory: {remote_directory}")

        # 2. Open and stream file, encoding and sending each chunk
        with open(file_path, "rb") as f:
            chunk_index = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                chunk_b64 = base64.b64encode(chunk).decode('utf-8')
                escaped_chunk = chunk_b64.replace("`", "``").replace('"', '`"')
                ps = f'Add-Content -Path "{remote_b64_path}" -Value "{escaped_chunk}"'
                self.execute_script("powerShell", command=ps)
                chunk_index += 1
                self._info(f"Sent chunk {chunk_index}")

        # 3. Decode and write binary file on remote side
        decode_script = (
            f'[IO.File]::WriteAllBytes("{remote_path}", '
            f'[Convert]::FromBase64String((Get-Content "{remote_b64_path}" -Raw)))'
        )
        self.execute_script("powerShell", command=decode_script)
        self._info(f"File written to: {remote_path}")

        # 4. Optional cleanup
        cleanup_script = f'Remove-Item "{remote_b64_path}" -ErrorAction SilentlyContinue'
        self.execute_script("powerShell", command=cleanup_script)
        self._info("Cleaned up temporary base64 file.")

    def appium_split_and_push_file(self, source_path: str, remote_path: str, chunk_size_mb: int = 20):
        """
        Splits a binary file into chunks, pushes each to a remote machine via Appium,
        then executes a PowerShell script remotely to recombine and clean up chunk files.

        Powershell command must be allowed. eg: appium --relaxed-security

        Parameters:
            source_path (str): Local path to the binary file.
            remote_path (str): Full remote file path to create from recombination.
            chunk_size_mb (int): Size of each chunk in MB (default: 20MB).
        """
        chunk_size = chunk_size_mb * 1024 * 1024
        file_size = os.path.getsize(source_path)

        file_name = os.path.basename(source_path)
        remote_dir = os.path.dirname(remote_path)
        total_chunks = math.ceil(file_size / chunk_size)
        # chunk_index_digits = max(4, len(str(total_chunks - 1)))  # at least 4 digits
        chunk_index_digits = len(str(total_chunks - 1))

        self._info(f"Splitting '{file_name}' ({file_size} bytes) into {total_chunks} chunks of {chunk_size_mb}MB each")

        # Step 1: Split and push chunks
        with open(source_path, "rb") as f:
            for index in range(total_chunks):
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                b64_chunk = base64.b64encode(chunk).decode("utf-8")
                chunk_suffix = f"{index:0{chunk_index_digits}d}"
                remote_chunk_path = os.path.join(remote_dir, f"{file_name}.part{chunk_suffix}")

                self.appium_push_file(destination_path=remote_chunk_path, base64data=b64_chunk)
                self._info(f"Pushed chunk {chunk_suffix} to {remote_chunk_path}")

        # Step 2: Build PowerShell recombine script
        escaped_dir = remote_dir.replace("'", "''")
        escaped_out = remote_path.replace("'", "''")
        escaped_base = file_name.replace("'", "''")
        pad_format = f"D{chunk_index_digits}"

        ps_script_lines = [
            f"$out = [System.IO.File]::OpenWrite('{escaped_out}')",
            "$out.SetLength(0)",
            f"for ($i = 0; $i -lt {total_chunks}; $i++) {{",
            f"    $chunkName = '{escaped_base}.part' + $i.ToString('{pad_format}')",
            f"    $chunkPath = Join-Path '{escaped_dir}' $chunkName",
            "    if (-not (Test-Path $chunkPath)) { throw \"Missing chunk: $chunkPath\" }",
            "    $in = [System.IO.File]::OpenRead($chunkPath)",
            "    $buffer = New-Object byte[] (1MB)",
            "    while (($n = $in.Read($buffer, 0, $buffer.Length)) -gt 0) {",
            "        $out.Write($buffer, 0, $n)",
            "    }",
            "    $in.Close()",
            "}",
            "$out.Close()",
            "",
            f"for ($i = 0; $i -lt {total_chunks}; $i++) {{",
            f"    $chunkName = '{escaped_base}.part' + $i.ToString('{pad_format}')",
            f"    $chunkPath = Join-Path '{escaped_dir}' $chunkName",
            "    Remove-Item -Path $chunkPath -Force -ErrorAction SilentlyContinue",
            "}",
            f"Write-Output 'Combine and cleanup complete: {escaped_out}'"
        ]

        ps_script = "\n".join(ps_script_lines)

        # Step 3: Execute recombine script remotely
        self._info("Combining chunks and cleaning up on remote machine...")
        result = self.appium_execute_powershell_script(ps_script)
        self._info(f"Remote PowerShell result: {result}")
        return escaped_out

    def close_application(self):
        """Closes the current application and also close webdriver session."""
        self._info('Closing application with session id %s' % self._current_application().session_id)
        self._cache.close()

    def close_all_applications(self, ignore_fail=True):
        """Closes all open applications.

        This keyword is meant to be used in test or suite teardown to
        make sure all the applications are closed before the test execution
        finishes.

        After this keyword, the application indices returned by `Open Application`
        are reset and start from `1`.
        """

        self._info('Closing all applications')
        self._cache.close_all(ignore_fail)

    def open_application(self, remote_url, alias=None, **kwargs):
        """Opens a new application to given Appium server.
        Capabilities of appium server, Android and iOS,
        Please check https://appium.io/docs/en/2.1/cli/args/
        | *Option*            | *Man.* | *Description*     |
        | remote_url          | Yes    | Appium server url |
        | alias               | no     | alias             |
        | strict_ssl          | No     | allows you to send commands to an invalid certificate host like a self-signed one. |

        Examples:
        | Open Application | http://localhost:4723/wd/hub | alias=Myapp1         | platformName=iOS      | platformVersion=7.0            | deviceName='iPhone Simulator'           | app=your.app                         |
        | Open Application | http://localhost:4723/wd/hub | alias=Myapp1         | platformName=iOS      | platformVersion=7.0            | deviceName='iPhone Simulator'           | app=your.app                         | strict_ssl=False         |
        | Open Application | http://localhost:4723/wd/hub | platformName=Android | platformVersion=4.2.2 | deviceName=192.168.56.101:5555 | app=${CURDIR}/demoapp/OrangeDemoApp.apk | appPackage=com.netease.qa.orangedemo | appActivity=MainActivity |
        """

        desired_caps = AppiumOptions().load_capabilities(caps=kwargs)
        application = webdriver.Remote(str(remote_url), options=desired_caps)

        self._info('Opened application with session id %s' % application.session_id)

        return self._cache.register(application, alias)

    def switch_application(self, index_or_alias):
        """Switches the active application by index or alias.

        `index_or_alias` is either application index (an integer) or alias
        (a string). Index is got as the return value of `Open Application`.

        This keyword returns the index of the previous active application,
        which can be used to switch back to that application later.

        Example:
        | ${appium1}=              | Open Application  | http://localhost:4723/wd/hub                   | alias=MyApp1 | platformName=iOS | platformVersion=7.0 | deviceName='iPhone Simulator' | app=your.app |
        | ${appium2}=              | Open Application  | http://localhost:4755/wd/hub                   | alias=MyApp2 | platformName=iOS | platformVersion=7.0 | deviceName='iPhone Simulator' | app=your.app |
        | Click Element            | sendHello         | # Executed on appium running at localhost:4755 |
        | Switch Application       | ${appium1}        | # Switch using index                           |
        | Click Element            | ackHello          | # Executed on appium running at localhost:4723 |
        | Switch Application       | MyApp2            | # Switch using alias                           |
        | Page Should Contain Text | ackHello Received | # Executed on appium running at localhost:4755 |

        """
        old_index = self._cache.current_index
        if index_or_alias is None:
            self._cache.close()
        else:
            self._cache.switch(index_or_alias)
        return old_index

    def launch_application(self):
        """*DEPRECATED!!* in selenium v4, use `Activate Application` keyword.

        Launch application. Application can be launched while Appium session running.
        This keyword can be used to launch application during test case or between test cases.

        This keyword works while `Open Application` has a test running. This is good practice to `Launch Application`
        and `Quit Application` between test cases. As Suite Setup is `Open Application`, `Test Setup` can be used to `Launch Application`

        Example (syntax is just a representation, refer to RF Guide for usage of Setup/Teardown):
        | [Setup Suite] |
        |  | Open Application | http://localhost:4723/wd/hub | platformName=Android | deviceName=192.168.56.101:5555 | app=${CURDIR}/demoapp/OrangeDemoApp.apk |
        | [Test Setup] |
        |  | Launch Application |
        |  |  | <<<test execution>>> |
        |  |  | <<<test execution>>> |
        | [Test Teardown] |
        |  | Quit Application |
        | [Suite Teardown] |
        |  | Close Application |

        See `Quit Application` for quiting application but keeping Appium sesion running.
        """
        driver = self._current_application()
        driver.launch_app()

    def quit_application(self):
        """*DEPRECATED!!* in selenium v4, check `Close Application` keyword.

        Close application. Application can be quit while Appium session is kept alive.
        This keyword can be used to close application during test case or between test cases.

        See `Launch Application` for an explanation.

        """
        driver = self._current_application()
        driver.close_app()

    def reset_application(self):
        """*DEPRECATED!!* in selenium v4, check `Terminate Application` keyword.

        Reset application. Open Application can be reset while Appium session is kept alive.
        """
        driver = self._current_application()
        driver.reset()

    def remove_application(self, application_id):
        """ Removes the application that is identified with an application id

        Example:
        | Remove Application |  com.netease.qa.orangedemo |

        """
        driver = self._current_application()
        driver.remove_app(application_id)

    def get_appium_timeout(self):
        """Gets the timeout in seconds that is used by various keywords.

        See `Set Appium Timeout` for an explanation."""
        return robot.utils.secs_to_timestr(self._timeout_in_secs)

    def set_appium_timeout(self, seconds):
        """Sets the timeout in seconds used by various keywords.

        There are several `Wait ...` keywords that take timeout as an
        argument. All of these timeout arguments are optional. The timeout
        used by all of them can be set globally using this keyword.

        The previous timeout value is returned by this keyword and can
        be used to set the old value back later. The default timeout
        is 5 seconds, but it can be altered in `importing`.

        Example:
        | ${orig timeout} = | Set Appium Timeout | 15 seconds |
        | Open page that loads slowly |
        | Set Appium Timeout | ${orig timeout} |
        """
        old_timeout = self.get_appium_timeout()
        self._timeout_in_secs = robot.utils.timestr_to_secs(seconds)
        return old_timeout

    def get_appium_sessionId(self):
        """Returns the current session ID as a reference"""
        self._info("Appium Session ID: " + self._current_application().session_id)
        return self._current_application().session_id

    def get_source(self):
        """Returns the entire source of the current page."""
        return self._current_application().page_source

    def log_source(self, loglevel='INFO'):
        """Logs and returns the entire html source of the current page or frame.

        The `loglevel` argument defines the used log level. Valid log levels are
        `WARN`, `INFO` (default), `DEBUG`, `TRACE` and `NONE` (no logging).
        """
        ll = loglevel.upper()
        if ll == 'NONE':
            return ''
        else:
            if "run_keyword_and_ignore_error" not in [check_error_ignored[3] for check_error_ignored in
                                                      inspect.stack()]:
                source = self._current_application().page_source
                self._log(source, ll)
                return source
            else:
                return ''

    def execute_script(self, script, **kwargs):
        """
        Execute a variety of native, mobile commands that aren't associated
        with a specific endpoint. See [https://appium.io/docs/en/commands/mobile-command/|Appium Mobile Command]
        for more details.

        Example:
        | &{scrollGesture}  |  create dictionary  |  left=${50}  |  top=${150}  |  width=${50}  |  height=${200}  |  direction=down  |  percent=${100}  |
        | Sleep             |  1                  |
        | Execute Script    |  mobile: scrollGesture  |  &{scrollGesture}  |

        Updated in AppiumLibrary 2
        """
        if kwargs:
            self._info(f"Provided dictionary: {kwargs}")

        return self._current_application().execute_script(script, kwargs)

    def execute_async_script(self, script, **kwargs):
        """
        Inject a snippet of Async-JavaScript into the page for execution in the
        context of the currently selected frame (Web context only).

        The executed script is assumed to be asynchronous and must signal that is done by
        invoking the provided callback, which is always provided as the final argument to the
        function.

        The value to this callback will be returned to the client.

        Check `Execute Script` for example kwargs usage

        Updated in AppiumLibrary 2
        """
        if kwargs:
            self._info(f"Provided dictionary: {kwargs}")

        return self._current_application().execute_async_script(script, kwargs)

    def execute_adb_shell(self, command, *args):
        """
        Execute ADB shell commands

        Android only.

        - _command_ - The ABD shell command
        - _args_ - Arguments to send to command

        Returns the exit code of ADB shell.

        Requires server flag --relaxed-security to be set on Appium server.
        """
        return self._current_application().execute_script('mobile: shell', {
            'command': command,
            'args': list(args)
        })

    def execute_adb_shell_timeout(self, command, timeout, *args):
        """
        Execute ADB shell commands

        Android only.

        - _command_ - The ABD shell command
        - _timeout_ - Timeout to be applied to command
        - _args_ - Arguments to send to command

        Returns the exit code of ADB shell.

        Requires server flag --relaxed-security to be set on Appium server.
        """
        return self._current_application().execute_script('mobile: shell', {
            'command': command,
            'args': list(args),
            'timeout': timeout
        })

    def go_back(self):
        """Goes one step backward in the browser history."""
        self._current_application().back()

    def lock(self, seconds=5):
        """
        Lock the device for a certain period of time. iOS only.
        """
        self._current_application().lock(robot.utils.timestr_to_secs(seconds))

    def background_app(self, seconds=5):
        """*DEPRECATED!!*  use  `Background Application` instead.
        Puts the application in the background on the device for a certain
        duration.
        """
        self._current_application().background_app(seconds)

    def background_application(self, seconds=5):
        """
        Puts the application in the background on the device for a certain
        duration.
        """
        self._current_application().background_app(seconds)

    def activate_application(self, app_id):
        """
        Activates the application if it is not running or is running in the background.
        Args:
         - app_id - BundleId for iOS. Package name for Android.

        New in AppiumLibrary v2
        """
        self._current_application().activate_app(app_id)

    def terminate_application(self, app_id):
        """
        Terminate the given app on the device

        Args:
         - app_id - BundleId for iOS. Package name for Android.

        New in AppiumLibrary v2
        """
        return self._current_application().terminate_app(app_id)

    def stop_application(self, app_id, timeout=5000, include_stderr=True):
        """
        Stop the given app on the device

        Android only. New in AppiumLibrary v2
        """
        self._current_application().execute_script('mobile: shell', {
            'command': 'am force-stop',
            'args': [app_id],
            'includeStderr': include_stderr,
            'timeout': timeout
        })

    def touch_id(self, match=True):
        """
        Simulate Touch ID on iOS Simulator

        `match` (boolean) whether the simulated fingerprint is valid (default true)

        New in AppiumLibrary 1.5
        """
        self._current_application().touch_id(match)

    def toggle_touch_id_enrollment(self):
        """
        Toggle Touch ID enrolled state on iOS Simulator

        New in AppiumLibrary 1.5
        """
        self._current_application().toggle_touch_id_enrollment()

    def shake(self):
        """
        Shake the device
        """
        self._current_application().shake()

    def portrait(self):
        """
        Set the device orientation to PORTRAIT
        """
        self._rotate('PORTRAIT')

    def landscape(self):
        """
        Set the device orientation to LANDSCAPE
        """
        self._rotate('LANDSCAPE')

    def get_current_context(self):
        """Get current context."""
        return self._current_application().current_context

    def get_contexts(self):
        """Get available contexts."""
        print(self._current_application().contexts)
        return self._current_application().contexts

    def get_window_height(self):
        """Get current device height.

        Example:
        | ${width}       | Get Window Width |
        | ${height}      | Get Window Height |
        | Click A Point  | ${width}         | ${height} |

        New in AppiumLibrary 1.4.5
        """
        return self._current_application().get_window_size()['height']

    def get_window_width(self):
        """Get current device width.

        Example:
        | ${width}       | Get Window Width |
        | ${height}      | Get Window Height |
        | Click A Point  | ${width}          | ${height} |

        New in AppiumLibrary 1.4.5
        """
        return self._current_application().get_window_size()['width']

    def switch_to_context(self, context_name):
        """Switch to a new context"""
        self._current_application().switch_to.context(context_name)

    def switch_to_frame(self, frame):
        """
        Switches focus to the specified frame, by index, name, or webelement.

        Example:
        | Go To Url | http://www.xxx.com |
        | Switch To Frame  | iframe_name|
        | Click Element | xpath=//*[@id="online-btn"] |
        """
        self._current_application().switch_to.frame(frame)

    def switch_to_parent_frame(self):
        """
        Switches focus to the parent context. If the current context is the top
        level browsing context, the context remains unchanged.
        """
        self._current_application().switch_to.parent_frame()

    def switch_to_window(self, window_name):
        """
        Switch to a new webview window if the application contains multiple webviews
        """
        self._current_application().switch_to.window(window_name)

    def go_to_url(self, url):
        """
        Opens URL in default web browser.

        Example:
        | Open Application  | http://localhost:4755/wd/hub | platformName=iOS | platformVersion=7.0 | deviceName='iPhone Simulator' | browserName=Safari |
        | Go To URL         | http://m.webapp.com          |
        """
        self._current_application().get(url)

    def get_capability(self, capability_name):
        """
        Return the desired capability value by desired capability name
        """
        try:
            capability = self._current_application().capabilities[capability_name]
        except Exception as e:
            raise e
        return capability

    def get_window_title(self):
        """Get the current Webview window title."""
        return self._current_application().title

    def get_window_url(self):
        """Get the current Webview window URL."""
        return self._current_application().current_url

    def get_windows(self):
        """Get available Webview windows."""
        print(self._current_application().window_handles)
        return self._current_application().window_handles

    # Private

    def _current_application(self):
        if not self._cache.current:
            raise RuntimeError('No application is open')
        return self._cache.current

    def _get_platform(self):
        try:
            platform_name = self._current_application().capabilities['platformName']
        except Exception as e:
            raise e
        return platform_name.lower()

    def _is_platform(self, platform):
        platform_name = self._get_platform()
        return platform.lower() == platform_name

    def _is_ios(self):
        return self._is_platform('ios')

    def _is_android(self):
        return self._is_platform('android')

    def _is_window(self):
        return self._is_platform('windows')

    def _rotate(self, orientation):
        driver = self._current_application()
        driver.orientation = orientation

    def _absnorm(self, path):
        return abspath(self._normalize_path(path))

    def _normalize_path(self, path, case_normalize=False):
        """Normalizes the given path.

        - Collapses redundant separators and up-level references.
        - Converts ``/`` to ``\\`` on Windows.
        - Replaces initial ``~`` or ``~user`` by that user's home directory.
        - Converts ``pathlib.Path`` instances to ``str``.
        On Windows result would use ``\\`` instead of ``/`` and home directory
        would be different.
        """
        if isinstance(path, Path):
            path = str(path)
        else:
            path = path.replace("/", os.sep)
        path = os.path.normpath(os.path.expanduser(path))
        # os.path.normcase doesn't normalize on OSX which also, by default,
        # has case-insensitive file system. Our robot.utils.normpath would
        # do that, but it's not certain would that, or other things that the
        # utility do, desirable.
        if case_normalize:
            path = os.path.normcase(path)
        return path or "."
