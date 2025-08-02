"""
Remote Process Plugin for yaapp

Clean interface for subprocess management:
1. start_process - Start a subprocess
2. inject_command - Inject command and tail output
3. tail_output - Just tail output streams
4. send_signal - Send signals to subprocess
5. stop_process - Stop the subprocess

All output includes timestamps for proper interleaving.
"""

import asyncio
import logging
import os
import pty
import select
import termios
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from yaapp import yaapp


@dataclass
class OutputLine:
    """Represents a line of output from the subprocess"""

    cmd: str
    timestamp: datetime
    text: str
    stream: str  # 'stdout' or 'stderr'


class PtyReader:
    """Reads from a PTY master fd and tracks output with command association"""

    def __init__(self):
        self.output_lines: List[OutputLine] = []
        self.current_command: str = "initial"
        self.reader_task: Optional[asyncio.Task] = None
        self.master_fd: Optional[int] = None
        self.command_start_index: int = 0  # Track where current command output starts

    def set_current_command(self, cmd: str):
        """Update the current command being executed and mark the start position"""
        self.current_command = cmd
        self.command_start_index = len(
            self.output_lines
        )  # Mark where new command output starts
        logger.info(
            f"PtyReader: Command set to '{cmd}', start index: {self.command_start_index}"
        )

    async def start(self, master_fd: int):
        """Start reading from the PTY master fd asynchronously"""
        self.master_fd = master_fd
        self.reader_task = asyncio.create_task(self._read_pty())
        logger.info(f"PtyReader: Started reading from master fd {master_fd}")

    async def _read_pty(self):
        """Internal method to read from PTY continuously"""
        try:
            try:
                loop = asyncio.get_running_loop()
                loop_running = True
            except RuntimeError:
                loop_running = False

            while True:
                # Use asyncio to read from fd in a non-blocking way
                data = await loop.run_in_executor(None, self._read_fd_chunk)
                if not data:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.01)
                    continue

                # Process text - preserve ANSI sequences for terminal display
                text = data.decode("utf-8", errors="replace")

                # Don't split into lines - preserve the raw text with newlines
                if text:
                    output_line = OutputLine(
                        cmd=self.current_command,
                        timestamp=datetime.now(),
                        text=text,
                        stream="pty",  # PTY merges stdout/stderr
                    )
                    self.output_lines.append(output_line)
                    logger.info(f"pty: {repr(text)}")

        except Exception as e:
            logger.error(f"Error reading from PTY: {e}")

    def _read_fd_chunk(self) -> bytes:
        """Read a chunk from the PTY fd (runs in executor)"""
        try:
            if self.master_fd is not None:
                # Use select to check if data is available
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                if ready:
                    return os.read(self.master_fd, 4096)
        except (OSError, select.error):
            pass
        return b""

    def get_recent_lines(self, count: int = 10) -> List[OutputLine]:
        """Get recent output lines"""
        return self.output_lines[-count:] if count > 0 else self.output_lines

    def get_current_command_output(self) -> List[OutputLine]:
        """Get output lines from the current command only"""
        if self.command_start_index >= len(self.output_lines):
            return []
        return self.output_lines[self.command_start_index :]

    async def stop(self):
        """Stop the PTY reader"""
        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        logger.info("PtyReader: Stopped")


