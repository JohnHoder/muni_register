# MUNI Registrator

## How to use

You need to have the following python libraries installed on your system to use the scripts.

    sudo pip install bs4 requests lxml
    
Set up your IS login credentials and other required variables in `config.py`

    vi config.py
    
Make the required changes according to your needs to:

    registersubjects.txt, seminars.txt, exams.txt or generic.txt
    
Then you can run the standalone scripts as follows:

    python2 muni_registersubjects_threaded.py
    python2 muni_seminars_threaded.py
    python2 muni_exams_threaded.py
    python2 muni_generic_threaded.py


## Note
As of now the scripts are made in compliance with `python2` interpreter, the support of which has been dropped on January 1st, 2020.
It is advisable to rewrite the code for `python3` if you plan on using the code properly.
