# AI Study Assistant

A simple study assistant using `google/flan-t5-small` from Hugging Face.

## Features

- Summarize study text
- Answer questions using provided context

## Setup

1. Create a Python environment.       
2. Install dependencies:

```bash
python -m venv venv

pip install -r requirements.txt
```

### Activate virtual environment (Windows PowerShell)

If you created a virtual environment named `venv` in the project folder, activate it in PowerShell with:

```powershell
.\\venv\\Scripts\\Activate
# prompt becomes: (venv) PS C:\\Users\\...\\week1\\mini-project>
```

If you're using CMD (Command Prompt) instead, run:

```cmd
venv\\Scripts\\activate.bat
```

On macOS / Linux use:

```bash
source venv/bin/activate
```

## Run

```bash
python study_assistant.py
```

## Usage

- Choose `1` to summarize text.
- Choose `2` to ask a question with context.
- Type `3` or `exit` to quit.

If prompted for a text source, you can paste text directly or enter a path to a text file.


(venv) PS C:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\week1\mini-project> .\venv\Scripts\Activate.ps1                           


