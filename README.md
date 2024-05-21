# 科学计算器

## 如何运行

- `python>=3.8`
- `pip install pyside6==6.4.2`
- `python calculator.py`

#### !!请确保安装对应版本的库
#### !!否则可能会出现兼容性问题

## 注意事项

- 本软件用于科学计算，支持多种计算模式和高级计算功能。
- 如果您希望使用自己的模型或数据，请确保数据格式与软件要求一致。
- 软件仍在持续优化中，欢迎反馈和建议。
- 如果启用了保存结果功能，结果将保存到 `./results` 目录中。
- 界面设计文件为 `calculator.ui`，如果进行了修改，需要使用 `pyside6-uic calculator.ui > ui/calculator.py` 命令重新生成 `.py` 文件。
- 资源文件为 `resources.qrc`，如果修改了默认图标，需要使用 `pyside6-rcc resources.qrc > ui/resources_rc.py` 命令重新生成 `.py` 文件。

## 主要功能

- **基本运算**：加、减、乘、除、括号运算
- **高级函数**：正弦、余弦、正切、对数、平方根
- **复数运算**：支持 a + bi 和 r ∠ φ 两种格式
- **方程求解**：一元多次方程和多元一次方程求解

## 使用指南

1. 运行以下命令启动计算器：
- [python calculator.py](https://github.com/L1Shun/Calculator/blob/main/calculate.py)

