import os, glob, platform

if platform.system() == "Windows":
    path = "..\\interfaceLogs\\"
else:
    path = "../interfaceLogs/"
    
for p in glob.glob(f"{path}*.csv"):
    if os.path.isfile(p):
        os.remove(p)

with open(f"{path}nowId.txt", "w") as f:
    f.write("0")
