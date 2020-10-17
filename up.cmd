python setup.py sdist bdist_wheel
twine upload dist/* --skip-existing -u koefoeden -p 8Guleposer
PAUSE
pip install --upgrade evolutionsimulator