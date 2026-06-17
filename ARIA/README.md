Option A: Running with the helper script (Recommended)
You can run the frontend helper script directly by navigating back up to the ARIA folder:

powershell
# 1. Navigate to the ARIA folder
cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA"
# 2. Run the startup script (it automatically adds the local Node folder to PATH)
.\start-dev.ps1
Option B: Running both manually in separate terminals
If you prefer to run them manually in separate terminal windows:

Terminal 1: Backend
powershell
# 1. Navigate to ARIA folder
cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA"
# 2. Activate Python virtual environment (located in the parent directory)
..\venv\Scripts\Activate.ps1
# 3. Start the FastAPI/uvicorn server
python -m uvicorn ws_server:app --reload --port 8000
Terminal 2: Frontend
powershell
# 1. Navigate to the React app folder
cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA\my-aria-app"
# 2. Add local Node.js binaries to your session PATH so npm works
$env:PATH = "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA\node;" + $env:PATH
# 3. Start the React/Vite development server
npm run dev