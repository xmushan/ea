import os


folder_path = r'C:\Users\Administrator\Desktop\pythonEa'

# 创建文件夹（如果不存在）
os.makedirs(folder_path, exist_ok=True)

# 指定文件的完整路径和文件名
file_path = os.path.join(folder_path, 'log.txt')


def saveLog(text=''):
    # 打开文件并写入文本
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(text + '\n')
