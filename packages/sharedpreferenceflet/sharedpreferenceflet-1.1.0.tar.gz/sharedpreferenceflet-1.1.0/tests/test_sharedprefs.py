# # If you want to use SharedPreferenceFlet for securely storing preferences,
# # you can use the following code snippet to set and get preferences.

from sharedflet import SharedPreferenceFlet

# Example 1: Using context manager (recommended)
with SharedPreferenceFlet("myprefsdd") as prefs:
    prefs.setString("token", "xyz")
    print(prefs.getString("token"))

# # Example 2: Manual open and close
prefs = SharedPreferenceFlet("myprefs", password="SuperSecure123")
prefs.setString("email", "user@example.com")
print(prefs.getString("email"))

prefs.setBool("dark_mode", True)
print(prefs.getBool("dark_mode"))

prefs.Close()

