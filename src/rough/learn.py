print("Hello!")
xyz = 10
xyz = xyz*35
print(xyz)
# ==, >, <, >=, <=

if xyz > 25:
    print("Its a big value....")
elif xyz == 10:
    print("Its exactly ten...")
else:
    print("Its a small value...")

i = 0
variable_x = True
while variable_x:
    print(f"while loop: {i}")
    i = i+1
    variable_x = i < 10

for a in range(10):
    print(f"For loop: {a}")


def write():
    print("printing from method....")


def print_another():
    print("second method...")
