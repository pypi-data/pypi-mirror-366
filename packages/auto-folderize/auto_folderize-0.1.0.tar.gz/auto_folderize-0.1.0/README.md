Here’s your polished and professional `README.md` in full **Markdown format** with ✅ emojis, headings, code blocks, and clarity — ready to upload to **GitHub or PyPI**:

---

````markdown
# Auto-Folderize 🗂️

**Auto-Folderize** is a lightweight and easy-to-use Python library that organizes files in a folder into subfolders based on their file extensions. It supports both **default categorization** and **custom rules**. You can even automatically delete empty folders after organizing.

---

## 📦 Installation

```bash
pip install auto-folderize
````

---

## 🚀 Usage

```python
from auto_folderize import organize, clean

# Organize using default rules
organize(r"D:\test_lib")

# Organize using custom rules
custom_rules = {
    "MyPhotos": ["jpg", "jpeg", "webp"],
    "MyText": ["txt", "md"],
    "Backups": ["zip", "rar"]
}
organize(r"D:\test_lib", rules=custom_rules)

# Clean up empty folders after organizing
clean(r"D:\test_lib")
```

---

## 🧠 Features

* ✅ Automatically sorts files into categories like images, documents, videos, etc.
* ✅ Fully customizable rule sets based on your needs
* ✅ Cleans up leftover empty folders after organization
* ✅ Easy to integrate and extend for automation scripts

---

## 📁 Default Rules (if no custom rules provided)

```python
default_rules = {
    "images": ["jpg", "jpeg", "png", "gif", "bmp"],
    "documents": ["pdf", "docx", "doc", "txt", "pptx", "xlsx"],
    "videos": ["mp4", "mov", "avi", "mkv"],
    "audio": ["mp3", "wav", "aac"],
    "archives": ["zip", "rar", "7z", "tar", "gz"],
    "code": ["py", "js", "java", "c", "cpp", "cs", "html", "css", "json"],
}
```

---

## 👤 Author

Made with 💻 by **Sourav Sandilya**
📧 Email: `youremail@example.com`
🌐 GitHub: [github.com/yourusername](https://github.com/yourusername)

---

## 📄 License

This project is licensed under the **MIT License** – feel free to use and contribute!

---

## 🌟 Contributions Welcome!

Found a bug or have a cool idea?
Fork the repo, open an issue, or make a pull request! Let's improve folder organization together.

```

---

✅ You can now:

- Save this as `README.md`
- Upload it to GitHub with your code
- It’ll also be used for your PyPI page if you add it in `setup.py`

Would you like a matching `setup.py` or `LICENSE` file too?
```
