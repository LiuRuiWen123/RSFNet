from pathlib import Path

input_dir = Path(r"D:\course\LLE\dataset\LOLdataset\our485\low")
output_file = Path(r"D:\course\LLE\dataset\LOLdataset\our485\trainList.txt")

# 写入文件
with output_file.open('w') as f:
    for file in input_dir.glob('*'):
        if file.is_file():
            f.write(f"{file.name}\n")

print(f"文件已生成: {output_file}")