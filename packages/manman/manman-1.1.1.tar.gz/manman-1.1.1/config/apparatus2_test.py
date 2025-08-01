'''Definition of the second test apparatus.
'''
import os
homeDir = os.environ['HOME']

__version__ = 'v0.0.1 2025-05-21'#

# abbreviations:
help,cmd,process,cd = ['help','cmd','process','cd']

#``````````````````Properties, used by manman`````````````````````````````````
title = 'Test1 applications'

startup = {
'xclock':{help:'Analog xclock', 
  cmd:'xclock -analog'
  },
'top':{help:'Process viewer in separate xterm',
  cmd:'xterm top',
  },
'sleep10':{help:'Sleep for 10 seconds', 
  cmd:'sleep 10', process:'sleep 10'
  },
}
