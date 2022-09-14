# auto-virtual-machine
Project to create between 1 to 5 virtual machines using images .qcow2 and .xml by running a script in Python
## Intructions
```
git clone https://github.com/danisanz22/auto-virtual-machine.git
cd auto-virtual-machine
python3 auto-p2.py prepare "Number of virtual machines"
```
If you do not insert any number, the project will create automatically 3 virtual machines. You must insert a number between 1 to 5.

To run the servers
```
python3 auto-p2.py launch
```
To stop the servers
```
python3 auto-p2.py stop
```
If you want to restart the servers repeat the command of launching.

To release the servers
```
python3 auto-p2-py
```
