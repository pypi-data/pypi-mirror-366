<p align="center">
  <img src="https://raw.githubusercontent.com/rlapine/detaillogger/refs/heads/main/assets/detaillogger_logo_2.png" alt="DetailLogger logo" width="400"/>
</p>

---

## 🎨 DetailLogger V 0.1.4

---

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/rlapine/detaillogger?style=social)](https://github.com/rlapine/detaillogger/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/rlapine/detaillogger?style=social)](https://github.com/rlapine/detaillogger/network/members)

---

## ✨ Overview

DetailLogger is a lightweight Python utility for enhanced logging and exception tracing. It automatically captures contextual information—such as file name, function, and line number—whenever messages or exceptions are logged. Ideal for debugging, monitoring, and building maintainable systems.

---

## 📦 Installation

`pip install detaillogger`

---

## ⚙️ Features

- ✅ Logs messages with caller context  
- ✅ Captures exceptions with full traceback  
- ✅ Supports console and file-based logging  
- ✅ Uses wrapper functions for quick integration  
- ✅ Built entirely on standard libraries

---

## ✍️ API Overview

- `DetailLogger(level, fmt, file_name)`: Create an instance with optional file output and log level  
- `log(message: str)`: Logs message with caller metadata  
- `log_exception(ex: BaseException, details: Optional[str])`: Logs exception type, message, optional details, and source context

---

## 🧪 Usage

# Run the built-in CLI demo for testing:

`python detaillogger.py`

# Embedded Example

```
from detaillogger import log, log_exception

log("This is a message to log.")

try:
    x = 1 / 0
except Exception as e:
    log_exception(e, details="This is a message about the exception to log.")
```

**Console Output:**

```
2025-07-28 17:02:27,674 - DEBUG - Details:  This is a message to log.
2025-07-28 17:02:27,674 - DEBUG - From:     c:\Users\ryan\...detaillogger.py
2025-07-28 17:02:27,675 - DEBUG - Function: main()
2025-07-28 17:02:27,675 - DEBUG - Line:     3

2025-07-28 17:05:22,185 - DEBUG - Exception type:    ZeroDivisionError
2025-07-28 17:05:22,186 - DEBUG - Exception message: division by zero
2025-07-28 17:05:22,186 - DEBUG - Details:           This is a message about the exception to log.
2025-07-28 17:05:22,186 - DEBUG - File:              ...detaillogger.py
2025-07-28 17:05:22,186 - DEBUG - Function:          main()
2025-07-28 17:05:22,186 - DEBUG - Line:              6
```

# Embedded Example

```
# To log to a file and console, instantiate DetailLogger class with filename.
from detaillogger import log, log_exception

logger = DetailLogger(file_name="detail.log")

log("This is a message to log to file.")

try:
    x = 1 / 0
except Exception as e:
    log_exception(e, details="This is a message about the exception to log to file.")
```

**File Output:**

![detail.log](https://raw.githubusercontent.com/rlapine/detaillogger/main/assets/image.png)

---

## 🔧 Built-in demo:

`python detaillogger.py`

```
Also log to file? (y/n):y
Enter filname:detail.log

Options
1) Log details.
2) Log 'division by zero' exception.
3) Log custom exception.
q) Exit.
Enter an option:1

Enter message to log:This is a message.
2025-07-30 14:46:04,161 - DEBUG - Details:  This is a message.
2025-07-30 14:46:04,161 - DEBUG - From:     c:\Users\ryan\Visual Code Projects\git_repositories\detaillogger\detaillogger.py
2025-07-30 14:46:04,162 - DEBUG - Function: main()
2025-07-30 14:46:04,162 - DEBUG - Line:     179

Message logged.
```

---

## 🧱 File Structure

```
detaillogger/
├── detaillogger.py         # Core module
├── test_detaillogger.py    # Unit test suite
├── assets/                 # Folder for images, badges, or other static assets
│   ├── detaillogger_logo_2.png     # Logo for documentation
│   └── image.png                   # File output 
├── README.md             # Documentation
├── detaillogger.log      # Optional output log file
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue to discuss improvements first.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Created by Ryan LaPine [@rlapine](https://github.com/rlapine) — a technically skilled developer focused on clarity, maintainability, and audience-ready documentation. This class is part of a broader effort to build reusable, well-documented tools for data-driven projects.

---

## 📬 Contact

Feel free to reach out with questions or collaboration ideas:

📧 github.stunt845@passinbox.com  
🔗 GitHub: [@rlapine](https://github.com/rlapine)
