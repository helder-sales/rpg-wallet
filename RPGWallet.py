import sys
from decimal import Decimal
from typing import Union

from Wallet import Wallet


wallet_id: str = input("Please enter the wallet id: ")
wallet = Wallet(int(wallet_id))

if wallet.empty_wallet:
    coin_names: list[str] = []
    coin_quantity: int = int(
        input("Please enter the quantity of coins to create: ")
    )
    print("\nPlease enter the coin names in descending order of value.\n")
    suffix_list: list[str] = ["st", "nd", "rd"]

    for i in range(0, coin_quantity):
        coin_names.append(
            input(f"{i + 1}{suffix_list[i] if i < 3 else 'th'} coin: ")
        )

    print("")
    coin_exchange_value: list[int] = [0]

    for i in range(0, coin_quantity - 1):
        coin_exchange_value.append(
            int(
                input(
                    f"{coin_names[i]} equals to how many "
                    f"{coin_names[i + 1]}: "
                )
            )
        )

    print("")

    for i in range(0, coin_quantity):
        wallet.create_coins(coin_names[i])
        wallet.add_coin_exchange_values(coin_names[i], coin_exchange_value[i])

while True:
    choice: str = input(
        "Please type one option listed below\n\n"
        "-add (coin)\n"
        "-remove (coin)\n"
        "-show\n"
        "-save\n"
        "-exit\n\n"
        "Input choice: "
    )
    option: list[str] = choice.split(" ")

    if option[0] == "add" or option[0] == "remove":
        coin: str = option[1]
        quantity: Union[int, float] = input(
            "Please enter the quantity (dot separator): "
        )

        if "." in quantity:
            idx_of_dot = quantity.index(".")
            qty_trunc = quantity[0 : (idx_of_dot + 2) + 1]
            quantity = Decimal(qty_trunc)

        else:
            quantity = int(quantity)

        if option[0] == "add":
            wallet.add_coin(coin, quantity)

        elif option[0] == "remove":
            wallet.remove_coin(coin, quantity)

    elif option[0] == "show":
        print(
            "\n################################################################"
            f"\n{wallet}"
            "################################################################\n"
        )

    elif option[0] == "save":
        wallet.save_wallet_contents()

    elif option[0] == "exit":
        sys.exit(0)

    else:
        print("\nPlease enter a valid choice!\n")
