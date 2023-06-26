rm -rf env/

echo "Creating Python virtual environment env"
python3 -m venv env/
source env/bin/activate
pip3 install --upgrade pip

echo "Install packages in requirements.txt"
pip3 install -r requirements.txt
deactivate
