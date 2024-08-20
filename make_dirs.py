import os


def print_python_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                print(os.path.join(root, file))


print_python_files('G:\\PycharmProject\\Timefold-training\\optylogisdep')
