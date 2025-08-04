import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

# Constant variables
LEVEL_1 = 11497
LEVEL_2 = 29315
LEVEL_3 = 83823
LEVEL_4 = 180294

TAX_1 = 0
TAX_2 = 0.11
TAX_3 = 0.30
TAX_4 = 0.41
TAX_5 = 0.45

# Computation function
def compute_tax(amount):
    if amount <= LEVEL_1:
        return amount*TAX_1
    elif amount > LEVEL_1 and amount <= LEVEL_2:
        return LEVEL_1*TAX_1 + (amount-LEVEL_1)*TAX_2
    elif amount > LEVEL_2 and amount <= LEVEL_3:
        return LEVEL_1*TAX_1 + (LEVEL_2-LEVEL_1)*TAX_2 + (amount-LEVEL_2)*TAX_3
    elif amount > LEVEL_3 and amount <= LEVEL_4:
        return LEVEL_1*TAX_1 + (LEVEL_2-LEVEL_1)*TAX_2 + (LEVEL_3-LEVEL_2)*TAX_3 + (amount-LEVEL_3)*TAX_4
    elif amount > LEVEL_4:
        return LEVEL_1*TAX_1 + (LEVEL_2-LEVEL_1)*TAX_2 + (LEVEL_3-LEVEL_2)*TAX_3 + (LEVEL_4-LEVEL_3)*TAX_4 + (amount-LEVEL_4)*TAX_5
    else:
        raise ValueError("Amount should be greater than 0")

def main():
    amount = float(input("Enter the amount of revenue: "))
    IR = round(compute_tax(amount))
    TGI = IR/amount
    print(f"--> IR:  {IR:n}€\n" + f"--> TGI: {TGI*100:.2f}%")
