import logging

logger = logging.getLogger('Arduino stepper control')

SIGN = 1
MOCK = True


class StepperComm:

    def __init__(self):
        from serial import Serial
        self.ser = Serial('/dev/tty.usbmodem1421', 9600, timeout=30)

    def steps(self, num):
        assert type(num) is type(3)
        self.ser.write(repr(num) + '\n')
        self.ser.readline()

    # 1/100th of an inch
    def down(self):
        self.steps(SIGN * 720)
        print 'down'

    def up(self):
        self.steps(SIGN * -720)
        print 'up'

    # 1/10th of an inch
    def Down(self):
        self.steps(SIGN * 7200)
        print 'Down'

    def Up(self):
        self.steps(SIGN * -7200)
        print 'Up'

    # 1 inch
    def wayDown(self):
        self.steps(SIGN * 72000)
        print 'wayDown'

    def wayUp(self):
        self.steps(SIGN * -72000)
        print 'wayUp'


class MockStepperComm(StepperComm):
    def __init__(self):
        ch = logging.StreamHandler()
        ch.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - " +
                              "%(levelname)s - %(message)s")
        )
        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)

    def steps(self, num):
        logger.debug(num)

if MOCK:
    StepperComm = MockStepperComm


def main():
    import time
    scom = StepperComm()
    scom.up()
    time.sleep(0.1)
    scom.down()
    time.sleep(0.1)
    scom.Up()
    time.sleep(0.1)
    scom.Down()


if __name__ == '__main__':
    main()
