import psutil
import time
from gpiozero import CPUTemperature

def my_background_task():
    while 1:
        cpu_temp = CPUTemperature().temperature
        cpu_temp = round(cpu_temp, 2)
        cpu = str(psutil.cpu_percent()) + '%'

        # Calculate memory information
        memory = psutil.virtual_memory()
        # Convert Bytes to MB (Bytes -> KB -> MB)
        available = round(memory.available/1024.0/1024.0,1)
        total = round(memory.total/1024.0/1024.0,1)
        mem_info = str(available) + 'MB free / ' + str(total) + 'MB total ( ' + str(memory.percent) + '% )'

        # Calculate disk information
        disk = psutil.disk_usage('/')
        # Convert Bytes to GB (Bytes -> KB -> MB -> GB)
        free = round(disk.free/1024.0/1024.0/1024.0,1)
        total = round(disk.total/1024.0/1024.0/1024.0,1)
        disk_info = str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )'
        # sio.emit("CPU-Info3–> ", cpu)
        # sio.emit("Memory-Info3–>", mem_info)
        # sio.emit("Disk-Info3–>", disk_info)
        # sio.emit('monitordata', [cpu,mem_info,disk_info,cpu_temp])
        print("CPU Info–> ", cpu)
        print("Memory Info–>", mem_info)
        print("Disk Info–>", disk_info)
        print("Temperature Info–>", cpu_temp)
        print("")
        time.sleep(5)