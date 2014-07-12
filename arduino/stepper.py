SIGN = 1


class StepperComm:

    def __init__(self):
        from serial import Serial
        self.ser = Serial('/dev/tty.usbmodem1421', 9600, timeout=30)
        #self._do(0)

    def _do(self, num):
        assert type(num) is type(3)
        self.ser.write(repr(num) + '\n')
        self.ser.readline()

    # 1/100th of an inch
    def down(self):
        self._do(SIGN * 720)
        print 'down'

    def up(self):
        self._do(SIGN * -720)
        print 'up'

    # 1/10th of an inch
    def Down(self):
        self._do(SIGN * 7200)
        print 'Down'

    def Up(self):
        self._do(SIGN * -7200)
        print 'Up'

    # 1 inch
    def wayDown(self):
        self._do(SIGN * 72000)
        print 'wayDown'

    def wayUp(self):
        self._do(SIGN * -72000)
        print 'wayUp'


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
