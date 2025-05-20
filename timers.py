class Timer:
  def __init__(self):
    self.time = 0
    self.tally = 0
    self.reverse = False

  def timer(self, duration=int):
    self.time += 1
    if self.time >= duration:
      self.time = 0
      return True
    else: return False

  def wait(self, duration=int, lag=2):
    self.time += 1
    if self.time >= duration:
      if self.time >= duration * lag:
        self.time = 0
      return True
    else: return False
  
  def count(self, duration=int, stop=int, start=0):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    if self.tally < stop:
      self.time += 1
      if self.time >= duration:
        self.time = 0
        self.tally += 1
    return self.tally
  
  def subcount(self, duration=int, stop=int, start=int):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    if self.tally > stop:
      self.time += 1
      if self.time >= duration:
        self.time = 0
        self.tally -= 1
    return self.tally

  def keep_count(self, duration=int, stop=int, start=0):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    if self.tally < stop:
      self.time += 1
      if self.time >= duration:
        self.time = 0
        self.tally += 1
        if self.tally >= stop:
          self.tally = start
    return self.tally
  
  def oscillate(self, duration=int, stop=int, start=0):
    if self.time == 0 and self.tally == 0: self.tally = start
    self.time += 1
    if self.time >= duration:
      self.time = 0
      if self.reverse: self.tally -= 1
      else: self.tally += 1
      if self.tally >= stop: self.reverse = True
      if self.tally < start: self.reverse = False
    return self.tally
  
  def reset(self):
    self.time = 0
    self.tally = 0