# MUNI Registrator

## Components description & config

Script `muni_subjects_threaded.py` registers the subjects of your choice. This choice has to be made in the file `subjects.txt`. Whole registration URL has to be provided for each subject separately on a new line. Make sure there are no empty lines in between the URLs nor at the end of the file. Example:

    https://is.muni.cz/auth/student/zapis?fakulta=0000;obdobi=0000;studium=000000;rreg=0000000;design=m
    https://is.muni.cz/auth/student/zapis?fakulta=0000;obdobi=0000;studium=000000;rreg=0000000;design=m
    https://is.muni.cz/auth/student/zapis?fakulta=0000;obdobi=0000;studium=000000;rreg=0000000;design=m
    
Script `muni_seminars_threaded.py` registers the seminar groups according to your wish. Your choice has to be made in the file `seminars.txt`. Notation of this file's structure is `CodeOfTheSubject [SPACE] NumberOfTheDesiredSeminarGroup`, such as following:

    MP110Z 10
    MP111Z 11
    MP112Z 15

Script `muni_exams_threaded.py` registers the exam termins for you. Similarly to registering subjects, your choice is to be made in the file `exams.txt` in the format containing the whole registration URL. Each exam URL has to be on a separate new line. 

    https://is.muni.cz/auth/student/prihl_na_zkousky?fakulta=0000;obdobi=0000;studium=000000;predmet=0000000;zkt=000000;prihlasit=1;stopwindow=1

Finally, script `muni_generic_threaded.py` can be used to execute any generic action in IS the purpose of which is not covered in the aforementioned scripts. Make your changes to `generic.txt`, again in URL format, one URL per line.

## How to use

You need to have the following python libraries installed on your system to use the scripts.

    sudo pip install bs4 requests lxml
    
If you are using python2, pip support for 2.7 has probably been removed from your system and you will have to get it by some workaround like this:

    sudo dnf -y install https://github.com/UnitedRPMs/unitedrpms/releases/download/17/unitedrpms-$(rpm -E %fedora)-17.fc$(rpm -E %fedora).noarch.rpm                       
    sudo dnf install python2-pip
    
Or preferably, of course, use python3 and alter the scripts appropriately.

Set up your IS login credentials and other required variables in `config.py`.

    vi config.py

In `config.py` there is, inter alia, setting for exact time all the scripts should run at. There are four variables for that (`time_hours`, `time_minutes`, `time_seconds`, `time_microseconds`) the names of which make their meaning self-explanatory.
If you do not know where to get the required information to set all the variables, refer to the URL of any of your registrations (such as the URLs indicated above).

Make the required changes according to your needs to `subjects.txt`, `seminars.txt`, `exams.txt` or `generic.txt`. Refer above to the syntax required by each of the mentioned files.

Then you can run the standalone scripts as follows:

    python2 muni_subjects_threaded.py
    python2 muni_seminars_threaded.py
    python2 muni_exams_threaded.py
    python2 muni_generic_threaded.py


If you have all the necessary libraries installed and all the config files are configured as they should be, the result shall be as follows:

![screenshot](https://github.com/JohnHoder/muni_register/blob/master/img/screenshot.png?raw=true)

## Note #1
All scripts assume that IS is in the Czech language (not in the English). Should that not be the case, it will result in misbehaviour.

## Note #2
As of now the scripts are made in compliance with `python2` interpreter, the support of which has been dropped on January 1st, 2020.
It is advisable to rewrite the code for `python3` if you plan on using the scripts properly on a long-term basis.

## Note #3
Files in `tests` folder are present for testing reference in development for historical reasons.

## Note #4
If you encounter an error message `('WEIRD -> ', ConnectionError(ProtocolError('Connection aborted.', BadStatusLine('No status line received - the server has closed the connection',)),))`, you do not need to worry about anything, the script will continue as it is supposed to. This behaviour seems to be present on a random basis and its effects on your registration success have been suppressed in the code. Of course, if you know what the reason behind this message could be, don't hesitate to make a pull request.

## Disclaimer
This code is rather dirty. There are also many places where the code might crash unexpectedly. Feel free to make any improvements or other modifications and suggest them via a pull request. Also feel free to open an issue if you find it convenient.
I am not responsible for anything you do with these scripts. All you do is at your own peril.
