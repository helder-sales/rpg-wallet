from decimal import Decimal
from typing import Union

from persistqueue import Queue
from indexed import IndexedOrderedDict


class Wallet:
    def __init__(self, wallet_id: int = 0) -> None:
        self.wallet_queue_file: Queue = Queue(
            f"./wallet_{wallet_id}",
            chunksize=1,
            autosave=True,
        )
        self.empty_wallet: bool = None
        self.__coin: IndexedOrderedDict[
            dict[int]
        ] = self.__get_wallet_contents()

        if self.__coin == IndexedOrderedDict(dict()):
            self.empty_wallet = True

        else:
            self.empty_wallet = False

    def __str__(self) -> str:
        wallet_contents: str = ""

        for coin in self.__coin:
            wallet_contents += f"{coin}: {self.__coin[coin]['quantity']}\n"

        return wallet_contents

    def create_coins(self, *coins: str) -> None:
        for coin in coins:
            self.__coin.update({coin: dict(exchange_value=0, quantity=0)})

    def add_coin_exchange_values(self, coin: str, value: int) -> None:
        self.__coin[coin]["exchange_value"] = value // 1

    def add_coin(self, coin: str, quantity: Union[int, float]) -> None:
        if quantity == 0:
            return

        if type(quantity) == int or int((quantity % 1) * 100) == 0:
            self.__coin[coin]["quantity"] += quantity // 1
            self.__rearrange_coins_to_fit_exchange()

            return

        integer_value: int
        decimal_value: int
        integer_value, decimal_value = Wallet.__separate_decimal_value(quantity)
        self.__coin[coin]["quantity"] += integer_value
        next_coin_idx_to_add_decimal_part: int = (
            self.__coin.keys().index(coin) + 1
        )

        if next_coin_idx_to_add_decimal_part < len(self.__coin):
            coin_to_add_decimal_part: str = self.__coin.keys()[
                next_coin_idx_to_add_decimal_part
            ]
            decimal_value = (
                decimal_value
                * self.__coin[coin_to_add_decimal_part]["exchange_value"]
            ) // 100

            self.__coin[coin_to_add_decimal_part]["quantity"] += decimal_value

        self.__rearrange_coins_to_fit_exchange()

    def remove_coin(self, coin: str, quantity: Union[int, float]) -> None:
        if quantity == 0:
            return

        if type(quantity) == int or int((quantity % 1) * 100) == 0:
            quantity_converted: int = self.__rearrange_coins_to_lowest(
                coin, quantity
            )
            self.__rearrange_coins_to_lowest()
            last_coin_idx: int = len(self.__coin) - 1
            last_coin: str = self.__coin.keys()[last_coin_idx]
            balance: int = (
                self.__coin[last_coin]["quantity"] - quantity_converted
            )

            if balance < 0:
                self.__rearrange_coins_to_fit_exchange()

                raise ValueError("Insufficient coins")

            self.__coin[last_coin]["quantity"] = balance
            self.__rearrange_coins_to_fit_exchange()

            return

        integer_value: int
        decimal_value: int
        integer_value, decimal_value = Wallet.__separate_decimal_value(quantity)
        quantity_converted_integer: int = self.__rearrange_coins_to_lowest(
            coin, integer_value
        )
        quantity_converted_decimal: int = (
            self.__get_exchange_value_relative_from_lowest_coin(coin)
            * decimal_value
        ) // 100
        self.__rearrange_coins_to_lowest()
        last_coin_idx: int = len(self.__coin) - 1
        last_coin: str = self.__coin.keys()[last_coin_idx]
        balance: int = self.__coin[last_coin]["quantity"] - (
            quantity_converted_integer + quantity_converted_decimal
        )

        if balance < 0:
            self.__rearrange_coins_to_fit_exchange()

            raise ValueError("Insufficient coins")

        self.__coin[last_coin]["quantity"] = balance
        self.__rearrange_coins_to_fit_exchange()

    def get_coin(self, coin: str) -> int:
        return self.__coin[coin]["quantity"]

    def get_coin_exchange_value(self, coin: str) -> int:
        return self.__coin[coin]["exchange_value"]

    def __rearrange_coins_to_fit_exchange(self) -> None:
        coin_promoted: int = 0

        for idx in range(len(self.__coin) - 1, -1, -1):
            current_coin: str = self.__coin.keys()[idx]

            if idx > 0:
                if coin_promoted > 0:
                    self.__coin[current_coin]["quantity"] += coin_promoted
                    coin_promoted = 0

                coin_quantity: int = self.__coin[current_coin]["quantity"]
                coin__exchange_value: int = self.__coin[current_coin][
                    "exchange_value"
                ]

                while (
                    coin_quantity >= coin__exchange_value and coin_quantity > 0
                ):
                    self.__coin[current_coin][
                        "quantity"
                    ] -= coin__exchange_value
                    coin_promoted += 1
                    coin_quantity = self.__coin[current_coin]["quantity"]

        self.__coin[current_coin]["quantity"] += coin_promoted

    def __rearrange_coins_to_lowest(
        self,
        coin: str = None,
        quantity: int = 0,
    ) -> Union[None, int]:
        if coin is None:
            for idx in range(0, len(self.__coin) - 1):
                current_coin: str = self.__coin.keys()[idx]
                current_coin_quantity: int = self.__coin[current_coin][
                    "quantity"
                ]
                next_coin: str = self.__coin.keys()[idx + 1]
                next_coin_exchange_value: int = self.__coin[next_coin][
                    "exchange_value"
                ]
                self.__coin[next_coin]["quantity"] = (
                    current_coin_quantity * next_coin_exchange_value
                    + self.__coin[next_coin]["quantity"]
                )
                self.__coin[current_coin]["quantity"] = 0

        else:
            quantity_converted: int = 0
            idx_of_current_coin: int = self.__coin.keys().index(coin)

            for idx in range(idx_of_current_coin, len(self.__coin) - 1):
                next_coin: str = self.__coin.keys()[idx + 1]
                next_coin_exchange_value: int = self.__coin[next_coin][
                    "exchange_value"
                ]
                quantity = quantity * next_coin_exchange_value

            quantity_converted = quantity

            return quantity_converted

    def __get_exchange_value_relative_from_lowest_coin(
        self, coin_base: str
    ) -> int:
        exchange_in_terms_of_lowest_coin: int = 1
        idx_of_next_coin_from_coin_base: int = (
            self.__coin.keys().index(coin_base) + 1
        )

        for i in range(idx_of_next_coin_from_coin_base, len(self.__coin)):
            current_coin: str = self.__coin.keys()[i]
            exchange_in_terms_of_lowest_coin *= self.__coin[current_coin][
                "exchange_value"
            ]

        return exchange_in_terms_of_lowest_coin

    @staticmethod
    def __separate_decimal_value(quantity: float) -> tuple[int, int]:
        qty_as_str = f"{float(quantity)}"
        idx_of_dot = qty_as_str.index(".")
        qty_as_str_trunc = qty_as_str[0 : (idx_of_dot + 2) + 1]
        decimal_value: int = int((Decimal(qty_as_str_trunc) % 1) * 100)
        integer_value: int = int(quantity // 1)

        return integer_value, decimal_value

    def __place_wallet_contents_in_queue(
        self, contents: IndexedOrderedDict[dict[int]]
    ) -> None:
        self.wallet_queue_file.put(contents)

    def __retrieve_wallet_contents_from_queue(
        self,
    ) -> IndexedOrderedDict[dict[int]]:
        wallet_content: IndexedOrderedDict[dict[int]] = IndexedOrderedDict(
            dict()
        )

        if not self.wallet_queue_file.empty():
            wallet_content = self.wallet_queue_file.get()

            if not self.wallet_queue_file.empty():
                raise Exception(
                    "For some reason, the queue had more than 1 item"
                )

        return wallet_content

    def __get_wallet_contents(self) -> IndexedOrderedDict[dict[int]]:
        wallet_content: IndexedOrderedDict[
            dict[int]
        ] = self.__retrieve_wallet_contents_from_queue()
        self.__place_wallet_contents_in_queue(wallet_content)

        return wallet_content

    def save_wallet_contents(self) -> None:
        self.__retrieve_wallet_contents_from_queue()
        self.__place_wallet_contents_in_queue(self.__coin)
