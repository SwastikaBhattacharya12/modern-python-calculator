"""
Modern Calculator Application

Run the graphical calculator:
    python calculator.py

Run the optional command-line calculator:
    python calculator.py --cli

Dependencies:
    This script only uses Python's standard library. Tkinter is included with
    most Python installations. If Tkinter is missing, install a Python build
    that includes Tcl/Tk support.
"""

from __future__ import annotations

import ast
import math
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


# ---------------------------------------------------------------------------
# Basic arithmetic functions used by both the CLI and GUI calculators.
# ---------------------------------------------------------------------------


def add(first_number: float, second_number: float) -> float:
    """Return the sum of two numbers."""
    return first_number + second_number


def subtract(first_number: float, second_number: float) -> float:
    """Return the difference between two numbers."""
    return first_number - second_number


def multiply(first_number: float, second_number: float) -> float:
    """Return the product of two numbers."""
    return first_number * second_number


def divide(first_number: float, second_number: float) -> float:
    """Return the quotient of two numbers, guarding against division by zero."""
    if second_number == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return first_number / second_number


def modulus(first_number: float, second_number: float) -> float:
    """Return the remainder from dividing two numbers."""
    if second_number == 0:
        raise ZeroDivisionError("Cannot use modulus with zero.")
    return first_number % second_number


def exponentiate(first_number: float, second_number: float) -> float:
    """Return the first number raised to the power of the second number."""
    return first_number**second_number


# ---------------------------------------------------------------------------
# Safe expression evaluator for the GUI calculator.
# It supports numbers, scientific notation, and calculator operators without
# exposing Python's general-purpose eval function.
# ---------------------------------------------------------------------------


class SafeCalculatorEvaluator:
    """Evaluate calculator expressions using Python's AST in a restricted way."""

    _binary_operators = {
        ast.Add: add,
        ast.Sub: subtract,
        ast.Mult: multiply,
        ast.Div: divide,
        ast.Mod: modulus,
        ast.Pow: exponentiate,
    }

    _unary_operators = {
        ast.UAdd: lambda number: number,
        ast.USub: lambda number: -number,
    }

    def evaluate(self, expression: str) -> float:
        """Evaluate a user expression and return its numeric result."""
        normalized_expression = expression.replace("^", "**").replace("x", "*").replace("÷", "/")
        if not normalized_expression.strip():
            raise ValueError("Enter a calculation first.")

        try:
            syntax_tree = ast.parse(normalized_expression, mode="eval")
        except SyntaxError as error:
            raise ValueError("Invalid calculation.") from error

        return float(self._evaluate_node(syntax_tree.body))

    def _evaluate_node(self, node: ast.AST) -> float:
        """Recursively evaluate only the AST nodes a calculator needs."""
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)
            operation = self._binary_operators.get(operator_type)
            if operation is None:
                raise ValueError("Unsupported operator.")
            return operation(self._evaluate_node(node.left), self._evaluate_node(node.right))

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)
            operation = self._unary_operators.get(operator_type)
            if operation is None:
                raise ValueError("Unsupported sign.")
            return operation(self._evaluate_node(node.operand))

        raise ValueError("Unsupported expression.")


