# UniSocial4
A cloud-powered high-perfomance system for data collection from social networks

## Installation
### Requirements
* [Python3](https://www.python.org/)
* Packages:
  * `pip install click`
  * `pip install -r CollectorRole/requirements.txt`
  * `pip install -r SaveResultRole/requirements.txt`

## Usage
Despite the fact that this system was designed to be runned in a cloud enviromenent, it provides a script for a simple data collection with saving results to a file.

### Simple data collection
Run the following command in the folder with the system: `python collect_data.py --help` to see a short help.

#### Input data
All commands accept as input a text file with parameters separated by the new line:

>1  
>2  
>3  

If the method requires several parameters, use `_` as the delimiter:

>1_1  
>3_2  
>3_4  

#### Methods
As the current moment the following methods are supported:
 * profiles
 * likes
 * walls
 * search


