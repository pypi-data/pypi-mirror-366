# 1. 创建新文件
moudle.new.file('1.txt')  # 当前目录创建1.txt
moudle.new.file('2.txt', 'C:/Users/Username')  # 指定目录创建2.txt

# 2. 创建新目录
moudle.new.dir('new_folder')  # 当前目录创建new_folder
moudle.new.dir('new_folder', 'C:/Users/Username')  # 指定目录创建new_folder

# 3. 打开文件
file = moudle.open('test.txt', 'file1')  # 打开test.txt并赋值给file1
with moudle.open('test.txt', 'file2') as f:  # 使用with语句
    pass

# 4. 写入内容
moudle.write('Hello', 1, 'file1')  # 写入到file1的第一行末尾

# 5. 保存更改
moudle.save('file1')

# 6. 关闭文件
moudle.close('file1')

# 7. 打开文件夹对话框
folder = moudle.look.dir('folder1')
with moudle.look.dir('folder2') as f:  # 使用with语句
    pass

# 8. 打开文件对话框
file = moudle.look.file('file3')
with moudle.look.file('file4') as f:  # 使用with语句
    pass