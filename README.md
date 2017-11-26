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