import sys

n = int(input())
arr = [list(map(int, sys.stdin.readline().split())) for _ in range(n)]
ans = [0,0]

def coount(arr,x,y,size):
    paper = arr[y][x]
    for i in range(y,y+size):
        for j in range(x,x+size):
            if paper != arr[i][j]:
                coount(arr,x,y,size//2)
                coount(arr,x+size//2,y,size//2)
                coount(arr,x,y+size//2,size//2)
                coount(arr,x+size//2,y+size//2,size//2)
                return 0
            
    if paper == 0:
        ans[0] += 1
        return 0
    else:
        ans[1] += 1
        return 0

coount(arr,0,0,n)
print(ans[0])
print(ans[1])