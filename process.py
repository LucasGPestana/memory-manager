class Process:

  def __init__(self, name: str, pid: int, session_name: str, session_number: int, memory_used: int):

    self.__name = name
    self.__pid = pid
    self.__session_name = session_name
    self.__session_number = session_number
    self.__memory_used = memory_used

  @property
  def name(self):

    return self.__name
  
  @property
  def pid(self):
    
    return self.__pid
  
  @property
  def session_name(self):
    
    return self.__session_name
  
  @property
  def session_number(self):
    
    return self.__session_number
  
  @property
  def memory_used(self):
    
    return self.__memory_used
  
  def getAllData(self):

    return "\t\t\t".join(list(map(str, [self.__name, 
                      self.__pid, 
                      self.__session_name, 
                      self.__session_number, 
                      self.memory_used])))