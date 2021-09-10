from decimal import Decimal
from typing import Union

from persistqueue import Queue


class Wallet:
    def __init__(self, wallet_id: int = 0) -> None:
        self.wallet_queue_file: Queue = Queue(
            f"./wallet_{wallet_id}",
            chunksize=1,
            autosave=True,
        )
        self.empty_wallet: bool = None
        self.__coin: list[list[Union[str, int]]] = self.__get_wallet_contents()

        if self.__coin == [[]]:
            self.empty_wallet = True

            del self.__coin[0]

        else:
            self.empty_wallet = False

    def __str__(self) -> str:
        wallet_contents: str = ""

        for item in self.__coin:
            wallet_contents += f"{item[0]}: {item[2]}\n"

        return wallet_contents

    def create_coins(self, *args: str) -> None:
        for item in args:
            self.__coin.append([item, 0, 0])

    def add_coin_exchange_values(self, coin: str, value: int) -> None:
        for idx, item in enumerate(self.__coin):
            if coin == item[0]:
                self.__coin[idx][1] = value // 1

    def add_coin(self, coin: str, quantity: Union[int, float]) -> None:
        if quantity == 0:
            return

        if type(quantity) == int or int((quantity % 1) * 100) == 0:
            for idx, item in enumerate(self.__coin):
                if coin == item[0]:
                    self.__coin[idx][2] += quantity // 1
                    self.__rearrange_coins_to_fit_exchange()

                    return

        integer_value: int
        decimal_value: int
        integer_value, decimal_value = Wallet.__separate_decimal_value(quantity)

        for idx, item in enumerate(self.__coin):
            if coin == item[0]:
                coin_idx_to_add_integer_part: int = idx
                coin_idx_to_add_decimal_part: int = idx + 1

        self.__coin[coin_idx_to_add_integer_part][2] += integer_value

        if coin_idx_to_add_decimal_part < len(self.__coin):
            decimal_value = (
                decimal_value * self.__coin[coin_idx_to_add_decimal_part][1]
            ) // 100

            self.__coin[coin_idx_to_add_decimal_part][2] += decimal_value

        self.__rearrange_coins_to_fit_exchange()

    def remove_coin(self, coin: str, quantity: Union[int, float]) -> None:
        if quantity == 0:
            return

        if type(quantity) == int or int((quantity % 1) * 100) == 0:
            quantity_converted: int = self.__rearrange_coins_to_lowest(
                coin, quantity
            )
            self.__rearrange_coins_to_lowest()
            last_coin_idx = len(self.__coin) - 1
            balance: int = self.__coin[last_coin_idx][2] - quantity_converted

            if balance < 0:
                self.__rearrange_coins_to_fit_exchange()

                raise ValueError("Insufficient coins")

            self.__coin[last_coin_idx][2] = balance
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
        balance: int = self.__coin[last_coin_idx][2] - (
            quantity_converted_integer + quantity_converted_decimal
        )

        if balance < 0:
            self.__rearrange_coins_to_fit_exchange()

            raise ValueError("Insufficient coins")

        self.__coin[last_coin_idx][2] = balance
        self.__rearrange_coins_to_fit_exchange()

    def get_coin(self, coin: str) -> int:
        for item in self.__coin:
            if coin == item[0]:
                return item[2]

        return 0

    def get_coin_exchange_value(self, coin: str) -> int:
        for idx, item in enumerate(self.__coin):
            if coin == item[0]:
                return self.__coin[idx][1]

    def __rearrange_coins_to_fit_exchange(self) -> None:
        coin_promoted: int = 0

        for idx in range(len(self.__coin) - 1, -1, -1):
            if idx > 0:
                if coin_promoted > 0:
                    self.__coin[idx][2] += coin_promoted
                    coin_promoted = 0

                coin_quantity: int = self.__coin[idx][2]
                coin_value: int = self.__coin[idx][1]

                while coin_quantity >= coin_value and coin_quantity > 0:
                    self.__coin[idx][2] -= coin_value
                    coin_promoted += 1
                    coin_quantity = self.__coin[idx][2]

        self.__coin[idx][2] += coin_promoted

    def __rearrange_coins_to_lowest(
        self,
        coin: str = None,
        quantity: int = 0,
    ) -> Union[None, int]:
        if coin is None:
            for idx in range(0, len(self.__coin) - 1):
                current_coin_quantity: int = self.__coin[idx][2]
                next_coin_exchange_value: int = self.__coin[idx + 1][1]
                self.__coin[idx + 1][2] = (
                    current_coin_quantity * next_coin_exchange_value
                    + self.__coin[idx + 1][2]
                )
                self.__coin[idx][2] = 0

        else:
            quantity_converted: int = 0

            for idx, item in enumerate(self.__coin):
                if coin == item[0]:
                    for idx in range(idx, len(self.__coin) - 1):
                        next_coin_exchange_value = self.__coin[idx + 1][1]
                        quantity = quantity * next_coin_exchange_value

            quantity_converted = quantity

            return quantity_converted

    def __get_exchange_value_relative_from_lowest_coin(
        self, coin_base: str
    ) -> int:
        for idx, item in enumerate(self.__coin):
            if coin_base == item[0]:
                exchange_in_terms_of_lowest_coin: int = 1

                for i in range(idx + 1, len(self.__coin)):
                    exchange_in_terms_of_lowest_coin *= self.__coin[i][1]

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
        self, contents: list[list[Union[str, int]]]
    ) -> None:
        self.wallet_queue_file.put(contents)

    def __retrieve_wallet_contents_from_queue(
        self,
    ) -> list[list[Union[str, int]]]:
        wallet_content: list[list[Union[str, int]]] = [[]]

        if not self.wallet_queue_file.empty():
            wallet_content = self.wallet_queue_file.get()

            if not self.wallet_queue_file.empty():
                raise Exception(
                    "For some reason, the queue had more than 1 item"
                )

        return wallet_content

    def __get_wallet_contents(self) -> list[list[Union[str, int]]]:
        wallet_content: list[
            list[Union[str, int]]
        ] = self.__retrieve_wallet_contents_from_queue()
        self.__place_wallet_contents_in_queue(wallet_content)

        return wallet_content

    def save_wallet_contents(self) -> None:
        self.__retrieve_wallet_contents_from_queue()
        self.__place_wallet_contents_in_queue(self.__coin)
