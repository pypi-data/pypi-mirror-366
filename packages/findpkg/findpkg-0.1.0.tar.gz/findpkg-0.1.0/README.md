# 🔍 findpkg

**findpkg** is a simple Python CLI tool that helps you locate which virtual environments a specific Python package is installed in.

---

## 🚀 Features

- Quickly search across local virtual environments
- Works with standard Python & virtualenv/venv environments
- Lightweight and fast

---

## 📦 Installation

### Option 1: Install via `pip`

```bash
pip install findpkg
```

### Option 2: Install from source (for development)
```bash
git clone https://github.com/<your-username>/findpkg.git
cd findpkg
pip install .
```

## 🛠 Usage
```bash
python -m findpkg <package_name>
```

### Example
- Input
```bash
python -m findpkg pandas
```

- Output
```bash
Searching for package 'pandas'...

Package 'pandas' found in the following location(s):

→ C:\Users\User\Desktop\Projects\myenv1\Lib
→ C:\Users\User\Desktop\Projects\myenv2\Lib
```

## Coming Soon
 - Unit test
 - Mac/Linux support (cross-platform paths)



## 🤝 Contributing
PRs are welcome! Please feel free to fork this repo and contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
