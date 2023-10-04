import os, glob, platform

filePath = os.path.dirname(__file__)
if platform.system() == "Windows":
    path = f"{filePath}\\..\\interfaceLogs\\"
else:
    path = f"{filePath}/../interfaceLogs/"
    
for p in glob.glob(f"{path}*.csv"):
    if os.path.isfile(p):
        os.remove(p)

with open(f"{path}nowId.txt", "w") as f:
    f.write("0")
