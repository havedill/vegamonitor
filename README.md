VegaMonitor                                                                                                                                      
=================================================================================================================================
							
							
Using python 3.6
							
XMR-Stak Config Changes:
- Set output to file to a location of your choosing
- Set verbose mode to 4
- Set the h_print_time to a lower value, I use 10 seconds

What it does:
- Monitor logfiles 60s hashrate
- Monitor logfiles last modified time
- Kills old process if the above are past thresholds
- Resets Drivers (HBCC) by resetting them in device manager
- Sets OverClockNTools configurations based on your supplied arguments
- Starts a new session of XMR-Stak

I want to add some API stuff to hopefully let me check my rates on the pool as well if needed. But since i watch the modified time...this might not be needed


No need to donate, but if you'd like to:
42uEk7j5ieJAyRhCcUjXkrhsSLe7J8WwXN86ubZfA5ne7RUrEJL2XhoYFtY71UgJiVG1CEZXwKi545cMB42AAdxV3MVT74Z




DEPENDENCIES (Set everything to always run as admin):

XMR-Stak - I'm typically a CastXMR fan, but since it is unable to write to a logfile, i opted to switch over to XMR-Stak for this.

- Compiling xmr-stak guide i used (to change donation level edit donate-level.h prior)
	- I ran with CUDA disabled since i have no NVIDIA cards.
	https://docs.google.com/document/d/1JoplwVyVQDo4ru8prsOD_kbMxeRvaACBiww3sSj1klA/mobilebasic

Devcon.exe - I followed the guide by AmirHossein to get the executable for this
	https://superuser.com/questions/1002950/quick-method-to-install-devcon-exe

OverDriveNTool - Make your "Stable" profile. I keep these on my desktop, and have it named "Stable" (as seen in arguments"
	https://forums.guru3d.com/threads/overdriventool-tool-for-amd-gpus.416116/

