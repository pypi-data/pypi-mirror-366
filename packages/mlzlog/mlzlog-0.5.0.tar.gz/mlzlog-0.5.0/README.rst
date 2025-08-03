mlzlog
======

mlzlog is a collection of common logging functionality developed and used at
`MLZ <http://mlz-garching.de/>`_.


Usage
-----

Before you do any logging, initiate the mlz logging via::

    initLogging(rootname='mlz', rootlevel='info', logdir='/var/log')

That will set up a global root logger (accesible via ``mlzlog.log``) and attach
handlers for colored console output and logfiles (in a nice version).

To get a new logger just use **getChild** on another logger (e.g. mlzlog.log)::

    # ownDir creates a new subdirectory for the desired logger name
    mlzlog.log.getChild('mysublogger', ownDir=True)
