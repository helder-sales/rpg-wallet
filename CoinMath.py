from copy import deepcopy
from decimal import Decimal

from indexed import IndexedOrderedDict


class CoinMath:
    def __init__(self) -> None:
        pass

    def add_coin_int(
        self,
        wallet_coins_obj: IndexedOrderedDict[dict[int]],
        coin_to_add: str,
        quantity: int,
    ) -> IndexedOrderedDict[dict[int]]:
        wallet_coins: IndexedOrderedDict[dict[int]] = deepcopy(wallet_coins_obj)
        wallet_coins[coin_to_add]["quantity"] += quantity // 1
        wallet_coins = self.__distribute_coins_according_to_exchange(
            wallet_coins
        )
        return wallet_coins

    def add_coin_float(
        self,
        wallet_coins_obj: IndexedOrderedDict[dict[int]],
        coin: str,
        quantity: float,
    ) -> IndexedOrderedDict[dict[int]]:
        wallet_coins: IndexedOrderedDict[dict[int]] = deepcopy(wallet_coins_obj)
        integer_value: int
        decimal_value: int
        integer_value, decimal_value = CoinMath.__separate_decimal_value(
            quantity
        )
        wallet_coins[coin]["quantity"] += integer_value
        next_coin_idx_to_add_decimal_part: int = (
            self.__get_coin_idx(wallet_coins, coin) + 1
        )

        if next_coin_idx_to_add_decimal_part < len(wallet_coins):
            coin_to_add_decimal_part: str = self.__get_coin_name(
                wallet_coins, next_coin_idx_to_add_decimal_part
            )
            decimal_value = (
                decimal_value
                * wallet_coins[coin_to_add_decimal_part]["exchange_value"]
            ) // 100
            wallet_coins[coin_to_add_decimal_part]["quantity"] += decimal_value

        return wallet_coins

    def remove_coin_int(
        self,
        wallet_coins_obj: IndexedOrderedDict[dict[int]],
        coin: str,
        quantity: int,
    ) -> IndexedOrderedDict[dict[int]]:
        wallet_coins: IndexedOrderedDict[dict[int]] = deepcopy(wallet_coins_obj)
        quantity_converted: int = self.__convert_coins_to_lowest(
            wallet_coins, coin, quantity
        )
        wallet_coins = self.__convert_coins_to_lowest(wallet_coins, "all")
        last_coin_idx: int = len(wallet_coins) - 1
        last_coin: str = self.__get_coin_name(wallet_coins, last_coin_idx)
        balance: int = wallet_coins[last_coin]["quantity"] - quantity_converted

        if balance < 0:
            missed_coins: str = self.__get_missing_coins(
                wallet_coins, balance, last_coin
            )
            wallet_coins = self.__distribute_coins_according_to_exchange(
                wallet_coins
            )
            raise ValueError(f"Insufficient coins! Missing:\n\n{missed_coins}")

        wallet_coins[last_coin]["quantity"] = balance
        wallet_coins = self.__distribute_coins_according_to_exchange(
            wallet_coins
        )
        return wallet_coins

    def remove_coin_float(
        self,
        wallet_coins_obj: IndexedOrderedDict[dict[int]],
        coin: str,
        quantity: float,
    ) -> IndexedOrderedDict[dict[int]]:
        wallet_coins: IndexedOrderedDict[dict[int]] = deepcopy(wallet_coins_obj)
        integer_value: int
        decimal_value: int
        integer_value, decimal_value = CoinMath.__separate_decimal_value(
            quantity
        )
        quantity_converted_integer: int = self.__convert_coins_to_lowest(
            wallet_coins, coin, integer_value
        )
        quantity_converted_decimal: int = (
            self.__get_exchange_value_in_terms_of_lowest_coin(
                wallet_coins, coin
            )
            * decimal_value
        ) // 100
        wallet_coins = self.__convert_coins_to_lowest(wallet_coins, "all")
        last_coin_idx: int = len(wallet_coins) - 1
        last_coin: str = self.__get_coin_name(wallet_coins, last_coin_idx)
        balance: int = wallet_coins[last_coin]["quantity"] - (
            quantity_converted_integer + quantity_converted_decimal
        )

        if balance < 0:
            missed_coins: str = self.__get_missing_coins(
                wallet_coins, balance, last_coin
            )
            wallet_coins = self.__distribute_coins_according_to_exchange(
                wallet_coins
            )
            raise ValueError(f"Insufficient coins! Missing:\n\n{missed_coins}")

        wallet_coins[last_coin]["quantity"] = balance
        wallet_coins = self.__distribute_coins_according_to_exchange(
            wallet_coins
        )
        return wallet_coins

    def __distribute_coins_according_to_exchange(
        self,
        coins: IndexedOrderedDict[dict[int]],
    ) -> IndexedOrderedDict[dict[int]]:
        converted_coins: IndexedOrderedDict[dict[int]] = deepcopy(coins)
        coin_promoted: int = 0

        for idx in range(len(converted_coins) - 1, -1, -1):
            current_coin: str = self.__get_coin_name(converted_coins, idx)

            if idx > 0:
                if coin_promoted > 0:
                    converted_coins[current_coin]["quantity"] += coin_promoted
                    coin_promoted = 0

                coin_quantity: int = converted_coins[current_coin]["quantity"]
                coin_exchange_value: int = converted_coins[current_coin][
                    "exchange_value"
                ]

                while (
                    coin_quantity >= coin_exchange_value and coin_quantity > 0
                ):
                    converted_coins[current_coin][
                        "quantity"
                    ] -= coin_exchange_value
                    coin_promoted += 1
                    coin_quantity = converted_coins[current_coin]["quantity"]

        converted_coins[current_coin]["quantity"] += coin_promoted
        return converted_coins

    def __convert_coins_to_lowest(
        self,
        wallet_coins_obj: IndexedOrderedDict[dict[int]],
        coin: str,
        quantity: int = 0,
    ) -> IndexedOrderedDict[dict[int]] | int:
        wallet_coins: IndexedOrderedDict[dict[int]] = deepcopy(wallet_coins_obj)

        if coin == "all":
            for idx in range(0, len(wallet_coins) - 1):
                current_coin: str = self.__get_coin_name(wallet_coins, idx)
                current_coin_quantity: int = wallet_coins[current_coin][
                    "quantity"
                ]
                next_coin: str = self.__get_coin_name(wallet_coins, idx + 1)
                next_coin_exchange_value: int = wallet_coins[next_coin][
                    "exchange_value"
                ]
                wallet_coins[next_coin]["quantity"] = (
                    current_coin_quantity * next_coin_exchange_value
                    + wallet_coins[next_coin]["quantity"]
                )
                wallet_coins[current_coin]["quantity"] = 0

            return wallet_coins

        else:
            idx_of_current_coin: int = self.__get_coin_idx(wallet_coins, coin)

            for idx in range(idx_of_current_coin, len(wallet_coins) - 1):
                next_coin: str = self.__get_coin_name(wallet_coins, idx + 1)
                next_coin_exchange_value: int = wallet_coins[next_coin][
                    "exchange_value"
                ]
                quantity = quantity * next_coin_exchange_value

            return quantity

    def __get_coin_name(
        self, coins: IndexedOrderedDict[dict[int]], idx_to_get_name: int
    ) -> str:
        return coins.keys()[idx_to_get_name]

    def __get_coin_idx(
        self, coins: IndexedOrderedDict[dict[int]], coin_to_get_idx: str
    ) -> int:
        return coins.keys().index(coin_to_get_idx)

    def __get_missing_coins(
        self,
        missed_coins: IndexedOrderedDict[dict[int]],
        balance: int,
        last_coin: str,
    ) -> str:
        from Wallet import Wallet

        missed_coins[last_coin]["quantity"] = abs(balance)
        missed_coins = self.__distribute_coins_according_to_exchange(
            missed_coins
        )
        return Wallet.format_coins_into_a_string(missed_coins)

    def __get_exchange_value_in_terms_of_lowest_coin(
        self,
        wallet_coins_obj: IndexedOrderedDict[dict[int]],
        coin_base: str,
    ) -> int:
        wallet_coins: IndexedOrderedDict[dict[int]] = deepcopy(wallet_coins_obj)
        exchange_in_terms_of_lowest_coin: int = 1
        idx_of_next_coin_from_coin_base: int = (
            self.__get_coin_idx(wallet_coins, coin_base) + 1
        )

        for idx in range(idx_of_next_coin_from_coin_base, len(wallet_coins)):
            current_coin: str = self.__get_coin_name(wallet_coins, idx)
            exchange_in_terms_of_lowest_coin *= wallet_coins[current_coin][
                "exchange_value"
            ]

        return exchange_in_terms_of_lowest_coin

    @staticmethod
    def __separate_decimal_value(quantity: float) -> tuple[int, int]:
        qty_as_str: str = f"{float(quantity)}"
        idx_of_dot: int = qty_as_str.index(".")
        qty_as_str_trunc: str = qty_as_str[0 : (idx_of_dot + 2) + 1]
        decimal_value: int = int((Decimal(qty_as_str_trunc) % 1) * 100)
        integer_value: int = int(quantity // 1)
        return integer_value, decimal_value
