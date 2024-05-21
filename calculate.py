import sys
import re
import numpy as np
from fractions import Fraction
from sympy import nsimplify, symbols, solve, Eq
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QTextEdit, QPushButton, QComboBox, QLineEdit, QLabel, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor

class EquationDialog(QDialog):
    def __init__(self, title, options, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout(self)
        self.combo = QComboBox(self)
        self.combo.addItems(options)
        self.layout.addWidget(self.combo)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_selected_option(self):
        return self.combo.currentText()

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("科学计算器")
        self.setGeometry(100, 100, 400, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.display = QTextEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(100)
        self.display.setFont(QFont('Arial', 18))
        self.layout.addWidget(self.display)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(['Degrees', 'Radians'])
        self.mode_selector.currentTextChanged.connect(self.change_mode)
        self.mode_selector.setFixedHeight(30)
        self.mode_selector.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.mode_selector)

        self.menu_selector = QComboBox()
        self.menu_selector.addItems(['Calculate', 'Complex', 'Equation'])
        self.menu_selector.currentTextChanged.connect(self.change_menu)
        self.menu_selector.setFixedHeight(30)
        self.menu_selector.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.menu_selector)

        self.buttons_layout = QGridLayout()
        self.layout.addLayout(self.buttons_layout)

        self.mode = 'Degrees'
        self.menu = 'Calculate'
        self.fraction_mode = True  # 分数模式开关
        self.result = None  # 存储最后计算结果
        self.complex_format = 'a+bi'  # 复数模式 a+bi or r∠φ
        self.equation_type = None  # 方程类型
        self.equation_order = None  # 方程次数或未知数数量
        self.ans = None  # 存储上一次计算结果        
        self.create_buttons()

    def create_buttons(self):
        for i in reversed(range(self.buttons_layout.count())):
            self.buttons_layout.itemAt(i).widget().setParent(None)

        self.mode_selector.setVisible(self.menu != 'Equation')

        if hasattr(self, 'complex_mode_selector'):
            self.complex_mode_selector.setVisible(self.menu == 'Complex')
            if self.menu != 'Complex':
                self.layout.removeWidget(self.complex_mode_selector)

        if self.menu == 'Calculate':
            self.setMinimumSize(400, 700)
            self.setMaximumSize(400, 700)
            # 上方功能按钮
            top_buttons = [
                ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('log', 0, 3), ('√', 0, 4), 
                ('x10^', 1, 0), ('(', 1, 1), (')', 1, 2), ('/', 1, 3), ('*', 1, 4),
                ('S<->D', 2, 0), ('^', 2, 1), ('π', 2, 2),('<-', 2, 3), ('->', 2, 4),
                ('Ans', 3, 0),
            ]
        elif self.menu == 'Complex':
            self.setMinimumSize(400, 700)
            self.setMaximumSize(400, 700)
            # 上方功能按钮
            top_buttons = [
                ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('log', 0, 3), ('√', 0, 4), 
                ('x10^', 1, 0), ('(', 1, 1), (')', 1, 2), ('/', 1, 3), ('*', 1, 4),
                ('S<->D', 2, 0), ('^', 2, 1), ('π', 2, 2), ('<-', 2, 3), ('->', 2, 4),
                ('Ans', 3, 0),('i', 3, 1), ('∠', 3, 2),
            ]
        elif self.menu == 'Equation':
            self.setMinimumSize(400, 400)
            self.setMaximumSize(400, 400)
            self.show_equation_dialog()
            return

        for text, row, col in top_buttons:
            button = QPushButton(text)
            button.setFixedSize(60, 60)
            button.setFont(QFont('Arial', 11))
            button.clicked.connect(self.on_button_click)
            self.buttons_layout.addWidget(button, row, col)

        # 下方数字和基本运算符按钮
        bottom_buttons = [
            ('7', 4, 0), ('8', 4, 1), ('9', 4, 2), ('+', 4, 3),
            ('4', 5, 0), ('5', 5, 1), ('6', 5, 2), ('-', 5, 3),
            ('1', 6, 0), ('2', 6, 1), ('3', 6, 2), ('=', 6, 3),
            ('0', 7, 0), ('.', 7, 1), ('C', 7, 2), ('DEL', 7, 3),
        ]
        for text, row, col in bottom_buttons:
            button = QPushButton(text)
            button.setFixedSize(80, 80)
            button.setFont(QFont('Arial', 14))
            button.clicked.connect(self.on_button_click)
            self.buttons_layout.addWidget(button, row, col)

        if self.menu == 'Complex':
            self.complex_mode_selector = QComboBox()
            self.complex_mode_selector.addItems(['a + bi', 'r ∠ φ'])
            self.complex_mode_selector.currentTextChanged.connect(self.change_complex_mode)
            self.complex_mode_selector.setFixedHeight(30)
            self.complex_mode_selector.setFont(QFont('Arial', 12))
            self.layout.addWidget(self.complex_mode_selector)

    def show_equation_dialog(self):
        dialog = EquationDialog("选择方程类型", ["一元多次方程", "多元一次方程"], self)
        if dialog.exec_() == QDialog.Accepted:
            self.equation_type = dialog.get_selected_option()
            if self.equation_type == "一元多次方程":
                self.show_order_dialog("选择最高次方", ["2", "3", "4"])
            else:
                self.show_order_dialog("选择未知数数量", ["2", "3", "4"])

    def show_order_dialog(self, title, options):
        dialog = EquationDialog(title, options, self)
        if dialog.exec_() == QDialog.Accepted:
            self.equation_order = int(dialog.get_selected_option())
            self.show_equation_input_page()

    def show_equation_input_page(self):
        for i in reversed(range(self.buttons_layout.count())):
            self.buttons_layout.itemAt(i).widget().setParent(None)

        if self.equation_type == "一元多次方程":
            display_text = ""
            for i in range(self.equation_order, -1, -1):
                display_text += f"0x^{i} + " if i > 0 else "0"
            self.display.setText(display_text)

            instructions = QLabel("请依次输入各项系数：")
            self.buttons_layout.addWidget(instructions, 0, 0, 1, 2)

        self.coefficient_inputs = []
        self.current_index = 0

        if self.equation_type == "一元多次方程":
            for i in range(self.equation_order + 1):
                label = QLabel(f"系数 x^{self.equation_order - i}:")
                self.buttons_layout.addWidget(label, i + 1, 0)
                input_field = QLineEdit()
                self.coefficient_inputs.append(input_field)
                self.buttons_layout.addWidget(input_field, i + 1, 1)

            calc_button = QPushButton("计算")
            calc_button.clicked.connect(self.solve_polynomial)
            self.buttons_layout.addWidget(calc_button, self.equation_order + 2, 1)

        elif self.equation_type == "多元一次方程":
            self.equations = []
            for i in range(self.equation_order):
                equation_line = []
                for j in range(self.equation_order):
                    input_field = QLineEdit()
                    input_field.setPlaceholderText(f"x{j+1} 的系数")
                    equation_line.append(input_field)
                    self.buttons_layout.addWidget(input_field, i, j)
                result_field = QLineEdit()
                result_field.setPlaceholderText("结果")
                equation_line.append(result_field)
                self.buttons_layout.addWidget(result_field, i, self.equation_order)
                self.equations.append(equation_line)

            calc_button = QPushButton("计算")
            calc_button.clicked.connect(self.solve_linear_system)
            self.buttons_layout.addWidget(calc_button, self.equation_order, self.equation_order)

    def solve_polynomial(self):
        try:
            coefficients = [float(input_field.text()) for input_field in self.coefficient_inputs]
            x = symbols('x')
            equation = sum(coef * x**exp for coef, exp in zip(coefficients, range(self.equation_order, -1, -1)))
            solutions = solve(equation, x)
            self.display.setText(f"解: {solutions}")
        except Exception as e:
            self.display.setText("Error")

    def solve_linear_system(self):
        try:
            A = []
            B = []
            for equation in self.equations:
                coeffs = [float(input_field.text()) for input_field in equation[:-1]]
                result = float(equation[-1].text())
                A.append(coeffs)
                B.append(result)
            A = np.array(A)
            B = np.array(B)
            solutions = np.linalg.solve(A, B)
            result_text = ", ".join([f"x{i+1} = {sol}" for i, sol in enumerate(solutions)])
            self.display.setText(f"解: {result_text}")
        except Exception as e:
            self.display.setText("Error")

    def change_mode(self, mode):
        self.mode = mode

    def change_menu(self, menu):
        self.menu = menu
        self.create_buttons()

    def change_complex_mode(self, mode):
        self.complex_format = mode

    def on_button_click(self):
        button = self.sender()
        text = button.text()

        if text == 'C':
            self.display.clear()
            self.result = None
        elif text == 'DEL':
            cursor = self.display.textCursor()
            cursor.deletePreviousChar()
        elif text == '=':
            try:
                result = self.evaluate_expression(self.display.toPlainText())
                self.ans = result
                self.result = result
                self.display.setText(self.format_result(result))
            except Exception as e:
                self.display.setText("Error")
                self.result = None
        elif text == 'S<->D':
            self.toggle_fraction_mode()
        elif text == 'x10^':
            self.insert_at_cursor('e')
        elif text == '√':
            self.insert_at_cursor('sqrt(')
        elif text == 'π':
            self.insert_at_cursor('pi')
        elif text == 'i':
            self.insert_at_cursor('j')
        elif text == '∠':
            self.insert_at_cursor('∠')
        elif text == 'Ans':
            if self.ans is not None:
                self.insert_at_cursor(str(self.ans))
        elif text == '<-':
            cursor = self.display.textCursor()
            cursor.movePosition(QTextCursor.Left)
            self.display.setTextCursor(cursor)
        elif text == '->':
            cursor = self.display.textCursor()
            cursor.movePosition(QTextCursor.Right)
            self.display.setTextCursor(cursor)
        else:
            self.insert_at_cursor(text)

    def insert_at_cursor(self, text):
        cursor = self.display.textCursor()
        cursor.insertText(text)
        self.display.setTextCursor(cursor)

    def toggle_fraction_mode(self):
        if self.result is not None:
            if self.fraction_mode:
                # 切换到小数
                self.display.setText(str(float(self.result)))
            else:
                # 切换到分数/根号
                self.display.setText(self.format_result(self.result))
            self.fraction_mode = not self.fraction_mode

    def evaluate_expression(self, expression):
        # 替换 ^ 为 ** 进行幂运算
        expression = expression.replace('^', '**')

        # 使用正则表达式为函数添加括号
        functions = ['sin', 'cos', 'tan', 'log', 'sqrt', 'pi']
        for func in functions:
            expression = re.sub(rf'({func})\s*([0-9.]+)', rf'\1(\2)', expression)

        # 根据模式转换角度
        if self.mode == 'Degrees':
            expression = expression.replace('sin', 'np.sin(np.deg2rad')
            expression = expression.replace('cos', 'np.cos(np.deg2rad')
            expression = expression.replace('tan', 'np.tan(np.deg2rad')
        else:
            expression = expression.replace('sin', 'np.sin')
            expression = expression.replace('cos', 'np.cos')
            expression = expression.replace('tan', 'np.tan')

        expression = expression.replace('log', 'np.log10')
        expression = expression.replace('sqrt', 'np.sqrt')
        expression = expression.replace('pi', 'np.pi')

        # 处理复数模式
        if self.menu == 'Complex':
            expression = self.handle_complex(expression)

        # 添加缺少的右括号
        expression = self.add_missing_parentheses(expression)

        return eval(expression)

    def handle_complex(self, expression):
        if '∠' in expression:
            parts = expression.split('∠')
            r = float(eval(parts[0]))
            phi = float(eval(parts[1]))
            result = r * (np.cos(np.deg2rad(phi)) + 1j * np.sin(np.deg2rad(phi)))
            return str(result)
        return expression

    def format_result(self, result):
        if self.menu == 'Complex':
            if self.complex_format == 'r ∠ φ':
                r = abs(result)
                phi = np.angle(result, deg=True)
                return f"{r} ∠ {phi}"
            else:
                return str(result)
        if isinstance(result, (int, float)):
            if float(result).is_integer():
                return str(int(result))
            else:
                sqrt_result = nsimplify(result, rational=True)
                if sqrt_result**2 == result:
                    return f"√{sqrt_result}"
                fraction_result = Fraction(result).limit_denominator()
                return str(fraction_result)
        return str(result)

    def add_missing_parentheses(self, expression):
        # 添加缺少的右括号
        open_parentheses = expression.count('(')
        close_parentheses = expression.count(')')
        if open_parentheses > close_parentheses:
            expression += ')' * (open_parentheses - close_parentheses)
        return expression

if __name__ == "__main__":
    app = QApplication(sys.argv)

    calculator = Calculator()
    calculator.show()

    sys.exit(app.exec())