class ModernCalculatorApp:
    """A dark themed, smartphone-style calculator built with Tkinter."""

    HISTORY_FILE = Path(__file__).with_name("calculator_history.txt")

    DARK_THEME = {
        "window": "#111318",
        "panel": "#1b1f27",
        "display": "#171a21",
        "text": "#f4f7fb",
        "muted": "#9aa4b2",
        "number": "#272d38",
        "number_hover": "#323a47",
        "operator": "#2f5d7c",
        "operator_hover": "#3b7298",
        "special": "#4b5361",
        "special_hover": "#606979",
        "equals": "#22a06b",
        "equals_hover": "#2ec27e",
        "danger": "#9d3b46",
        "danger_hover": "#b74a57",
    }

    LIGHT_THEME = {
        "window": "#eef2f7",
        "panel": "#ffffff",
        "display": "#f8fafc",
        "text": "#172033",
        "muted": "#64748b",
        "number": "#e2e8f0",
        "number_hover": "#cbd5e1",
        "operator": "#bfdbfe",
        "operator_hover": "#93c5fd",
        "special": "#d8dee9",
        "special_hover": "#c2cad7",
        "equals": "#16a34a",
        "equals_hover": "#15803d",
        "danger": "#fecaca",
        "danger_hover": "#fca5a5",
    }

    BUTTONS = [
        ("MC", "special"), ("MR", "special"), ("M+", "special"), ("M-", "special"), ("C", "danger"),
        ("√", "operator"), ("%", "operator"), ("^", "operator"), ("÷", "operator"), ("Exit", "danger"),
        ("7", "number"), ("8", "number"), ("9", "number"), ("x", "operator"), ("Copy", "special"),
        ("4", "number"), ("5", "number"), ("6", "number"), ("-", "operator"), ("Save", "special"),
        ("1", "number"), ("2", "number"), ("3", "number"), ("+", "operator"), ("History C", "special"),
        ("±", "special"), ("0", "number"), (".", "number"), ("mod", "operator"), ("=", "equals"),
        ("Mode", "special"),
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Modern Calculator")
        self.root.geometry("900x620")
        self.root.minsize(720, 520)

        self.evaluator = SafeCalculatorEvaluator()
        self.expression = tk.StringVar(value="")
        self.result = tk.StringVar(value="0")
        self.memory_value = 0.0
        self.is_dark_mode = True
        self.history: list[str] = []
        self.buttons: list[tuple[tk.Button, str]] = []

        self.date_time = tk.StringVar()
        self.memory_label = tk.StringVar(value="Memory: 0")

        self._create_icon()
        self._build_interface()
        self._bind_keyboard_shortcuts()
        self._apply_theme()
        self._tick_clock()

    def _create_icon(self) -> None:
        """Create a small calculator-style app icon without external files."""
        icon = tk.PhotoImage(width=32, height=32)
        icon.put("#1f2937", to=(0, 0, 32, 32))
        icon.put("#22a06b", to=(5, 5, 27, 12))
        for row in range(3):
            for column in range(3):
                x = 6 + column * 8
                y = 16 + row * 5
                icon.put("#f8fafc", to=(x, y, x + 4, y + 3))
        self.root.iconphoto(True, icon)
        self.icon = icon

    def _build_interface(self) -> None:
        """Create the calculator layout."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.rowconfigure(1, weight=1)

        self.display_frame = tk.Frame(self.main_frame, padx=16, pady=12)
        self.display_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        self.display_frame.columnconfigure(0, weight=1)

        self.expression_label = tk.Label(
            self.display_frame,
            textvariable=self.expression,
            anchor="e",
            font=("Segoe UI", 16),
        )
        self.expression_label.grid(row=0, column=0, sticky="ew")

        self.result_label = tk.Label(
            self.display_frame,
            textvariable=self.result,
            anchor="e",
            font=("Segoe UI", 34, "bold"),
        )
        self.result_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self.status_frame = tk.Frame(self.display_frame)
        self.status_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.status_frame.columnconfigure(0, weight=1)
        self.status_frame.columnconfigure(1, weight=1)

        self.memory_status_label = tk.Label(
            self.status_frame,
            textvariable=self.memory_label,
            anchor="w",
            font=("Segoe UI", 10),
        )
        self.memory_status_label.grid(row=0, column=0, sticky="ew")

        self.clock_label = tk.Label(
            self.status_frame,
            textvariable=self.date_time,
            anchor="e",
            font=("Segoe UI", 10),
        )
        self.clock_label.grid(row=0, column=1, sticky="ew")

        self.keypad_frame = tk.Frame(self.main_frame)
        self.keypad_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        for column in range(5):
            self.keypad_frame.columnconfigure(column, weight=1, uniform="buttons")
        row_count = (len(self.BUTTONS) + 4) // 5
        for row in range(row_count):
            self.keypad_frame.rowconfigure(row, weight=1, uniform="buttons")

        for index, (button_text, button_kind) in enumerate(self.BUTTONS):
            row, column = divmod(index, 5)
            button = tk.Button(
                self.keypad_frame,
                text=button_text,
                command=lambda value=button_text: self._handle_button(value),
                font=("Segoe UI", 13, "bold"),
                relief=tk.FLAT,
                borderwidth=0,
                cursor="hand2",
            )
            button.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
            self._add_button_animation(button, button_kind)
            self.buttons.append((button, button_kind))

        self.history_frame = tk.Frame(self.main_frame, padx=12, pady=12)
        self.history_frame.grid(row=1, column=1, sticky="nsew")
        self.history_frame.rowconfigure(1, weight=1)
        self.history_frame.columnconfigure(0, weight=1)

        self.history_title = tk.Label(
            self.history_frame,
            text="History",
            anchor="w",
            font=("Segoe UI", 15, "bold"),
        )
        self.history_title.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.history_listbox = tk.Listbox(
            self.history_frame,
            font=("Consolas", 11),
            borderwidth=0,
            activestyle="none",
            highlightthickness=0,
        )
        self.history_listbox.grid(row=1, column=0, sticky="nsew")
        self.history_listbox.bind("<Double-Button-1>", self._recall_history_item)

    def _add_button_animation(self, button: tk.Button, button_kind: str) -> None:
        """Add hover and press feedback to a button."""

        def on_enter(_: tk.Event) -> None:
            theme = self._theme
            button.configure(background=theme[f"{button_kind}_hover"])

        def on_leave(_: tk.Event) -> None:
            theme = self._theme
            button.configure(background=theme[button_kind])

        def on_press(_: tk.Event) -> None:
            button.configure(relief=tk.SUNKEN)

        def on_release(_: tk.Event) -> None:
            button.configure(relief=tk.FLAT)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

    @property
    def _theme(self) -> dict[str, str]:
        """Return the currently selected color palette."""
        return self.DARK_THEME if self.is_dark_mode else self.LIGHT_THEME

    def _apply_theme(self) -> None:
        """Apply the active light or dark theme to every widget."""
        theme = self._theme
        self.root.configure(background=theme["window"])
        self.main_frame.configure(background=theme["window"])
        self.keypad_frame.configure(background=theme["window"])
        self.display_frame.configure(background=theme["display"])
        self.status_frame.configure(background=theme["display"])
        self.history_frame.configure(background=theme["panel"])

        label_widgets = [
            self.expression_label,
            self.result_label,
            self.memory_status_label,
            self.clock_label,
            self.history_title,
        ]
        for label in label_widgets:
            label.configure(background=label.master["background"], foreground=theme["text"])
        self.expression_label.configure(foreground=theme["muted"])
        self.memory_status_label.configure(foreground=theme["muted"])
        self.clock_label.configure(foreground=theme["muted"])

        self.history_listbox.configure(
            background=theme["display"],
            foreground=theme["text"],
            selectbackground=theme["operator"],
            selectforeground="#ffffff",
        )

        for button, button_kind in self.buttons:
            text_color = "#ffffff" if button_kind in {"operator", "equals", "danger"} else theme["text"]
            button.configure(
                background=theme[button_kind],
                activebackground=theme[f"{button_kind}_hover"],
                foreground=text_color,
                activeforeground=text_color,
            )

    def _bind_keyboard_shortcuts(self) -> None:
        """Connect common calculator keys to button actions."""
        self.root.bind("<Key>", self._handle_key_press)
        self.root.bind("<Return>", lambda _: self._calculate_result())
        self.root.bind("<KP_Enter>", lambda _: self._calculate_result())
        self.root.bind("<Escape>", lambda _: self._clear())
        self.root.bind("<BackSpace>", lambda _: self._backspace())
        self.root.bind("<Control-c>", lambda _: self._copy_result())
        self.root.bind("<Control-s>", lambda _: self._save_history())
        self.root.bind("<Control-l>", lambda _: self._clear_history())

    def _tick_clock(self) -> None:
        """Refresh the date and time display once per second."""
        self.date_time.set(datetime.now().strftime("%d %b %Y, %I:%M:%S %p"))
        self.root.after(1000, self._tick_clock)

    def _handle_key_press(self, event: tk.Event) -> None:
        """Handle number, decimal, and operator input from the keyboard."""
        character = event.char
        if character in "0123456789.eE":
            self._append_to_expression(character)
        elif character in "+-*/%^":
            display_operator = {"*": "x", "/": "÷"}.get(character, character)
            self._append_operator(display_operator)

    def _handle_button(self, button_text: str) -> None:
        """Route each button press to the correct calculator behavior."""
        if button_text.isdigit() or button_text == ".":
            self._append_to_expression(button_text)
        elif button_text in {"+", "-", "x", "÷", "^", "mod"}:
            operator_symbol = "%" if button_text == "mod" else button_text
            self._append_operator(operator_symbol)
        elif button_text == "%":
            self._apply_percentage()
        elif button_text == "=":
            self._calculate_result()
        elif button_text == "C":
            self._clear()
        elif button_text == "√":
            self._square_root()
        elif button_text == "±":
            self._toggle_sign()
        elif button_text == "M+":
            self._memory_add()
        elif button_text == "M-":
            self._memory_subtract()
        elif button_text == "MR":
            self._memory_recall()
        elif button_text == "MC":
            self._memory_clear()
        elif button_text == "Copy":
            self._copy_result()
        elif button_text == "Save":
            self._save_history()
        elif button_text == "History C":
            self._clear_history()
        elif button_text == "Mode":
            self._toggle_theme()
        elif button_text == "Exit":
            self.root.destroy()

    def _append_to_expression(self, value: str) -> None:
        """Add a number, decimal point, or scientific notation character."""
        self.expression.set(self.expression.get() + value)

    def _append_operator(self, operator_symbol: str) -> None:
        """Add an operator while avoiding accidental duplicate operators."""
        current_expression = self.expression.get().strip()
        if not current_expression:
            if operator_symbol == "-":
                self.expression.set("-")
            return

        if current_expression[-1] in "+-x÷%^":
            self.expression.set(current_expression[:-1] + operator_symbol)
        else:
            self.expression.set(current_expression + operator_symbol)

    def _calculate_result(self) -> None:
        """Evaluate the current expression and show the result."""
        current_expression = self.expression.get()
        try:
            calculated_result = self.evaluator.evaluate(current_expression)
        except ZeroDivisionError as error:
            self._show_error(str(error))
            return
        except (OverflowError, ValueError) as error:
            self._show_error(str(error))
            return

        formatted_result = self._format_number(calculated_result)
        self.result.set(formatted_result)
        self._add_history_item(f"{current_expression} = {formatted_result}")
        self.expression.set(formatted_result)

    def _square_root(self) -> None:
        """Calculate the square root of the current value or expression."""
        try:
            current_value = self.evaluator.evaluate(self.expression.get() or self.result.get())
            if current_value < 0:
                raise ValueError("Cannot calculate the square root of a negative number.")
            calculated_result = math.sqrt(current_value)
        except (ZeroDivisionError, OverflowError, ValueError) as error:
            self._show_error(str(error))
            return

        formatted_result = self._format_number(calculated_result)
        self.result.set(formatted_result)
        self._add_history_item(f"√({self._format_number(current_value)}) = {formatted_result}")
        self.expression.set(formatted_result)

    def _apply_percentage(self) -> None:
        """Convert the current value or expression result into a percentage."""
        try:
            current_value = self.evaluator.evaluate(self.expression.get() or self.result.get())
            calculated_result = current_value / 100
        except (ZeroDivisionError, OverflowError, ValueError) as error:
            self._show_error(str(error))
            return

        formatted_result = self._format_number(calculated_result)
        self.result.set(formatted_result)
        self._add_history_item(f"{self._format_number(current_value)}% = {formatted_result}")
        self.expression.set(formatted_result)

    def _toggle_sign(self) -> None:
        """Switch the sign of the current value."""
        try:
            current_value = self.evaluator.evaluate(self.expression.get() or self.result.get())
        except (ZeroDivisionError, OverflowError, ValueError) as error:
            self._show_error(str(error))
            return

        formatted_result = self._format_number(-current_value)
        self.result.set(formatted_result)
        self.expression.set(formatted_result)

    def _clear(self) -> None:
        """Clear the current calculation."""
        self.expression.set("")
        self.result.set("0")

    def _backspace(self) -> None:
        """Remove the last character from the expression."""
        self.expression.set(self.expression.get()[:-1])

    def _memory_add(self) -> None:
        """Add the current result to calculator memory."""
        self.memory_value += self._get_current_numeric_value()
        self._update_memory_label()

    def _memory_subtract(self) -> None:
        """Subtract the current result from calculator memory."""
        self.memory_value -= self._get_current_numeric_value()
        self._update_memory_label()

    def _memory_recall(self) -> None:
        """Place the stored memory value into the expression display."""
        self.expression.set(self._format_number(self.memory_value))
        self.result.set(self._format_number(self.memory_value))

    def _memory_clear(self) -> None:
        """Reset calculator memory to zero."""
        self.memory_value = 0.0
        self._update_memory_label()

    def _get_current_numeric_value(self) -> float:
        """Return the current expression or result as a number."""
        try:
            return self.evaluator.evaluate(self.expression.get() or self.result.get())
        except (ZeroDivisionError, OverflowError, ValueError):
            return 0.0

    def _update_memory_label(self) -> None:
        """Refresh the memory status text."""
        self.memory_label.set(f"Memory: {self._format_number(self.memory_value)}")

    def _copy_result(self) -> None:
        """Copy the visible result to the clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result.get())
        self.root.update()

    def _save_history(self) -> None:
        """Save calculation history to a text file beside this script."""
        if not self.history:
            messagebox.showinfo("History", "No calculations to save yet.")
            return

        with self.HISTORY_FILE.open("w", encoding="utf-8") as history_file:
            history_file.write("Calculator History\n")
            history_file.write(f"Saved: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
            history_file.write("\n".join(self.history))

        messagebox.showinfo("History saved", f"History saved to:\n{self.HISTORY_FILE}")

    def _add_history_item(self, history_text: str) -> None:
        """Add a calculation to the visible and saved history."""
        self.history.append(history_text)
        self.history_listbox.insert(tk.END, history_text)
        self.history_listbox.yview_moveto(1)

    def _clear_history(self) -> None:
        """Clear all stored history from the panel."""
        self.history.clear()
        self.history_listbox.delete(0, tk.END)

    def _recall_history_item(self, _: tk.Event) -> None:
        """Double-clicking a history item recalls its result."""
        selection = self.history_listbox.curselection()
        if not selection:
            return
        selected_text = self.history_listbox.get(selection[0])
        if "=" in selected_text:
            recalled_result = selected_text.split("=")[-1].strip()
            self.expression.set(recalled_result)
            self.result.set(recalled_result)

    def _toggle_theme(self) -> None:
        """Switch between dark and light themes."""
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()

    def _show_error(self, message: str) -> None:
        """Display a friendly error state."""
        self.result.set("Error")
        messagebox.showerror("Calculator error", message)

    @staticmethod
    def _format_number(number: float) -> str:
        """Format numbers clearly while supporting scientific notation."""
        if math.isinf(number) or math.isnan(number):
            raise ValueError("Result is not a valid number.")
        if number.is_integer():
            return str(int(number))
        return f"{number:.12g}"


# ---------------------------------------------------------------------------
# Optional command-line calculator mode.
# ---------------------------------------------------------------------------


def get_number_from_user(prompt: str) -> float:
    """Ask for a number until the user enters a valid numeric value."""
    while True:
        user_input = input(prompt).strip()
        try:
            return float(user_input)
        except ValueError:
            print("Please enter a valid number.")


def run_cli_calculator() -> None:
    """Run a beginner-friendly command-line calculator."""
    menu_options = {
        "1": ("Addition", add),
        "2": ("Subtraction", subtract),
        "3": ("Multiplication", multiply),
        "4": ("Division", divide),
    }

    while True:
        print("\nSimple Calculator")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Exit")

        choice = input("Choose an operation: ").strip()

        if choice == "5":
            print("Goodbye!")
            break

        if choice not in menu_options:
            print("Invalid choice. Please select a menu option from 1 to 5.")
            continue

        first_number = get_number_from_user("Enter the first number: ")
        second_number = get_number_from_user("Enter the second number: ")
        operation_name, operation = menu_options[choice]

        try:
            calculation_result = operation(first_number, second_number)
        except ZeroDivisionError as error:
            print(f"Error: {error}")
            continue

        print(f"{operation_name} result: {calculation_result}")


def run_gui_calculator() -> None:
    """Start the Tkinter calculator application."""
    root = tk.Tk()
    ModernCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli_calculator()
    else:
        run_gui_calculator()
