Arduino code
==

The Arduino has the job of driving the stepper. It communicates over USB-serial with the
host machine. (The host machine also drives the projector.) I'm using a Macbook for the
host machine but there is no reason you couldn't use a Windows or Linux machine.

The serial protocol works like this. You type a letter (j, J, k, K, U, I) and in respponse
the motor moves the carriage up or down by some amount. The mnemonic is the vi commands:
Lower-case j and k respectively move the carriage down and up by 1/40 inch. Upper-case J
and K respectively move the carriage down and up by 1/4 inch. Upper-case U and I
respectively move the carriage down and up by 2.5 inches. Since the threaded rod is
20 threads per inch, the small step is a half-rotation of the threaded rod, or 90 steps
of the NEMA-23 stepper motor.

Any other characters typed will be echoed, but won't move the motor. These letters will
be echoed at the end of the carriage movement. While the carriage is in motion, any
characters typed should be ignored.
