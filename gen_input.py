import os
"""newpath = "./input/1/"
if not os.path.exists(newpath):
    os.makedirs(newpath)
file = open(os.path.join(newpath, "config"), "w")
file.write("hello")
file.close
"""
from shutil import copyfile
import numpy as np

count = 1
for length in np.arange(45, 61, 15):
    for changesong in np.arange(0.8, 1.1, 0.1):
        for minbeatcount in np.arange(9, 12, 1):
            newpath = "./input/" + str(count) + "/"
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            file = open(os.path.join(newpath, "config"), "w")
            file.write("input=song1.wav\n"
                       "input=song2.wav\n"
                       "length="+str(length)+"\n"
                        "timbre="+str(1.0)+"\n"
                        "chroma="+str(1.0)+"\n"
                        "energy="+str(1.0)+"\n"
                        "minbeats="+str(8)+"\n"
                        "changesong="+str(changesong)+"\n"
                        "minbeatcount="+str(minbeatcount))
            file.close()
            copyfile("./2/song1.wav", os.path.join(newpath, "song1.wav"))
            copyfile("./2/song2.wav", os.path.join(newpath, "song2.wav"))
            count += 1
print count

