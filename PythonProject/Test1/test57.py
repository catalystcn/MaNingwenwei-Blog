def categorize_temp_dict(over_temp_orders, file_paths):
    # 初始化结果字典
    result = {
        "超温": {},
        "正常": {}
    }

    # 遍历文件路径字典，检查每个键名
    for key, path in file_paths.items():
        if key in over_temp_orders:
            result["超温"][key] = path
        else:
            result["正常"][key] = path

    return result

# 示例使用
over_temp_orders = ["设备1-订单1", "设备2-订单2", "设备3-订单3"]
file_paths = {
    "设备1-订单1": "path/to/file1",
    "设备2-订单2": "path/to/file2",
    "设备3-订单3": "path/to/file3"
}

# 调用函数
categorized_orders = categorize_temp_dict(over_temp_orders, file_paths)

# 输出结果
print(categorized_orders)
