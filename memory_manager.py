import re
import subprocess
from typing import List

from process import Process

class MemoryManager:

  def __init__(self):

    completed_process = subprocess.run(args=("tasklist"), stdout=subprocess.PIPE)

    processes_info_str = completed_process.stdout.decode("latin-1")

    processes_info = processes_info_str.splitlines()

    # Removendo os elementos dos índices 0, 1, 2 e -1
    processes_info = processes_info[3:-1]

    self.processes = list(map(MemoryManager.processData, processes_info))
  
  @staticmethod
  def processData(process_info: str) -> Process:

    space_pattern = re.compile(r"[\s]{2,}")

    # Pega os dados em forma de lista
    process_data = space_pattern.split(process_info)

    # Dividindo os dados de identificação e nome da sessão em elementos diferentes da lista
    ident_and_name_session_data = process_data[1].split(" ")

    process_data[1] = int(ident_and_name_session_data[0])
    process_data.insert(2, ident_and_name_session_data[1])

    # Convertendo o número de sessão para inteiro
    process_data[3] = int(process_data[3])

    # Removendo o caractere K no dado de uso de memória, e convertendo para bytes
    process_data[4] = int(process_data[4].replace(" K", "").replace(".", "")) * 1024

    return Process(*process_data)
  
  @staticmethod
  def sortProcesses(process: Process, order_by: str="") -> str | int:

    match (order_by):

      case "name":

        return process.name
      
      case "pid":

        return process.pid
      
      case "memory":

        return process.memory_used

  def listProcesses(self, order_by: str="", quantity: int=-1) -> str:

    if quantity == -1:

      quantity = len(self.processes)

    match (order_by):

      case "name":

        reverse_value = False
      
      case "pid":

        reverse_value = True
      
      case "memory":

        reverse_value = True

    sorted_processes = sorted(self.processes, key=lambda x: MemoryManager.sortProcesses(x, order_by), reverse=reverse_value)[:quantity]

    return "\n".join([process.getAllData() for process in sorted_processes])
  
  def searchProcesses(self, by: str, value: str | int) -> str:

    choosed_processes: List[Process] = None

    match (by):

      case "name":

        name_pattern = re.compile(value, re.IGNORECASE)

        choosed_processes = [process for process in self.processes if name_pattern.search(process.name)]
      
      case "pid":

        choosed_processes = [process for process in self.processes if process.pid == value]
      
      case _:

        print("O meio de identificação do(s) processo(s) a ser(em) buscado(s) não é válido!")
        return
    
    return "\n".join([process.getAllData() for process in choosed_processes])
  
  def finishProcess(self, by: str, value: str | int, forcefully_end: bool=False) -> None:

    choosed_process: Process = None

    add_args: List[str] = ["/F"] if forcefully_end else [] # Argumentos adicionais

    try:

      match (by):
        
        case "pid":

          choosed_process = [process for process in self.processes if process.pid == value][0]
        
        case _:

          print("O meio de identificação do processo a ser finalizado não é válido!")
          return
        
    except IndexError:

      print("Não há nenhum processo com essa especificação!")
      return
    
    subprocess.run(args=["taskkill", "/PID", str(choosed_process.pid)] + add_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Instância temporária de MemoryManager cuja lista de processos já foi atualizada (com o processo já finalizado)
    # Serve para não remover o processo da lista de processos do objeto original antes de verificar se este já foi removido da lista de processos (tasklist.exe)
    temp_m = MemoryManager()

    if not choosed_process.pid in [process.pid for process in temp_m.processes]:

      self.processes.pop(self.processes.index(choosed_process)) # Remove o processo da lista

      print(f"\033[1;32m{choosed_process.name} (PID {choosed_process.pid}) foi finalizado!\033[m")
      return
    
    print(f"\033[1;31mO processo {choosed_process.name} (PID {choosed_process.pid}) não foi finalizado corretamente!\033[m")

    answer = input("Deseja finalizar forçadamente esse processo (S/N)? ").upper()

    match (answer):

      case 'S':

        self.finishProcess(by, value, True)
      
      case 'N':

        return
      
      case _:

        print("Opção inválida!")
  
  # Verifica quando de memória está sendo usada, sem contar o programa de listagem (tasklist.exe)
  def getTotalMemoryUsed(self) -> str:

    memory_used = sum(process.memory_used for process in self.processes if not process.name in ["tasklist.exe"])

    memory_capacity_info = subprocess.run(args=("wmic", "memorychip", "get", "capacity"), 
                                         stdout=subprocess.PIPE).stdout.decode("utf-8")
    
    memory_capacity = int(memory_capacity_info.splitlines()[2].strip())

    return f"{memory_used} bytes/{memory_capacity} bytes ({(memory_used/memory_capacity)*100}%)"