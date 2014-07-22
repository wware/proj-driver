import logging

logger = logging.getLogger('Arduino stepper control')
ch = logging.StreamHandler()
ch.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - " +
                      "%(levelname)s - %(message)s")
)
logger.addHandler(ch)

SIGN = 1
MOCK = True


class Stepper:

    def __init__(self):
        from serial import Serial
        self.ser = Serial('/dev/tty.usbmodem1421', 9600, timeout=30)

    def steps(self, num):
        assert type(num) is type(3)
        self.ser.write(repr(num) + '\n')
        self.ser.readline()   # wait for "OK"


class MockStepper(Stepper):
    def __init__(self):
        logger.setLevel(logging.DEBUG)

    def steps(self, num):
        logger.debug(num)

if MOCK:
    Stepper = MockStepper


def main():
    import time
    stepper = Stepper()
    stepper.steps(50)
    time.sleep(0.5)
    stepper.steps(-50)
    time.sleep(0.5)
    stepper.steps(500)
    time.sleep(0.5)
    stepper.steps(-500)


if __name__ == '__main__':
    main()
