# SharedPreferFlet

A simple and secure Python module for saving and retrieving preferences using encrypted JSON files, inspired by Android's SharedPreferences system.  
Ideal for desktop and local Python apps that need to persist user settings safely.

## ✨ Features

- 🔐 AES encryption to protect your preferences
- 💾 Store and retrieve strings, integers, booleans, lists, and dictionaries
- 🧼 Auto-encryption/decryption during save/load
- 👌 Context manager support for safe usage
- 🧪 Minimal dependencies

## 📦 Installation

Install using pip:

```bash
pip install sharedpreferflet
```

```python
from sharedpreferflet.sharedflet.core import SharedPreferenceFlet

# Using context manager (automatically closes)
with SharedPreferenceFlet("myprefs", password="1234") as prefs:
    prefs.setString("token", "xyz")
    print(prefs.getString("token"))

# Manual open/close usage
prefs = SharedPreferenceFlet("myprefs", password="SuperSecure123")
prefs.setString("email", "user@example.com")
print(prefs.getString("email"))

prefs.setBool("dark_mode", True)
print(prefs.getBool("dark_mode"))

prefs.Close()
```

<h3>📋 Available Methods</h3>

<table>
  <thead>
    <tr>
      <th>Method</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>setString(key, value)</code></td><td>Save a string</td></tr>
    <tr><td><code>getString(key)</code></td><td>Retrieve a string</td></tr>
    <tr><td><code>setBool(key, value)</code></td><td>Save a boolean</td></tr>
    <tr><td><code>getBool(key)</code></td><td>Retrieve a boolean</td></tr>
    <tr><td><code>setInt(key, value)</code></td><td>Save an integer</td></tr>
    <tr><td><code>getInt(key)</code></td><td>Retrieve an integer</td></tr>
    <tr><td><code>setStringList(key, value)</code></td><td>Save a list</td></tr>
    <tr><td><code>getStringList(key)</code></td><td>Retrieve a list string</td></tr>
    <tr><td><code>setList(key, value)</code></td><td>Save a a list string</td></tr>
    <tr><td><code>getList(key)</code></td><td>Retrieve a list</td></tr>
    <tr><td><code>getDouble(key, value)</code></td><td>Save a Double</td></tr>
    <tr><td><code>getDouble(key)</code></td><td>Retrieve a dictionary</td></tr>
    <tr><td><code>remove()</code></td><td>Remove all saved keys</td></tr>
    <tr><td><code>Close()</code></td><td>Close the storage (when not using <code>with</code>)</td></tr>
  </tbody>
</table>


🔐 Security
All data is encrypted using AES-256 with a user-provided password.
The encrypted file is stored with a .lock extension and is unreadable without the correct password.

📁 File Format
Encrypted preferences are stored as binary .lock files.
On disk, the original file is removed after encryption, and only the locked file remains.

🔧 Constructor Options
```python
SharedPreferenceFlet(filename, password)
```
filename — The name of the preference file.

password — A strong password to encrypt/decrypt the data.

🧪 Example Test Use
```python
with SharedPreferenceFlet("settings", password="mypassword") as prefs:
    prefs.setInt("volume", 80)
    if prefs.getBool("dark_theme"):
        print("Dark mode is enabled")
```
🛠 Requirements
Python 3.6+

pycryptodome package (installed automatically with pip)

📄 License
This project is licensed under the MIT License. See LICENSE for details.


Created with ❤️ for developers who miss SharedPreferences in Python.

