cd "C:\VSCode\Historical_Gainers_Site"
python utility_functions.py
git add static/top_gainers.json
git commit -m "Daily update: %date%" || echo "No changes"
git push
echo Done! %date% %time%