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
# 2. Start the FastAPI/uvicorn server
python -m uvicorn ws_server:app --reload --port 8000


Terminal 2: Frontend
powershell
# 1. Navigate to the ARIA folder
>> cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA"
>> 
>> # 2. Run the startup script (it automatically adds the local Node folder to PATH)
>> .\start-dev.ps1
>>