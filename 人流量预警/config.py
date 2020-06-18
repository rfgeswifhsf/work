from pprint import pprint

list_a = [i for i in range(0,100)]

distance=5
step =3
pivote = 0

for i in range(0, len(list_a) - distance + 1):
    pprint(list_a[pivote:pivote+distance])
    pivote+=step
    if pivote>len(list_a)-distance+1:
        break
