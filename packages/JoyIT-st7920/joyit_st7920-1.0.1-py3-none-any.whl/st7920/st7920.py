import spidev
import time
from PIL import Image
from gpiozero import OutputDevice

class ST7920:
  def __init__(self, spi_bus=0, spi_device=0, reset_pin = 22):
    """
    Initilize ST7920 with SPI
    """
    self.spi = spidev.SpiDev()
    self.spi.open(spi_bus, spi_device)
    self.spi.max_speed_hz = 500000
    self.spi.mode = 0

    self.reset_pin = OutputDevice(reset_pin)    
    self.init_display()
    self.clear()

  def _send_command(self, cmd):
    """
    Send command to display
    """
    data = [0xF8, cmd & 0xF0, (cmd << 4) & 0xF0]
    self.spi.writebytes(data)
    time.sleep(0.001)

  def _send_data(self, data):
    """
    Send data to display
    """
    packet = [0xFA, data & 0xF0, (data << 4) & 0xF0]
    self.spi.writebytes(packet)
    time.sleep(0.001)

  def init_display(self):
    """
    Establish communication with display 
    """
    time.sleep(0.05)
    self._send_command(0x30)
    self._send_command(0x30)
    self._send_command(0x0C)
    self._send_command(0x01)
    time.sleep(0.01)
        
  def clear_graphics(self):
    """
    Clear image on display
    """
    self._send_command(0x30)  
    self._send_command(0x34)
    self._send_command(0x36)
    for y in range(64):
      if y < 32:
        self._send_command(0x80 | y)
        self._send_command(0x80)
      else:
        self._send_command(0x80 | (y - 32))
        self._send_command(0x88)
      for _ in range(16):
        self._send_data(0x00)
        
  def clear(self):
    """
    Clear display
    """
    self._send_command(0x01)
    time.sleep(0.01)
    self.reset_pin.off()
    time.sleep(0.1)
    self.reset_pin.on()
    time.sleep(0.1)
    self.clear_graphics()
    self._send_command(0x30)
    self._send_command(0x0C)

  def close(self):
    """
    Close connection
    """
    self.spi.close()

  def write_text(self, text):
    """
    Write text on display
    """
    for char in text:
      self._send_data(ord(char))

  def home(self):
    """
    Set cursor to (0,0)
    """
    self._send_command(0x02)
    time.sleep(0.01)

  def display_on(self, cursor=False, blink=False):
    """
    Activate display with visible cursor (False/True) and or blinking cursor (False/True)
    """
    cmd = 0x0C
    if cursor:
      cmd |= 0x02
    if blink:
      cmd |= 0x01
    self._send_command(cmd)

  def display_off(self):
    """
    Turn display off
    """
    self._send_command(0x08)

  def set_cursor(self, row: int, col: int):
    """
    Set cursor to position (row, col)
    """
    if row == 0:
      address = 0x80 + col
    elif row == 1:
      address = 0x90 + col
    else:
      raise ValueError("Zeile muss 0 oder 1 sein.")
    self._send_command(address)

  def write_at(self, row: int, col: int, text: str):
    """
    Method to write text at position (row, col)
    """
    self.set_cursor(row, col)
    self.write_text(text)

  def shift_display_left(self):
    """
    Shift display to the left
    """
    self._send_command(0x18)

  def shift_display_right(self):
    """
    Shift display to the right
    """
    self._send_command(0x1C)

  def entry_mode(self, increment=True, shift=False):
    """
    Setup entry mode
    """
    cmd = 0x04
    if increment:
      cmd |= 0x02
    if shift:
      cmd |= 0x01
    self._send_command(cmd)

  def draw_image(self, image: Image.Image):
    """
    draw image on display
    """
    self._send_command(0x30)
    self._send_command(0x34)
    self._send_command(0x36)
    if image.size != (128, 64):
      raise ValueError("Image has to be 128x64 Pixel")
    image = image.convert("1")    
    pixels = image.load()
    for y in range(64):
      if y < 32:
        self._send_command(0x80 | y)
        self._send_command(0x80)
      else:
        self._send_command(0x80 | (y - 32))
        self._send_command(0x88)
      for x in range(0, 128, 8):
        byte = 0
        for bit in range(8):
          if pixels[x + bit, y] == 0:
            byte |= (1 << (7 - bit))
        self._send_data(byte)
            