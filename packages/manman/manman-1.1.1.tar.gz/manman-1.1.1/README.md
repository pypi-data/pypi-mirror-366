# manman
GUI for deployment and monitoring of servers and applications
associated with specific tasks or apparatuses.<br>

The GUI can control multiple independent apparatuses in different tabs.

The 'status' column dynamically shows the color-coded status of the server.

The commands are executed by right clicking on the cells in the 'Applications' (leftmost) column.<br>
The top left cell executes table-wide commands:<br>
**Check All, Start All, Stop All**<br>
It also holds commands to
- delete current tab (**Delete**),
- edit the table of the current tab(**Edit**),
- condense and expannd table arrangement (**Condense and Uncondense**).

The following actions are defined for regular rows:
  - **Check**
  - **Start**
  - **Stop**
  - **Command**: will display the command for starting the manager

Definition of actions, associated with an apparatus, are defined in the 
startup dictionary of the python scripts, code-named as apparatus_NAME.py. See examples in the config directory.

Supported keys are:
  - **'cmd'**: command which will be used to start and stop the manager,
  - **'cd'**:   directory (if needed), from where to run the cmd,
  - **'process'**: used for checking/stopping the manager to identify 
     the manager's process. If cmd properly identifies the 
     manager, then this key is not necessary,
  - **'shell'**: some managers require shell=True option for subprocess.Popen()
  - **'help'**: it will be used as a tooltip,

## Demo
  - **python -m manman config/apparatus*.py**<br>
Control of all apparatuses, defined in the ./config directory.
Each apparatus will be controlled in a separate tab.
  - **python -m manman -c config apparatus1_test.py apparatus3_TST.py**<br>
Control two apparatuses from the ./config directory
  - **python -m manman -i -c config**<br>
Interacively select apparatuses from the ./config directory<br>
![manman](docs/manman.png)

