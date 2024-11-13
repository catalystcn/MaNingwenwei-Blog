import psutil
import os

def read_usb():
    # 获取磁盘信息
    disks = psutil.disk_partitions()
    # 过滤出U盘信息
    usb_disks = [disk for disk in disks if "removable" in disk.opts]
    # 存储每个U盘中的.ttv文件
    usb_list = []

    for usb_disk in usb_disks:
        path = usb_disk.device
        # 遍历U盘目录，查找.ttv文件
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".ttv"):
                    usb_list.append(os.path.join(root, file))
                    print(f"找到文件: {os.path.join(root, file)}")

    return usb_list

print(read_usb())