# udacityFSWD_p2
udacity full stack web dev project 2

This code is developed inside a vagrant virtual box VM.

run:
git clone http://github.com/udacity/fullstack-nanodegree-vm fullstack
cd fullstack/vagrant
vagrant up
vagrant ssh 

To obtain the same starting dev environment. 
By default the unmodified starting code of this project will live in the /vagrant/tournament directory of your VM.

Use the following commands to set up the db:
```
> pqsl

> \i tournament.sql

> \q
```

The run tournament_test.py to show unit tests, and one example of a tournament
```
> python tournament_test.py
```






