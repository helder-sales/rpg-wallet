from indexed import IndexedOrderedDict
from persistqueue import Queue

from CoinMath import CoinMath


class Wallet:
    def __init__(self, wallet_id: int = 0) -> None:
        self.wallet_queue: Queue = Queue(
            f"./wallet_{wallet_id}",
            chunksize=1,
            autosave=True,
        )
        self.coin_math: CoinMath = CoinMath()
        self.empty_wallet: bool = True
        self.coins: IndexedOrderedDict[dict[int]] = self.get_wallet_contents()

        if self.coins == IndexedOrderedDict(dict()):
            self.empty_wallet = True

        else:
            self.empty_wallet = False

    def __str__(self) -> str:
        return Wallet.format_coins_into_a_string(self.coins)

    @staticmethod
    def format_coins_into_a_string(coins: IndexedOrderedDict[dict[int]]) -> str:
        coins_string: str = ""

        for coin in coins:
            coins_string += f"{coin}: {coins[coin]['quantity']}\n"

        return coins_string

    def create_coins(self, *coins: str) -> None:
        for coin in coins:
            self.coins.update({coin: {"exchange_value": 0, "quantity": 0}})

    def add_coin_exchange_values(self, coin: str, value: int) -> None:
        self.coins[coin]["exchange_value"] = value // 1

    def add_coin(self, coin_to_add: str, quantity: int | float) -> None:
        if quantity == 0:
            return

        if type(quantity) == int or int((quantity % 1) * 100) == 0:
            self.coins = self.coin_math.add_coin_int(
                self.coins, coin_to_add, quantity
            )
            return

        self.coins = self.coin_math.add_coin_float(
            self.coins, coin_to_add, quantity
        )

    def remove_coin(self, coin: str, quantity: int | float) -> None:
        if quantity == 0:
            return

        if type(quantity) == int or int((quantity % 1) * 100) == 0:
            self.coins = self.coin_math.remove_coin_int(
                self.coins, coin, quantity
            )
            return

        self.coins = self.coin_math.remove_coin_float(
            self.coins, coin, quantity
        )

    def get_coin(self, coin: str) -> int:
        return self.coins[coin]["quantity"]

    def get_coin_exchange_value(self, coin: str) -> int:
        return self.coins[coin]["exchange_value"]

    def __place_wallet_contents_in_queue(
        self,
        contents: IndexedOrderedDict[dict[int]],
    ) -> None:
        self.wallet_queue.put(contents)

    def __retrieve_wallet_contents_from_queue(
        self,
    ) -> IndexedOrderedDict[dict[int]]:
        wallet_content: IndexedOrderedDict[dict[int]] = IndexedOrderedDict(
            dict()
        )

        if not self.wallet_queue.empty():
            wallet_content = self.wallet_queue.get()

            if not self.wallet_queue.empty():
                raise Exception(
                    "For some reason, the queue had more than 1 item"
                )

        return wallet_content

    def get_wallet_contents(self) -> IndexedOrderedDict[dict[int]]:
        wallet_content: IndexedOrderedDict[
            dict[int]
        ] = self.__retrieve_wallet_contents_from_queue()
        self.__place_wallet_contents_in_queue(wallet_content)
        return wallet_content

    def save_wallet_contents(self) -> None:
        self.__retrieve_wallet_contents_from_queue()
        self.__place_wallet_contents_in_queue(self.coins)
