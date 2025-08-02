# smallneuron
Network Programming platform

Requirements

mqtt bridge:
    sudo pip3 install paho-mqtt

gpio bridge:
    sudo pip3 install --upgrade OPi.GPIO


To use gpio h3: install gpio_h3, run 
  ./build
##
##  Python Package
# Install tools
sudo apt install python3-pip python3-venv
python3 -m pip install build # pip3 install build


# Build
python3 -m build
python3 -m twine upload --repository testpypi dist/* # test
python3 -m twine upload  dist/*                      # prod


# Install
Installing module
	sudo python3 -m pip install --upgrade --index-url https://test.pypi.org/simple/ --no-deps smallneuron-pelainux    # test
  
  sudo python3 -m pip install --upgrade --index-url https://pypi.org/simple/ --no-deps smallneuron==1.1.1 # prod
  sudo python3 -m pip install --upgrade --index-url https://pypi.org/simple/ --break-system-packages --no-deps smallneuron==1.1.1 # prod