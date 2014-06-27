class StepperComm:
	def __init__(self):
		from serial import Serial
		self.ser = Serial('/dev/tty.usbmodem1421', 9600, timeout=30)
		while True:
			L = self.ser.readline()
			if L.strip() == 'A':
				self._do('A\n')
				break
		self.ser.readline()

	def _do(self, char):
		self.ser.write(char + '\n')
		while True:
			x = self.ser.readline()
			if x.startswith(char):
				return

	def down(self):
		self._do('j')
		print 'down'

	def up(self):
		self._do('k')
		print 'up'

	def Down(self):
		self._do('J')
		print 'Down'

	def Up(self):
		self._do('K')
		print 'Up'

	def wayDown(self):
		self._do('U')
		print 'wayDown'

	def wayUp(self):
		self._do('I')
		print 'wayUp'


if __name__ == '__main__':
	import time
	scom = StepperComm()
	scom.up()
	time.sleep(0.1)
	scom.down()
	scom.Up()
	scom.Down()
	#scom.wayUp()
	#scom.wayDown()