@yaapp.expose("remote")
class RemoteProcess:
    """Manages a subprocess with PTY for proper interactive behavior"""

    def __init__(self, config=None):
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        self.process: Optional[asyncio.subprocess.Process] = None
        self.pty_reader = PtyReader()
        self.master_fd: Optional[int] = None
        self._command_counter = 0

    def start_process(self, command: str, tail: bool = True) -> str:
        """Start the subprocess with PTY for proper interactive behavior"""
        try:
            try:
                loop = asyncio.get_running_loop()
                loop_running = True
            except RuntimeError:
                loop_running = False
            
            if loop_running:
                # If we're already in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._start_process_async(command, tail))
                    return future.result(timeout=30)
            else:
                return asyncio.run(self._start_process_async(command, tail))
        except Exception as e:
            return f"Error starting process: {str(e)}"
    
    async def _start_process_async(self, command: str, tail: bool = True) -> str:
        """Start the subprocess with PTY for proper interactive behavior"""
        if self.is_running():
            return "ERROR: A subprocess is already running. Stop it first."

        cmd_parts = command.split()
        master_fd = None
        slave_fd = None

        try:
            # Create pseudo-terminal
            master_fd, slave_fd = pty.openpty()

            # Configure slave terminal for interactive use
            slave_attr = termios.tcgetattr(slave_fd)
            # Disable echo to prevent double echoing
            slave_attr[3] = slave_attr[3] & ~termios.ECHO
            termios.tcsetattr(slave_fd, termios.TCSADRAIN, slave_attr)

            # Set terminal size for proper ANSI rendering
            try:
                import fcntl
                import struct

                # Get current terminal size
                terminal_size = os.get_terminal_size()
                winsize = struct.pack(
                    "HHHH", terminal_size.lines, terminal_size.columns, 0, 0
                )
                fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
            except (OSError, AttributeError):
                # Fallback to common size if can't detect
                winsize = struct.pack("HHHH", 24, 80, 0, 0)
                try:
                    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
                except OSError:
                    pass

            # Start process with PTY - run EXACTLY what user specified
            self.process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,  # Enable job control
                env=None,  # Inherit environment without modification
            )

            # Close slave fd in parent process (we only need master_fd)
            os.close(slave_fd)
            slave_fd = None  # Mark as closed

            # Store master_fd and start PTY reader
            self.master_fd = master_fd
            await self.pty_reader.start(self.master_fd)

            logger.info(
                f"Started subprocess with PTY: {' '.join(cmd_parts)} (PID: {self.process.pid})"
            )

            # Wait for subprocess to initialize and show natural prompt
            await asyncio.sleep(
                1.0
            )  # Give subprocess time to show its prompt naturally

            # Check if process is still running
            if self.process.returncode is not None:
                logger.error(
                    f"Process exited immediately with code {self.process.returncode}"
                )
                return f"Failed to start subprocess: process exited with code {self.process.returncode}"

            result = f"Successfully started subprocess: {command}"
            
            # If tail is requested, include initial output
            if tail:
                # Wait a bit more for initial output
                await asyncio.sleep(0.5)
                initial_output = self.pty_reader.get_recent_lines(count=5)
                if initial_output:
                    result += "\n\nInitial output:\n"
                    for line in initial_output:
                        result += line.text
            
            return result

        except Exception as e:
            logger.error(f"Failed to start subprocess: {e}")
            return f"Failed to start subprocess: {str(e)}"

        finally:
            # Cleanup FDs on error
            if slave_fd is not None:
                try:
                    os.close(slave_fd)
                except OSError:
                    pass

            # If we failed and have master_fd, clean it up
            if not hasattr(self, "master_fd") or self.master_fd != master_fd:
                if master_fd is not None:
                    try:
                        os.close(master_fd)
                    except OSError:
                        pass

    def inject_command(self, command: str, tail_count: int = 10) -> str:
        """Inject a command into the subprocess and tail the output from that command"""
        try:
            try:
                loop = asyncio.get_running_loop()
                loop_running = True
            except RuntimeError:
                loop_running = False
            
            if loop_running:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._inject_command_async(command, tail_count))
                    return future.result(timeout=30)
            else:
                return asyncio.run(self._inject_command_async(command, tail_count))
        except Exception as e:
            return f"Error injecting command: {str(e)}"
    
    async def _inject_command_async(self, command: str, tail_count: int = 10) -> str:
        """Inject a command into the subprocess and tail the output from that command"""
        if not self.is_running():
            return "ERROR: No subprocess is currently running. Start one first."

        try:
            # Update command tracking - set checkpoint BEFORE sending command
            self._command_counter += 1
            command_id = f"cmd_{self._command_counter}"

            self.pty_reader.set_current_command(command_id)

            # Send command to subprocess via PTY
            command_bytes = f"{command}\n".encode("utf-8")
            os.write(self.master_fd, command_bytes)

            logger.info(f"Injected command via PTY: {command}")

            # Wait for command output to appear
            await asyncio.sleep(0.5)

            # Get output from current command only
            all_lines = self.pty_reader.get_current_command_output()

            if not all_lines:
                return f"Command injected successfully. No output from this command yet."

            # Format output - show only output from this command execution
            result = f"Command injected successfully. Current command output:\n"
            for line in all_lines:
                result += line.text

            return result

        except Exception as e:
            logger.error(f"Failed to inject command '{command}': {e}")
            return f"ERROR: Failed to inject command: {str(e)}"

    def tail_output(self, count: int = 10, stream: str = "both") -> str:
        """Tail the output from the subprocess"""
        if not self.is_running():
            return "ERROR: No subprocess is currently running."

        # Get interleaved output
        all_lines = self.pty_reader.get_recent_lines(count)

        if not all_lines:
            return f"No {stream} output available yet."

        # Format output
        result = f"Recent {stream} output ({len(all_lines)} lines):\n\n"
        for line in all_lines:
            result += line.text

        return result

    def send_signal(self, signal_name: str) -> str:
        """Send a signal to the subprocess (SIGINT, SIGTERM)"""
        # Quick check before trying async operations
        if not self.is_running():
            return "No subprocess is currently running."
            
        try:
            try:
                loop = asyncio.get_running_loop()
                loop_running = True
            except RuntimeError:
                loop_running = False
            
            if loop_running:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._send_signal_async(signal_name))
                    return future.result(timeout=30)
            else:
                return asyncio.run(self._send_signal_async(signal_name))
        except Exception as e:
            return f"Error sending signal: {str(e)}"
    
    async def _send_signal_async(self, signal_name: str) -> str:
        """Send a signal to the subprocess (SIGINT, SIGTERM)"""
        if not self.is_running():
            return "No subprocess is currently running."

        try:
            if signal_name == "SIGINT":  # Ctrl+C
                os.write(self.master_fd, b"\x03")  # ASCII 3 = Ctrl+C
                logger.info("Sent SIGINT (Ctrl+C) to subprocess")
                return f"Signal {signal_name} sent successfully."
            elif signal_name == "SIGTERM":  # Ctrl+\
                os.write(self.master_fd, b"\x1c")  # ASCII 28 = Ctrl+\
                logger.info("Sent SIGTERM (Ctrl+\\) to subprocess")
                return f"Signal {signal_name} sent successfully."
            else:
                logger.error(f"Unknown signal: {signal_name}")
                return f"Unknown signal: {signal_name}. Supported: SIGINT, SIGTERM"

        except Exception as e:
            logger.error(f"Failed to send signal '{signal_name}': {e}")
            return f"Failed to send signal {signal_name}: {str(e)}"

    def stop_process(self) -> str:
        """Stop the subprocess and PTY reader with proper SIGTERM -> SIGKILL sequence"""
        try:
            try:
                loop = asyncio.get_running_loop()
                loop_running = True
            except RuntimeError:
                loop_running = False
            
            if loop_running:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._stop_process_async())
                    return future.result(timeout=30)
            else:
                return asyncio.run(self._stop_process_async())
        except Exception as e:
            return f"Error stopping process: {str(e)}"
    
    async def _stop_process_async(self) -> str:
        """Stop the subprocess and PTY reader with proper SIGTERM -> SIGKILL sequence"""
        if not self.is_running():
            return "No subprocess is currently running."

        try:
            if self.process:
                # First try SIGTERM (graceful)
                self.process.terminate()
                logger.info("Sent SIGTERM to subprocess")

                # Wait up to 5 seconds for graceful shutdown
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                    logger.info("Subprocess terminated gracefully")
                except asyncio.TimeoutError:
                    # Force kill with SIGKILL
                    logger.info(
                        "Subprocess didn't terminate gracefully, sending SIGKILL"
                    )
                    self.process.kill()
                    await self.process.wait()
                    logger.info("Subprocess killed forcefully")

            await self.pty_reader.stop()
            logger.info("Subprocess and PTY reader stopped")
            return "Subprocess stopped successfully."

        except Exception as e:
            logger.error(f"Error stopping subprocess: {e}")
            return f"Error stopping subprocess: {str(e)}"

    def is_running(self) -> bool:
        """Check if subprocess is running"""
        return self.process is not None and self.process.returncode is None

    def get_status(self) -> Dict[str, Any]:
        """Get subprocess status information"""
        if not self.process:
            return {
                "running": False,
                "pid": None,
                "returncode": None,
                "output_lines": 0
            }

        return {
            "running": self.is_running(),
            "pid": self.process.pid,
            "returncode": self.process.returncode,
            "output_lines": len(self.pty_reader.output_lines)
        }
    
    def send_input(self, input_text: str) -> str:
        """Send input to the running process (for keyboard input)"""
        if not self.is_running():
            return "ERROR: No subprocess is currently running."
        
        try:
            # Send input directly to PTY (like keyboard input)
            input_bytes = f"{input_text}\n".encode("utf-8")
            os.write(self.master_fd, input_bytes)
            logger.info(f"Sent input to process: {repr(input_text)}")
            return f"Input sent: {input_text}"
        except Exception as e:
            logger.error(f"Failed to send input '{input_text}': {e}")
            return f"ERROR: Failed to send input: {str(e)}"
    
    async def start_process_stream(self, command: str):
        """Start process and yield output as SSE stream"""
        # Start the process first
        start_result = await self._start_process_async(command, tail=False)
        if "ERROR" in start_result:
            yield f"data: {start_result}\n\n"
            return
        
        # Send initial success message
        yield f"data: {start_result}\n\n"
        
        # Track last seen output index to only yield new output
        last_output_index = 0
        
        # Stream output as it comes
        while self.is_running():
            current_lines = self.pty_reader.output_lines
            
            # Yield any new output since last check
            if len(current_lines) > last_output_index:
                new_lines = current_lines[last_output_index:]
                for line in new_lines:
                    # SSE format: data: <content>\n\n
                    escaped_text = line.text.replace('\n', '\\n').replace('\r', '\\r')
                    yield f"data: {escaped_text}\n\n"
                last_output_index = len(current_lines)
            
            # Small delay to prevent busy waiting
            await asyncio.sleep(0.1)
        
        # Send final message when process ends
        yield f"data: Process ended\n\n"


