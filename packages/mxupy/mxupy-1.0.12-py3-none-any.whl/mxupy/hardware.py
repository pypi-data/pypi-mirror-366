import platform
from datetime import datetime
import mxupy as mu

def getAllLocalIPs():
    import socket
    try:
        # 获取所有网络接口
        interfaces = socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET)
        # 提取IP地址
        ips = [info[4][0] for info in interfaces]
        return ips
    except Exception as e:
        print(f"无法获取本机IP: {e}")
        return None


def getDiskInfo():
    """
    获取磁盘信息。

    返回:
        str: 包含磁盘信息的字符串。
    """
    import psutil

    infostr = ['', '']
    mu.sprt(infostr)
    # Disk Information
    print("=" * 40, "Disk Details", "=" * 40)
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {mu.formatBytes(partition_usage.total)}")
        print(f"  Used: {mu.formatBytes(partition_usage.used)}")
        print(f"  Free: {mu.formatBytes(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {mu.formatBytes(disk_io.read_bytes)}")
    print(f"Total write: {mu.formatBytes(disk_io.write_bytes)}")

    mu.eprt(infostr)

    return infostr[1]


def getCPUInfo():
    """
    获取 CPU 信息。

    返回:
        str: 包含 CPU 信息的字符串。
    """

    import psutil
    infostr = ['', '']
    mu.sprt(infostr)
    print("=" * 40, "CPU Details", "=" * 40)

    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    print("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%", end=', ')
    print(f"\nTotal CPU Usage: {psutil.cpu_percent()}%")
    mu.eprt(infostr)

    return infostr[1]


def getGPUInfo(idx=0):
    """
    获取 GPU 信息。

    参数:
        idx (int, 可选): GPU 索引，默认为 0。

    返回:
        str: 包含 GPU 信息的字符串。
    """
    import GPUtil

    from tabulate import tabulate
    infostr = ['', '']
    mu.sprt(infostr)
    print("=" * 40, "GPU Details", "=" * 40)

    gpus = GPUtil.getGPUs()
    list_gpus = []
    for i, gpu in enumerate(gpus):
        if i != idx:
            continue
        # get the GPU id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load*100}%"
        # get free memory in MB format
        gpu_free_memory = f"{mu.formatBytes(gpu.memoryFree*1024*1024)}"
        # get used memory
        gpu_used_memory = f"{mu.formatBytes(gpu.memoryUsed*1024*1024)}"
        # get total memory
        gpu_total_memory = f"{mu.formatBytes(gpu.memoryTotal*1024*1024)}"
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        gpu_uuid = gpu.uuid
        list_gpus.append((gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory, gpu_total_memory, gpu_temperature, gpu_uuid))

    print(tabulate(list_gpus, headers=("id", "name", "load", "free memory", "used memory", "total memory", "temperature", "uuid")))

    mu.eprt(infostr)

    return infostr[1]


def getSystemInfo():
    """
    获取系统信息。

    返回:
        str: 包含系统信息的字符串。
    """

    import psutil
    uname = platform.uname()

    boot_time_timestamp = psutil.boot_time()

    infostr = "=" * 40 + "System Details" + "=" * 40 + '\n'

    infostr += f"System: {uname.system}\nNode Name: {uname.node}\nRelease: {uname.release}\nVersion: {uname.version}\nMachine: {uname.machine}\nProcessor: {uname.processor}\n\nBoot Time: {datetime.fromtimestamp(boot_time_timestamp).strftime('%Y/%m/%d %H:%M:%S')}"

    return infostr


def getMemoryInfo():
    """
    获取内存信息。

    返回:
        str: 包含内存信息的字符串。
    """

    import psutil
    infostr = ['', '']
    mu.sprt(infostr)
    print("=" * 40, "Memory Details", "=" * 40)

    virtual_memory = psutil.virtual_memory()
    swap_memory = psutil.swap_memory()

    print(
        "Virtual Memory:\n", {
            "Total": f"{mu.formatBytes(virtual_memory.total)}",
            "Available": f"{mu.formatBytes(virtual_memory.available)}",
            "Used": f"{mu.formatBytes(virtual_memory.used)}",
            "Usage Percentage": f"{virtual_memory.percent}%"
        })
    print("Swap Memory\n", {
        "Total": f"{mu.formatBytes(swap_memory.total)}",
        "Used": f"{mu.formatBytes(swap_memory.used)}",
        "Free": f"{mu.formatBytes(swap_memory.free)}",
        "Usage Percentage": f"{swap_memory.percent}%"
    })

    mu.eprt(infostr)

    return infostr[1]


if __name__ == '__main__':

    # print(getSystemInfo())
    # print(getGPUInfo())
    # print(getMemoryInfo())
    # print(getCPUInfo())
    # print(getDiskInfo())
    print(getAllLocalIPs())
