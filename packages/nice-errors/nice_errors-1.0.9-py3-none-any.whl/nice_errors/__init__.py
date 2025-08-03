# friendly_errors.py

import sys
import traceback
from colorama import Fore, Style, init
# Initialize colorama
init(autoreset=True)

# === Configuration ===
CONFIG = {
    "SHOW_TRACEBACK": True  # Toggle technical tracebacks
}

class ErrorMessage:
    def __init__(self, title, explanation, fix, emoji):
        self.title = title
        self.explanation = explanation
        self.fix = fix
        self.emoji = emoji
# Friendly error explanations
ERROR_MESSAGES = {
    "ArithmeticError": ErrorMessage(
        title="➕ Arithmetic Error",
        explanation="A general arithmetic error occurred.",
        fix="Check your calculations and operands.",
        emoji="➗"
    ),
    "AssertionError": ErrorMessage(
        title="⚠️ Assertion Failed",
        explanation="An assert statement expected something to be true — but it wasn’t.",
        fix="Check what you're testing. Maybe it’s not quite what you think.",
        emoji="🔍"
    ),
    "AttributeError": ErrorMessage(
        title="🔍 Missing Something!",
        explanation="Python expected your object to have a function or property — but it doesn’t.",
        fix="Use 'dir()' to see what your object can actually do.",
        emoji="🧱"
    ),
    "BaseException": ErrorMessage(
        title="🧱 Base Exception",
        explanation="The base class for all exceptions.",
        fix="This should not be raised directly.",
        emoji="📦"
    ),
    "BlockingIOError": ErrorMessage(
        title="🛑 Blocking I/O Error",
        explanation="An operation would block on a non-blocking I/O object.",
        fix="Ensure the file/socket is ready or use non-blocking I/O properly.",
        emoji="🔌"
    ),
    "BrokenPipeError": ErrorMessage(
        title="🚰 Broken Pipe",
        explanation="You tried writing to a pipe that’s been closed on the other end.",
        fix="Ensure the pipe is open and the reader is available.",
        emoji="🧵"
    ),
    "BufferError": ErrorMessage(
        title="🧠 Buffer Error",
        explanation="A problem occurred with a buffer-related operation.",
        fix="Avoid modifying buffers in unsupported ways.",
        emoji="📉"
    ),
    "ChildProcessError": ErrorMessage(
        title="👶 Child Process Error",
        explanation="An operation related to a child process failed.",
        fix="Check the child process logic and its state.",
        emoji="👶"
    ),
    "ConnectionAbortedError": ErrorMessage(
        title="❌ Connection Aborted",
        explanation="The connection was closed unexpectedly.",
        fix="Check server/client connection stability.",
        emoji="📡"
    ),
    "ConnectionError": ErrorMessage(
        title="🔌 Connection Error",
        explanation="There was a connection-related error.",
        fix="Check your network or socket configuration.",
        emoji="🌐"
    ),
    "ConnectionRefusedError": ErrorMessage(
        title="🚫 Connection Refused",
        explanation="The target machine refused to connect.",
        fix="Ensure the server is running and reachable.",
        emoji="🖥️"
    ),
    "ConnectionResetError": ErrorMessage(
        title="🔁 Connection Reset",
        explanation="The connection was reset by the peer.",
        fix="Check for network or peer issues.",
        emoji="🔄"
    ),
    "EOFError": ErrorMessage(
        title="📭 End of File Reached",
        explanation="Tried to read beyond the end of a file.",
        fix="Ensure you’re not reading past available input.",
        emoji="📪"
    ),
    "EnvironmentError": ErrorMessage(
        title="🌎 Environment Error",
        explanation="An error occurred in the environment.",
        fix="Check file paths, permissions, and system resources.",
        emoji="🛠️"
    ),
    "Exception": ErrorMessage(
        title="❗ Generic Exception",
        explanation="A general exception occurred.",
        fix="Review the traceback for specifics.",
        emoji="⚙️"
    ),
    "FileExistsError": ErrorMessage(
        title="📁 File Already Exists",
        explanation="Tried to create a file that already exists.",
        fix="Use a different name or remove the old file first.",
        emoji="📂"
    ),
    "FileNotFoundError": ErrorMessage(
        title="📄 File Not Found",
        explanation="The file you tried to open doesn't exist — or the path is wrong.",
        fix="Double-check the file name and location.",
        emoji="🗂️"
    ),
    "FloatingPointError": ErrorMessage(
        title="💫 Floating Point Error",
        explanation="A floating-point calculation failed.",
        fix="Ensure valid numbers and avoid undefined operations.",
        emoji="🔬"
    ),
    "GeneratorExit": ErrorMessage(
        title="🔚 Generator Exit",
        explanation="A generator is being closed.",
        fix="This usually doesn’t indicate a bug.",
        emoji="🚪"
    ),
    "ImportError": ErrorMessage(
        title="📦 Couldn’t Import Something",
        explanation="Python had trouble importing a piece of code or library.",
        fix="Make sure the name is correct and it’s installed properly.",
        emoji="📚"
    ),
    "IndentationError": ErrorMessage(
        title="📐 Indentation Mix-Up",
        explanation="Python is picky about spaces and tabs. Something’s not lined up right.",
        fix="Stick with either spaces or tabs — don’t mix them!",
        emoji="📏"
    ),
    "IndexError": ErrorMessage(
        title="📦 List Index Out of Bounds",
        explanation="You asked for a list item that’s too far — it doesn’t exist!",
        fix="Try using 'len()' to check the size before accessing by index.",
        emoji="📏"
    ),
    "InterruptedError": ErrorMessage(
        title="⛔ Interrupted",
        explanation="A system call was interrupted.",
        fix="Retry the operation or handle the interruption.",
        emoji="🔔"
    ),
    "IsADirectoryError": ErrorMessage(
        title="📁 Expected File, Got Directory",
        explanation="You tried to treat a directory like a file.",
        fix="Check the path and use the correct file type.",
        emoji="📂"
    ),
    "KeyError": ErrorMessage(
        title="🔑 Key Not Found!",
        explanation="That key you tried to use in a dictionary isn’t there.",
        fix="Use '.get()' or check with 'in' before accessing the key.",
        emoji="🗝️"
    ),
    "KeyboardInterrupt": ErrorMessage(
        title="🛑 Keyboard Interrupt",
        explanation="You manually stopped the program (usually with Ctrl+C).",
        fix="This was intentional — no fix needed.",
        emoji="⌨️"
    ),
    "LookupError": ErrorMessage(
        title="🔍 Lookup Failed",
        explanation="A lookup operation (e.g., indexing) failed.",
        fix="Ensure the index/key exists in the data structure.",
        emoji="🔎"
    ),
    "MemoryError": ErrorMessage(
        title="💥 Out of Memory",
        explanation="Python ran out of memory to keep going.",
        fix="Try using smaller data chunks or loops instead of big lists.",
        emoji="💾"
    ),
    "ModuleNotFoundError": ErrorMessage(
        title="🔍 Module Not Found",
        explanation="Python couldn’t find that library or module.",
        fix="Try running 'pip install' to add it, or check the spelling.",
        emoji="📦"
    ),
    "NameError": ErrorMessage(
        title="❌ Oops! That Name Doesn’t Exist",
        explanation="Python saw a name it didn’t recognize. Maybe a typo or you forgot to define it?",
        fix="Make sure you spelled it right and created it before using it.",
        emoji="🔍"
    ),
    "NotADirectoryError": ErrorMessage(
        title="🚫 Not a Directory",
        explanation="Expected a directory but found something else.",
        fix="Check the path and whether it’s a file or directory.",
        emoji="📁"
    ),
    "NotImplementedError": ErrorMessage(
        title="🚧 Not Implemented",
        explanation="This part of the code isn’t implemented yet.",
        fix="Fill in the implementation where needed.",
        emoji="🛠️"
    ),
    "OSError": ErrorMessage(
        title="🧱 OS Error",
        explanation="An error occurred interacting with the OS.",
        fix="Check the path, permissions, and system environment.",
        emoji="🧰"
    ),
    "OverflowError": ErrorMessage(
        title="📈 Number Got Too Big",
        explanation="A number went beyond what Python can handle!",
        fix="Use smaller numbers, or use special number types like 'decimal' if needed.",
        emoji="🔺"
    ),
    "PermissionError": ErrorMessage(
        title="🔒 No Permission!",
        explanation="Python tried to open something, but it doesn’t have permission.",
        fix="Try running with more access or changing file permissions.",
        emoji="🚷"
    ),
    "ProcessLookupError": ErrorMessage(
        title="🔍 Process Not Found",
        explanation="You tried to interact with a process that doesn't exist.",
        fix="Make sure the process ID is valid.",
        emoji="🔍"
    ),
    "RecursionError": ErrorMessage(
        title="🔁 Too Much Recursion!",
        explanation="Your function is calling itself too many times and didn’t stop.",
        fix="Make sure you have a base case that ends the loop.",
        emoji="🌀"
    ),
    "ReferenceError": ErrorMessage(
        title="🔗 Reference Lost",
        explanation="You tried to use a weak reference that no longer exists.",
        fix="Avoid using deleted objects.",
        emoji="🪢"
    ),
    "RuntimeError": ErrorMessage(
        title="🏃 Runtime Error",
        explanation="Something went wrong while the program was running.",
        fix="Check the context of the error and trace it back.",
        emoji="📉"
    ),
    "StopAsyncIteration": ErrorMessage(
        title="🛑 Async Done",
        explanation="An async iterator has no more items.",
        fix="This usually means the loop is complete — nothing to fix.",
        emoji="⏹️"
    ),
    "StopIteration": ErrorMessage(
        title="🛑 Nothing Left to Loop",
        explanation="You're trying to loop through something that’s finished.",
        fix="Make sure you're not using 'next()' too many times.",
        emoji="⏹️"
    ),
    "SyntaxError": ErrorMessage(
        title="📜 Syntax Error",
        explanation="Python couldn’t understand your code — something’s not right.",
        fix="Double-check punctuation, keywords, and structure.",
        emoji="✏️"
    ),
    "IndentationError": ErrorMessage(
        title="📐 Indentation Mix-Up",
        explanation="Python is picky about spaces and tabs. Something’s not lined up right.",
        fix="Stick with either spaces or tabs — don’t mix them!",
        emoji="📏"
    ),
    "TabError": ErrorMessage(
        title="🔄 Mixed Tabs and Spaces",
        explanation="You mixed tabs and spaces in your code's indentation.",
        fix="Use only tabs or only spaces — not both.",
        emoji="🔠"
    ),
    "SystemError": ErrorMessage(
        title="🖥️ System Error",
        explanation="A serious error occurred in the interpreter.",
        fix="Try to isolate and reproduce the error. Might be a bug in Python itself.",
        emoji="🧯"
    ),
    "SystemExit": ErrorMessage(
        title="👋 Exiting Program",
        explanation="The program is trying to exit using 'sys.exit()'.",
        fix="This is normal if done intentionally.",
        emoji="🚪"
    ),
    "TimeoutError": ErrorMessage(
        title="⏰ Operation Timed Out",
        explanation="A timeout occurred while waiting for a process or connection.",
        fix="Check your timeout settings or increase the limit.",
        emoji="⌛"
    ),
    "TypeError": ErrorMessage(
        title="🔢 Uh-oh, Types Don't Match",
        explanation="You tried to do something like add a number to a word — and Python got confused.",
        fix="Make sure you're working with the right types. You can convert them if needed!",
        emoji="🔁"
    ),
    "UnboundLocalError": ErrorMessage(
        title="📍 Unbound Local Variable",
        explanation="You used a local variable before assigning a value to it.",
        fix="Make sure the variable is defined before use.",
        emoji="📌"
    ),
    "UnicodeDecodeError": ErrorMessage(
        title="🈳 Unicode Decode Error",
        explanation="Python couldn’t decode a byte string.",
        fix="Check the encoding and ensure it matches the input.",
        emoji="📜"
    ),
    "UnicodeEncodeError": ErrorMessage(
        title="🔤 Unicode Encode Error",
        explanation="Python couldn’t encode a string into bytes.",
        fix="Check the output encoding and your string contents.",
        emoji="🆎"
    ),
    "UnicodeError": ErrorMessage(
        title="🔣 Unicode Error",
        explanation="A problem occurred with encoding or decoding Unicode.",
        fix="Ensure valid encodings and correct byte sequences.",
        emoji="🎴"
    ),
    "UnicodeTranslateError": ErrorMessage(
        title="🔄 Unicode Translate Error",
        explanation="An error occurred during Unicode translation.",
        fix="Validate characters and encodings.",
        emoji="🌐"
    ),
    "ValueError": ErrorMessage(
        title="❗ Weird Value Detected",
        explanation="Python got a value that looked okay... but wasn’t quite right.",
        fix="Double-check the input values — they may need tweaking!",
        emoji="📉"
    ),
    "ZeroDivisionError": ErrorMessage(
        title="🚫 Can’t Divide by Zero",
        explanation="Nice try, but dividing by 0 isn’t allowed in math or Python!",
        fix="Before dividing, check that the bottom number isn’t zero.",
        emoji="➗"
    ),
    "Generic": ErrorMessage(
        title="❓ Something Went Wrong",
        explanation="An error happened, but I’m not sure which one!",
        fix="Check the code and traceback to learn more.",
        emoji="🤷"
    )
}

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_type = exc_type.__name__
    msg = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["Generic"])

    tb = traceback.extract_tb(exc_traceback)
    if tb:
        tb_last = tb[-1]
        filename = tb_last.filename
        lineno = tb_last.lineno
        code_line = tb_last.line.strip() if tb_last.line else "N/A"
    else:
        filename = "<unknown>"
        lineno = "?"
        code_line = "?"

    sys.stderr.write(Fore.RED + Style.BRIGHT + "\n🚨 Uh-oh! A Python Error Happened!\n\n")
    sys.stderr.write(f"{Fore.YELLOW}{Style.BRIGHT}{msg.emoji} {msg.title}\n")
    sys.stderr.write(Fore.WHITE + f"\n{msg.explanation}\n")
    sys.stderr.write(Fore.GREEN + f"💡 Tip: {msg.fix}\n")
    sys.stderr.write(Fore.CYAN + "\n📍 Where it happened:\n")
    sys.stderr.write(f"{Fore.WHITE}  File: {Fore.MAGENTA}{filename}\n")
    sys.stderr.write(f"{Fore.WHITE}  Line: {Fore.MAGENTA}{lineno}\n")
    sys.stderr.write(f"{Fore.WHITE}  Code: {Fore.MAGENTA}{code_line}\n")

    if CONFIG["SHOW_TRACEBACK"]:
        sys.stderr.write(Fore.LIGHTBLACK_EX + "\n🛠️ Technical Details:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

# Automatically install the handler
sys.excepthook = handle_exception
