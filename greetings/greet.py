import time
t=time.strftime('%H:%M:%S')
hour=int(time.strftime("%H"))
hour=int(input("enter the hour: "))
print(hour)
if(hour>=0 and hour<12):
  print("Good morning sir")
elif(hour>12 and hour<17):
  print("Good afternoon sir")
else: 
  print("Good night sir")