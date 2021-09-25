import shutil

import pytest

from Wallet import Wallet


class TestWallet:
    @pytest.fixture
    def wallet_object(self) -> None:
        self.wallet = Wallet()

        yield

        if not self.wallet.wallet_queue_file.empty():
            self.wallet.wallet_queue_file.get()

        del self.wallet.wallet_queue_file
        shutil.rmtree("./wallet_0")

    @pytest.fixture
    def coin_types(
        self,
        wallet_object: pytest.fixture,
    ) -> None:
        self.wallet.create_coins("gold", "silver", "bronze")

    @pytest.fixture
    def coin_types_and_exchange_values(
        self,
        coin_types: pytest.fixture,
    ) -> None:
        self.wallet.add_coin_exchange_values("gold", 0)
        self.wallet.add_coin_exchange_values("silver", 100)
        self.wallet.add_coin_exchange_values("bronze", 100)

    def test_if_wallet_returns_empty_wallet(self):
        wallet = Wallet()

        assert wallet.empty_wallet is True, "Wallet isn't empty"

        del wallet.wallet_queue_file
        shutil.rmtree("./wallet_0")

    def test_if_creates_coins(
        self,
        wallet_object: pytest.fixture,
    ):
        self.wallet.create_coins("gold", "silver", "bronze")

        assert self.wallet.get_coin("gold") == 0, "Failed to create a gold coin"
        assert (
            self.wallet.get_coin("silver") == 0
        ), "Failed to create a silver coin"
        assert (
            self.wallet.get_coin("bronze") == 0
        ), "Failed to create a bronze coin"

    def test_if_adds_coin_exchange_values(
        self,
        coin_types: pytest.fixture,
    ):
        expected_gold_coins = 0
        expected_silver_coins = 100
        expected_bronze_coins = 100

        self.wallet.add_coin_exchange_values("gold", 0)
        self.wallet.add_coin_exchange_values("silver", 100)
        self.wallet.add_coin_exchange_values("bronze", 100)

        assert (
            self.wallet.get_coin_exchange_value("gold") == expected_gold_coins
        ), "Gold coin exchange value doesn't match"
        assert (
            self.wallet.get_coin_exchange_value("silver")
            == expected_silver_coins
        ), "Silver coin exchange value doesn't match"
        assert (
            self.wallet.get_coin_exchange_value("bronze")
            == expected_bronze_coins
        ), "Bronze coin exchange value doesn't match"

    def test_if_adds_coins_correctly(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        expected_gold_coins = 10
        expected_silver_coins = 51
        expected_bronze_coins = 50

        self.wallet.add_coin("gold", 0)
        self.wallet.add_coin("silver", 1050)
        self.wallet.add_coin("bronze", 150)

        assert (
            self.wallet.get_coin("gold") == expected_gold_coins
        ), "Gold coin value doesn't match"
        assert (
            self.wallet.get_coin("silver") == expected_silver_coins
        ), "Silver coin value doesn't match"
        assert (
            self.wallet.get_coin("bronze") == expected_bronze_coins
        ), "Bronze coin value doesn't match"

    def test_if_adds_coins_up_to_two_decimal_places_and_ignores_beyond_that(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        expected_gold_coins = 1
        expected_silver_coins = 50
        expected_bronze_coins = 22

        self.wallet.add_coin("gold", 1.5)
        self.wallet.add_coin("silver", 0.222)
        self.wallet.add_coin(
            "bronze", 0.99
        )  # lowest coin should not add decimal values

        assert (
            self.wallet.get_coin("gold") == expected_gold_coins
        ), "Gold coin value doesn't match"
        assert (
            self.wallet.get_coin("silver") == expected_silver_coins
        ), "Silver coin value doesn't match"
        assert (
            self.wallet.get_coin("bronze") == expected_bronze_coins
        ), "Bronze coin value doesn't match"

    def test_if_removes_coin_correctly(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        expected_gold_coins = 100
        expected_silver_coins = 0
        expected_bronze_coins = 0

        self.wallet.add_coin("gold", 100)
        self.wallet.add_coin("silver", 100)
        self.wallet.add_coin("bronze", 100)
        self.wallet.remove_coin("gold", 1)
        self.wallet.remove_coin("silver", 1)
        self.wallet.remove_coin("bronze", 0)

        assert (
            self.wallet.get_coin("gold") == expected_gold_coins
        ), "Gold coin value doesn't match"
        assert (
            self.wallet.get_coin("silver") == expected_silver_coins
        ), "Silver coin value doesn't match"
        assert (
            self.wallet.get_coin("bronze") == expected_bronze_coins
        ), "Bronze coin value doesn't match"

    def test_if_removes_coin_up_to_two_decimal_places_and_ignores_beyond_that(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        expected_gold_coins = 1
        expected_silver_coins = 49
        expected_bronze_coins = 88

        self.wallet.add_coin("gold", 3)
        self.wallet.add_coin("silver", 0)
        self.wallet.add_coin("bronze", 0)
        self.wallet.remove_coin("gold", 1.5)
        self.wallet.remove_coin("silver", 0.111)
        self.wallet.remove_coin(
            "bronze", 1.99
        )  # lowest coin should not remove decimal values

        assert (
            self.wallet.get_coin("gold") == expected_gold_coins
        ), "Gold coin value doesn't match"
        assert (
            self.wallet.get_coin("silver") == expected_silver_coins
        ), "Silver coin value doesn't match"
        assert (
            self.wallet.get_coin("bronze") == expected_bronze_coins
        ), "Bronze coin value doesn't match"

    def test_if_removes_coin_and_raises_exception_correctly_when_balance_is_negative(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        expected_exception_message = "Insufficient coins"

        self.wallet.add_coin("gold", 110)

        with pytest.raises(ValueError) as exc_info:
            self.wallet.remove_coin("gold", 111)

        assert (
            str(exc_info.value) == expected_exception_message
        ), "Wrong exception message"

        with pytest.raises(ValueError) as exc_info:
            self.wallet.remove_coin("gold", 110.01)

        assert (
            str(exc_info.value) == expected_exception_message
        ), "Wrong exception message"

    def test_if_prints_wallet_contents_successfully(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        expected_returned_str_from_object = (
            "gold: 100\n" "silver: 10\n" "bronze: 1\n"
        )

        self.wallet.add_coin("gold", 100)
        self.wallet.add_coin("silver", 10)
        self.wallet.add_coin("bronze", 1)
        returned_str_from_object = str(self.wallet)

        assert (
            returned_str_from_object == expected_returned_str_from_object
        ), "Wallet is not generating a valid string output"

    def test_if_saves_wallet_contents_successfully(
        self,
        coin_types_and_exchange_values: pytest.fixture,
    ):
        self.wallet.save_wallet_contents()

        assert (
            not self.wallet.wallet_queue_file.empty()
        ), "Failed to save to queue"

        self.wallet.wallet_queue_file.get()

    def test_if_retrieves_wallet_contents_from_another_instance_with_same_id_successfully(
        self,
    ):
        wallet_instance_1 = Wallet(1337)
        wallet_instance_1.create_coins("gold", "silver", "bronze")
        wallet_instance_1.add_coin_exchange_values("gold", 0)
        wallet_instance_1.add_coin_exchange_values("silver", 100)
        wallet_instance_1.add_coin_exchange_values("bronze", 100)
        wallet_instance_1.add_coin("gold", 100)
        wallet_instance_1.add_coin("silver", 10)
        wallet_instance_1.add_coin("bronze", 1)
        wallet_instance_1.save_wallet_contents()
        wallet_instance_1_gold_coins = wallet_instance_1.get_coin("gold")
        wallet_instance_1_silver_coins = wallet_instance_1.get_coin("silver")
        wallet_instance_1_bronze_coins = wallet_instance_1.get_coin("bronze")

        del wallet_instance_1.wallet_queue_file
        del wallet_instance_1

        wallet_instance_2 = Wallet(1337)
        wallet_instance_2_gold_coins = wallet_instance_2.get_coin("gold")
        wallet_instance_2_silver_coins = wallet_instance_2.get_coin("silver")
        wallet_instance_2_bronze_coins = wallet_instance_2.get_coin("bronze")

        assert (
            wallet_instance_1_gold_coins == wallet_instance_2_gold_coins
        ), "Gold coin value doesn't match"
        assert (
            wallet_instance_1_silver_coins == wallet_instance_2_silver_coins
        ), "Silver coin value doesn't match"
        assert (
            wallet_instance_1_bronze_coins == wallet_instance_2_bronze_coins
        ), "Bronze coin value doesn't match"

        del wallet_instance_2.wallet_queue_file
        shutil.rmtree("./wallet_1337")

    def test_if_two_wallets_with_different_id_have_different_coin_quantity_saved(
        self,
    ):
        wallet_instance_1 = Wallet(9998)
        wallet_instance_1.create_coins("gold", "silver", "bronze")
        wallet_instance_1.add_coin_exchange_values("gold", 0)
        wallet_instance_1.add_coin_exchange_values("silver", 100)
        wallet_instance_1.add_coin_exchange_values("bronze", 100)
        wallet_instance_1.add_coin("gold", 100)
        wallet_instance_1.add_coin("silver", 10)
        wallet_instance_1.add_coin("bronze", 1)
        wallet_instance_1.save_wallet_contents()

        wallet_instance_2 = Wallet(9999)
        wallet_instance_2.create_coins("gold", "silver", "bronze")
        wallet_instance_2.add_coin_exchange_values("gold", 0)
        wallet_instance_2.add_coin_exchange_values("silver", 100)
        wallet_instance_2.add_coin_exchange_values("bronze", 100)
        wallet_instance_2.add_coin("gold", 50)
        wallet_instance_2.add_coin("silver", 5)
        wallet_instance_2.add_coin("bronze", 0)
        wallet_instance_2.save_wallet_contents()

        assert wallet_instance_1.get_coin("gold") != wallet_instance_2.get_coin(
            "gold"
        ), "Gold coin value is the same"
        assert wallet_instance_1.get_coin(
            "silver"
        ) != wallet_instance_2.get_coin(
            "silver"
        ), "Silver coin value is the same"
        assert wallet_instance_1.get_coin(
            "bronze"
        ) != wallet_instance_2.get_coin(
            "bronze"
        ), "Bronze coin value is the same"

        del wallet_instance_1.wallet_queue_file
        del wallet_instance_2.wallet_queue_file
        shutil.rmtree("./wallet_9998")
        shutil.rmtree("./wallet_9999")

    def test_if_raises_exception_correctly_when_a_wallet_have_more_than_one_queue_item_saved(
        self,
    ):
        expected_exception_message = (
            "For some reason, the queue had more than 1 item"
        )

        wallet = Wallet()
        wallet.create_coins("gold")
        wallet.add_coin_exchange_values("gold", 100)
        wallet.save_wallet_contents()
        wallet.wallet_queue_file.put("Content")

        with pytest.raises(Exception) as exc_info:
            wallet.save_wallet_contents()

        assert (
            str(exc_info.value) == expected_exception_message
        ), "Wrong exception message"

        del wallet.wallet_queue_file
        shutil.rmtree("./wallet_0")
