# ode-example
A simple Django project to be used as a coding sample. There is a verbose 
description of the site on the landing page.

## FYI
Uses many default settings, and should all be pretty automatic with the a SQLite
db. For use with python 3.7. In order to use it, it will require users. Non 
admin users can be created via admin menu.


## Getting Started.
1) Clone the repo
2) Setup new python (3.7) environment, install python requirements from `requirements.txt`
3) `$python manage.py migrate`
4) `$python manage.py createsuperuser` and follow prompts to setup a user.
5) `$python manage.py runserver`

## Coding Style.
Generally I stay pretty close to PEP8, although sometimes I am loose with the 80
line character limit. I haven't done type hinting here, because personally I 
think it slows development down a little bit, and I was in a bit of a rush to 
get this out. For the purposes of sustainable code, I do encourage type hinting.

As for js, well... uh... I think it looks neat? I haven't researched style 
guides for js, but I do try to stay internally consistent.