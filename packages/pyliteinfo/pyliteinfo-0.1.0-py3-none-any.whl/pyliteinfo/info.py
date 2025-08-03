import platform
import psutil
import socket
import os

class SystemInfo:
    def get_os_info(self):
        return {
            "os": platform.system(),
            "version": platform.version(),
            "architecture": platform.machine()
        }

    def get_cpu_info(self):
        return {
            "cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "arch": platform.processor()
        }

    def get_memory_info(self):
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / 1e9, 2),
            "available_gb": round(mem.available / 1e9, 2)
        }

    def get_disk_info(self):
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / 1e9, 2),
            "used_gb": round(disk.used / 1e9, 2),
            "free_gb": round(disk.free / 1e9, 2)
        }

    def get_ip(self):
        return socket.gethostbyname(socket.gethostname())

    def get_all_drive_info(self):
        drive_info = []
        partitions = psutil.disk_partitions(all=False)
        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                drive_info.append({
                    "device": p.device,
                    "mountpoint": p.mountpoint,
                    "fstype": p.fstype,
                    "total_gb": round(usage.total / 1e9, 2),
                    "used_gb": round(usage.used / 1e9, 2),
                    "free_gb": round(usage.free / 1e9, 2),
                    "percent_used": usage.percent
                })
            except PermissionError:
                continue
        return drive_info

    def get_drive_wise_largest_files(self, top_n=5):
        drive_files = {}
        partitions = psutil.disk_partitions(all=False)
        for part in partitions:
            drive = part.mountpoint
            largest = []
            for root, dirs, files in os.walk(drive):
                for name in files:
                    try:
                        filepath = os.path.join(root, name)
                        size = os.path.getsize(filepath)
                        largest.append((filepath, size))
                    except (PermissionError, FileNotFoundError,OSError):
                        continue
            # Sort and trim to top_n
            largest.sort(key=lambda x: x[1], reverse=True)
            drive_files[drive] = [
                {"file": f, "size_mb": round(s / 1e6, 2)} for f, s in largest[:top_n]
            ]
        return drive_files
