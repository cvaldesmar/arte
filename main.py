from VanGoghMuseum import VanGoghMuseum as VGM
from MuseoDelPrado import MuseoDelPrado as MDP

mdp = MDP(headlessMode=0)
mdp.museoDelPradoDataExport("MuseoDelPradoTodos.json")


# vgm = VGM(headlessMode=0)
# vgm.vanGoghMuseumDataExport("Todos.json")
# vgm.vanGoghMuseumExploration("Todos.json")


# import sys
# print(str(sys.getrecursionlimit()))
# sys.setrecursionlimit(5000)
# print(str(sys.getrecursionlimit()))
# import shutil
# shutil.rmtree('fullBackup')