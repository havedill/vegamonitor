VegaMonitor (XMRSTAK | CASTXMR)                                                                                                                           
=================================================================================================================================
Using python 3.6

Install python 3.6
Install the python module requirments (pip install -r requirements.txt)

CONFIG LOCATION
===============
- Make a copy of exampleconfig.yaml, and name it config.yaml.	Update this with your settings. Put which miner you use, file paths, etc

XMRSTAK
=======
- Monitor logfiles 60s hashrate
- Monitor logfiles last modified time
- Kills old process if the above are past thresholds
- Resets Drivers (HBCC) by resetting them in device manager
- Sets OverClockNTools configurations based on your supplied arguments
- Starts a new session of XMR-Stak

XMR-Stak Config Changes:
- Set output to file to a location of your choosing
- Set verbose mode to 4
- Set the h_print_time to a lower value, I use 10 seconds

CASTXMR
=======
- Web request castxmr for hashrates
- Confirm web requests return code 200. If not, restart things - we assume cast is locked up or countdown
- Kills old process if below hash thresholds, or return has troubles
- Resets Drivers (HBCC) by resetting them in device manager
- Sets OverClockNTools configurations based on your supplied arguments
- Starts a new session of Cast with your supplied arguments

Cast Required Arugments:
- Requires -R flag to allow access to the json data

No need to donate, but if you'd like to:
42uEk7j5ieJAyRhCcUjXkrhsSLe7J8WwXN86ubZfA5ne7RUrEJL2XhoYFtY71UgJiVG1CEZXwKi545cMB42AAdxV3MVT74Z

GUIDES + REQUIRED TOOLS:
=========================

- Compiling xmr-stak guide i used (to change donation level edit donate-level.h prior)
	- I ran with CUDA disabled since i have no NVIDIA cards.
	https://docs.google.com/document/d/1JoplwVyVQDo4ru8prsOD_kbMxeRvaACBiww3sSj1klA/mobilebasic


DEPENDENCIES (Set everything to always run as admin):

Devcon.exe - I followed the guide by AmirHossein to get the executable for this
	https://superuser.com/questions/1002950/quick-method-to-install-devcon-exe

OverDriveNTool - Make your "Stable" profile. I keep these on my desktop, and have it named "Stable" (as seen in arguments"
	https://forums.guru3d.com/threads/overdriventool-tool-for-amd-gpus.416116/
