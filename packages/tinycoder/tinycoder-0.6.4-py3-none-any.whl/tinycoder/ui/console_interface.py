import platform
import sys
import logging # For type hinting Logger
from typing import Callable, Optional, Dict

from tinycoder.ui.log_formatter import STYLES, COLORS as FmtColors, RESET # Assuming this path

def ring_bell():
    """Ring the terminal bell."""
    print("\a", end="", flush=True)  # Print bell character and flush output


def prompt_user_input(prompt: str) -> str:
    """Rings the terminal bell, displays a prompt, and returns user input."""
    ring_bell()
    try:
        # Prompt the user and wait for input
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        # Handle cases where the user cancels the input (e.g., Ctrl+C, Ctrl+D)
        print()  # Add a newline for clean output
        return ""  # Return an empty string to signify cancellation


class ConsoleInterface:
    """Handles console input operations for the application."""

    def __init__(self, logger: logging.Logger, get_app_mode_func: Callable[[], str], readline_available: bool, get_token_breakdown_func: Callable[[], Dict[str, int]]):
        """
        Initializes the ConsoleInterface.

        Args:
            logger: The application logger.
            get_app_mode_func: A callable that returns the current app mode (e.g., "code", "ask").
            readline_available: Boolean flag indicating if the readline module is available.
            get_token_breakdown_func: A callable that returns the context token breakdown.
        """
        self.logger = logger
        self.get_app_mode = get_app_mode_func
        self.readline_available = readline_available
        self.get_token_breakdown = get_token_breakdown_func

    def _format_token_breakdown(self, breakdown: Dict[str, int]) -> str:
        """Formats the token breakdown dictionary into a user-friendly string."""
        total = breakdown.get("total", 0)
        prompt_rules = breakdown.get("prompt_rules", 0)
        repo_map = breakdown.get("repo_map", 0)
        files = breakdown.get("files", 0)
        history = breakdown.get("history", 0)

        # Color for total token count
        total_color = FmtColors['GREEN']
        if total > 15000:
            total_color = FmtColors['YELLOW']
        if total > 25000:
            total_color = FmtColors['RED']
        
        total_str = f"Context: {total_color}{total:,}{RESET} tokens"

        # Breakdown string, using grey for less emphasis
        breakdown_parts = [
            f"Prompt/Rules: {prompt_rules:,}",
            f"Repo Map: {repo_map:,}",
            f"Files: {files:,}",
            f"History: {history:,}"
        ]
        breakdown_str = f"{FmtColors['GREY']}({', '.join(breakdown_parts)}){RESET}"

        # Combine with tabs for alignment
        return f"\t{total_str}\t{breakdown_str}"

    def _get_multiline_input_readline(self) -> Optional[str]:
        """
        Gets multi-line input using readline (if available), terminated by Ctrl+D.
        Handles prompts and Ctrl+C cancellation.
        """
        lines = []
        # Determine the correct instruction based on the OS
        if platform.system() == "Windows":
             # Readline might be available via pyreadline3, but Ctrl+Z is more standard there
            finish_instruction = "(Ctrl+Z then Enter to finish on Windows)"
        else:
            finish_instruction = "(Ctrl+D to finish)" # Standard Unix-like

        # Get and format token breakdown for the prompt
        token_breakdown = self.get_token_breakdown()
        token_info_line = self._format_token_breakdown(token_breakdown)

        # Construct the informational line
        print(f"Enter text {finish_instruction}{token_info_line}")

        # Mode prefix for the prompt
        current_mode = self.get_app_mode()
        mode_prefix = f"{STYLES['BOLD']}{FmtColors['GREEN']}({current_mode}){RESET} "
        
        # Initial prompt for the first line
        first_line_prompt = f"{mode_prefix}> "
        # Continuation prompt for subsequent lines
        continuation_prompt = f"{mode_prefix}. "
        
        prompt_to_use = first_line_prompt

        while True:
            try:
                # Use input() to leverage readline's line editing, history, and completion
                line = input(prompt_to_use)
                lines.append(line)
                # Change prompt for subsequent lines
                if prompt_to_use == first_line_prompt:
                    prompt_to_use = continuation_prompt
            except EOFError: # Handle Ctrl+D (or Ctrl+Z+Enter on Windows sometimes)
                print() # Print a newline for cleaner exit after EOF
                break
            except KeyboardInterrupt: # Handle Ctrl+C
                print("\nInput cancelled (Ctrl+C).")
                return None # Indicate cancellation

        return "\n".join(lines)

    def _get_multiline_input_stdin(self) -> Optional[str]:
         """Gets multi-line input by reading stdin until EOF (fallback)."""
         # Determine the correct instruction based on the OS
         if platform.system() == "Windows":
             finish_instruction = "Ctrl+Z then Enter to finish"
         else:
             finish_instruction = "Ctrl+D to finish"

         # Get and format token breakdown for the prompt
         token_breakdown = self.get_token_breakdown()
         token_info_line = self._format_token_breakdown(token_breakdown)

         print(f"Enter text ({finish_instruction}){token_info_line}")

         # Mode prefix for the prompt - print once before stdin.read()
         current_mode = self.get_app_mode()
         mode_prefix = f"{STYLES['BOLD']}{FmtColors['GREEN']}({current_mode}){RESET} "
         print(f"{mode_prefix}> ", end="", flush=True)
         try:
             user_input = sys.stdin.read()
             # .read() often includes the final newline if the user pressed Enter
             # before Ctrl+D/Ctrl+Z. You might want to strip trailing whitespace.
             return user_input.rstrip()
         except KeyboardInterrupt:
             print("\nInput cancelled (Ctrl+C).")
             return None  # Return None to signal cancellation
         except Exception as e: # Should ideally not happen with stdin.read()
             self.logger.error(f"An unexpected error occurred reading stdin: {e}", exc_info=True)
             print(f"\nAn unexpected error occurred reading stdin: {e}")
             return None  # Return None on error

    def _get_single_line_input_with_prompt(self) -> Optional[str]:
        """Gets single-line input using the built-in input(), with a formatted prompt."""
        current_mode = self.get_app_mode()
        token_breakdown = self.get_token_breakdown()
        token_count = token_breakdown.get('total', 0)

        token_color = FmtColors['GREEN']
        if token_count > 15000:
            token_color = FmtColors['YELLOW']
        if token_count > 25000:
            token_color = FmtColors['RED']

        # Simplified info for a more compact single-line prompt
        token_info = f"{token_color}[Context: {token_count:,} tokens]{RESET}"
        mode_prefix = f"{STYLES['BOLD']}{FmtColors['GREEN']}({current_mode}){RESET}"

        prompt_str = f"{mode_prefix} {token_info} > "
        try:
            line = input(prompt_str)
            return line
        except KeyboardInterrupt: # Handle Ctrl+C
            print("\nInput cancelled (Ctrl+C).")
            return None # Indicate cancellation
        except EOFError: # Handle Ctrl+D when input() is used directly
            # This might be treated as an exit signal higher up,
            # but returning None is consistent for input methods here.
            print() # Newline for cleaner exit after EOF
            return None


    def determine_input_function(self) -> Callable[[], Optional[str]]:
        """Returns the appropriate input function based on readline availability and OS."""
        if self.readline_available and platform.system() != "Windows":
            # Use readline-based input on non-Windows where it's generally more reliable
            self.logger.debug("Using readline-based multi-line input function.")
            return self._get_multiline_input_readline
        elif platform.system() == "Windows":
             if self.readline_available:
                 self.logger.debug("Readline detected on Windows, using readline-based multi-line input.")
                 # Try using the readline function on Windows too, relies on pyreadline3 behaving well
                 return self._get_multiline_input_readline
             else:
                  self.logger.debug("Readline not available on Windows, falling back to single-line input with prompt.")
                  return self._get_single_line_input_with_prompt
        else:
            # Fallback for non-Windows non-readline scenarios (unlikely)
            # For instance, if readline_available is somehow False on a non-Windows system
            self.logger.debug("Readline not available or OS is non-Windows non-readline, falling back to basic multi-line stdin read.")
            return self._get_multiline_input_stdin
