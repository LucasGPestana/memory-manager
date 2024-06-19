import sys

from memory_manager import MemoryManager

if __name__ == "__main__":

  if sys.platform.startswith("win"):

    m = MemoryManager()

    print(m.listProcesses("memory", 10))
    # print(m.searchProcesses("name", "chrome.exe"))
    # m.finishProcess("pid", 11456)
    print(f"Memória usada: {m.getTotalMemoryUsed()}")