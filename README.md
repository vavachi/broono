# Broono - MSSQL Schema Comparison Tool

Broono is a professional, high-performance toolkit designed for SQL Server developers to compare schemas, identify differences, and generate precise synchronization scripts.

## 🚀 Features

- **Multi-Object Analysis**: Support for Tables, Stored Procedures, Functions, and Triggers.
- **Selective Synchronization**: Checkbox-based selection allows you to generate scripts for specific objects only.
- **Dynamic Diff View**: Side-by-side visual comparison with high-contrast highlighting of additions and deletions.
- **Object Search & Filtering**: Real-time search bar to quickly locate specific schema objects in large databases.
- **External Object Filtering**: Option to load a text file containing a subset of objects to focus your comparison.
- **Premium Themes**: Includes "Antigravity Dark Mode" for deep-space aesthetics and "Cerulean Light" for a crisp, blue-tinted professional look.
- **High-Density UI**: Optimized layout with dynamic script reveal to maximize workspace efficiency.

## 🛠 How It Works

1.  **Connection**: Securely connect to your Source (Target) and Base (Source) databases via standard ODBC/SQL Server authentication.
2.  **Comparison**: Broono extracts schema metadata and performs a deep analysis to find structural differences.
3.  **Review**: Differences are displayed in a hierarchical tree. You can search, filter, and double-click any object to see a detailed side-by-side diff.
4.  **Selection**: Select the objects you wish to update using the interactive checkboxes.
5.  **Generation**: Click "Generate Script" to produce a ready-to-execute SQL script to synchronize your target database.

## 💻 Windows Installation

### 1. Requirements
- **Python 3.10+**: Download from [python.org](https://www.python.org/).
- **ODBC Driver**: [Microsoft ODBC Driver 17/18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/broono.git
cd broono

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## 📦 Tech Stack & Libraries

Broono is built using a modern, robust Python stack:

- **[Python](https://www.python.org/) (3.10+)**: Core programming language.
- **[PyQt6](https://pypi.org/project/PyQt6/)**: For the modern, responsive Graphical User Interface.
- **[pyodbc](https://pypi.org/project/pyodbc/)**: For high-performance database connectivity via ODBC.
- **difflib**: (Built-in) For precise side-by-side text difference analysis.
- **json**: (Built-in) For managing local connection profiles and configuration.
- **PyInstaller**: (Optional) For compiling the application into a standalone Windows executable.

## 📦 Creating an Executable (.exe)
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name Broono main.py
```

## 🌟 Credits

This project was developed with the power of:
- **Antigravity Editor**: The intelligent orchestration agent that handled the design, logic, and implementation.
- **Gemini**: The foundational intelligence powering the reasoning and code generation of this tool.

---
*Developed by the Google DeepMind team for high-performance agentic coding.*
