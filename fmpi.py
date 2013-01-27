#! /usr/bin/env python

import RPi.GPIO as GPIO
import time
import subprocess
import logging

class Button(object):
    def __init__(self, pin, callback):
        self.pin = pin
        self._callback = callback
        GPIO.setup(self.pin, GPIO.IN)
        self._last_state = False

    def is_press(self):
        cur_state = GPIO.input(self.pin)
        pressed = False
        if cur_state and cur_state != self._last_state:
            logging.info('Button [%s] pressed.', self.pin)
            pressed = True
        self._last_state = cur_state
        return pressed

    def run(self):
        if self.is_press():
            self._callback(self)

class DoubanPi(object):
    ONOFF = 22
    LIKE = 16
    SKIP = 18

    FMC_PATH = '/usr/local/bin/fmc'

    def __init__(self):
        self._buttons = [
            Button(self.ONOFF, self._on_off),
            Button(self.LIKE, self._like),
            Button(self.SKIP, self._skip)]

    def run(self):
        time.sleep(1)   # Sleep 1 seconds to wait buttons initialized.
        while True:
            for button in self._buttons:
                button.run()
            time.sleep(0.1)

    def _fmc(self, cmd):
        p = subprocess.Popen([self.FMC_PATH, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout

    def _on_off(self, button):
        fmc_state = self._fmc('info')
        if fmc_state.find('FMD Stopped') != -1:
            logging.info('Start FM')
        else:
            logging.info('Stop FM')
        self._fmc('toggle')

    def _like(self, button):
        logging.info('Like')
        print self._fmc('rate')

    def _skip(self, button):
        logging.info('Skip')
        print self._fmc('skip')


def main():
    GPIO.setmode(GPIO.BOARD)

    try:
        dbpi = DoubanPi()
        dbpi.run()
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

