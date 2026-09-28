@echo off
echo ============================================
echo   DocuMind AI - Powered by Mistral
echo   PDF Chatbot for AppLab Assessment
echo ============================================
echo.

echo [1/4] Creating virtual environment...
py -3.10 -m venv venv

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies (first run may take 5-10 minutes)...
python -m pip install --upgrade pip --quiet
pip install Flask==3.0.0 flask-cors==4.0.0 PyPDF2==3.0.1 torch==2.5.1 transformers==4.44.0 sentence-transformers==2.7.0 numpy==1.24.3 python-dotenv==1.0.0 werkzeug==3.0.1 requests==2.31.0

echo.
echo [4/4] Starting DocuMind AI...
echo.
echo ============================================
echo   App running at: http://localhost:5000
echo   Press CTRL+C to stop
echo ============================================
echo.

python app.py

pause
