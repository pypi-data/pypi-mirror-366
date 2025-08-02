from xarizmi.fundamentals.time_value_money import time_value_money

value = time_value_money(
    impatience_to_consume=0.05,
    inflation=0.1,
    risk=0.045,
)

print(f"Time value of money is {value}")
print(f"A $1000 one year later worth ${int(value * 1000 + 1000)} now")
