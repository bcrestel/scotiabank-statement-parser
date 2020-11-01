# Scotiabank Statement Parser
Simple parser for electronic credit cart statements by Scotiabank. 
The input file must be a text file where each statement spreads over 2 lines: the first line is the title of the period,
and the second line contains all activities, on a single line, separated by spaces. 


## Usage

You can run the code in this repo in a few different ways.
* ``make run INPUT=<input file path>``: this command will run the main function
* ``make shell``: this will create a shell inside a Docker container, 
from where you can run any code you like
* ``make notebook``: this will start a jupyter notebook server

In all cases, these commands will build the required Docker image if 
you don't already have it. 

