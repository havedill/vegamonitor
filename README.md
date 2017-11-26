                                                                                                                                     
8b           d8                                    88b           d88                            88                                   
`8b         d8'                                    888b         d888                            ""    ,d                             
 `8b       d8'                                     88`8b       d8'88                                  88                             
  `8b     d8'  ,adPPYba,   ,adPPYb,d8  ,adPPYYba,  88 `8b     d8' 88   ,adPPYba,   8b,dPPYba,   88  MM88MMM  ,adPPYba,   8b,dPPYba,  
   `8b   d8'  a8P_____88  a8"    `Y88  ""     `Y8  88  `8b   d8'  88  a8"     "8a  88P'   `"8a  88    88    a8"     "8a  88P'   "Y8  
    `8b d8'   8PP"""""""  8b       88  ,adPPPPP88  88   `8b d8'   88  8b       d8  88       88  88    88    8b       d8  88          
     `888'    "8b,   ,aa  "8a,   ,d88  88,    ,88  88    `888'    88  "8a,   ,a8"  88       88  88    88,   "8a,   ,a8"  88          
      `8'      `"Ybbd8"'   `"YbbdP"Y8  `"8bbdP"Y8  88     `8'     88   `"YbbdP"'   88       88  88    "Y888  `"YbbdP"'   88          
                           aa,    ,88                                                                                                
                            "Y8bbdP"                                                                                             
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