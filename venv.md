Great question — let’s build you a **complete toolkit of venv commands on Windows**, plus the theory so you understand *why* each step matters.  

---

## 🧠 Theory: What is a venv?
- A **virtual environment (venv)** is an isolated Python environment.  
- It keeps dependencies separate from your global Python installation.  
- Each venv has its own `python.exe`, `pip`, and `site-packages`.  
- This isolation prevents version conflicts between projects (e.g., Django 4 in one project, Flask 2 in another).  

Think of it as a **sandbox**: you can install packages freely without messing up your system Python.

---

## ⚙️ Essential Commands on Windows

### 1. **Create a venv**
```powershell
# Create a venv named .venv in the current folder
python -m venv .venv

# Or give it a custom name
python -m venv myenv
```

---

### 2. **Activate a venv**
```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1

# Command Prompt (cmd)
.\.venv\Scripts\activate.bat
```

👉 Once activated, you’ll see the venv name in parentheses before your prompt, e.g. `(.venv) PS C:\...>`.

---

### 3. **Deactivate a venv**
```powershell
deactivate
```
This returns you to the global/system Python.

---

### 4. **Delete a venv**
Since venvs are just folders:
```powershell
Remove-Item -Recurse -Force .\.venv
Remove-Item -Recurse -Force .\myenv
```

⚠️ Always deactivate first before deleting.

---

### 5. **Check which venv is active**
```powershell
where python
python -c "import sys; print(sys.prefix)"
```
If inside a venv, the path will point to its `Scripts` folder.

---

### 6. **List all venvs in one place**
There’s no built‑in registry of venvs — they’re just directories.  
You can scan your user folder for them:

```powershell
# Find all folders starting with .venv or named venv
Get-ChildItem -Recurse -Directory -Filter ".venv*"
Get-ChildItem -Recurse -Directory -Filter "venv"
```

Or search across your drive:
```powershell
Get-ChildItem C:\Users\cnpan -Recurse -Directory -Include venv,.venv* -ErrorAction SilentlyContinue
```

---

### 7. **Handy extras**
- **Check installed packages in a venv**:
  ```powershell
  pip list
  ```
- **Freeze dependencies to a file**:
  ```powershell
  pip freeze > requirements.txt
  ```
- **Recreate venv from requirements**:
  ```powershell
  python -m venv newenv
  .\newenv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

## 🚀 Best Practices
- Use `.venv` as the default name inside each project folder — keeps things consistent.  
- Always activate before running project code.  
- Keep a `requirements.txt` so you can rebuild environments easily.  
- Delete old venvs when projects are done to save disk space.  

---

Would you like me to write you a **PowerShell script** that automatically lists all venvs under your `C:\Users\cnpan` directory and gives you an interactive choice to delete them? That way you’ll have a one‑stop cleanup tool.