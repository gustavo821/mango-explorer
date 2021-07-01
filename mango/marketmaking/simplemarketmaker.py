# # ⚠ Warning
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# [🥭 Mango Markets](https://mango.markets/) support is available at:
#   [Docs](https://docs.mango.markets/)
#   [Discord](https://discord.gg/67jySBhxrg)
#   [Twitter](https://twitter.com/mangomarkets)
#   [Github](https://github.com/blockworks-foundation)
#   [Email](mailto:hello@blockworks.foundation)


import logging
import mango
import time
import traceback
import typing

from datetime import timedelta
from decimal import Decimal


# # 🥭 SimpleMarketMaker class
#
# This is a simple demonstration of market making. It is intended to show how to do some things market
# makers require. It is not intended to be an actual, useful market maker.
#
# This market maker performs the following steps:
#
# 1. Cancel any orders
# 2. Update current state
#   2a. Fetch current prices
#   2b. Fetch current inventory
# 3. Figure out what orders to place
# 4. Place those orders
# 5. Sleep for a defined period
# 6. Repeat from Step 1
#
# There are many features missing that you'd expect in a more realistic market maker. Here are just a few:
# * There is very little error handling
# * There is no retrying of failed actions
# * There is no introspection on whether orders are filled
# * There is no inventory management, nor any attempt to balance number of filled buys with number of
#   filled sells.
# * Token prices and quantities are rounded to the token mint's decimals, not the market's tick size and
#   lot size
# * The strategy of placing orders at a fixed spread around the mid price without taking any other factors
#   into account is likely to be costly
# * Place and Cancel instructions aren't batched into single transactions
#

class SimpleMarketMaker:
    def __init__(self, context: mango.Context, wallet: mango.Wallet, market: mango.Market, market_operations: mango.MarketOperations, oracle: mango.Oracle, spread_ratio: Decimal, position_size_ratio: Decimal, existing_order_tolerance: Decimal, pause: timedelta):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.context: mango.Context = context
        self.wallet: mango.Wallet = wallet
        self.market: mango.Market = market
        self.market_operations: mango.MarketOperations = market_operations
        self.oracle: mango.Oracle = oracle
        self.spread_ratio: Decimal = spread_ratio
        self.position_size_ratio: Decimal = position_size_ratio
        self.existing_order_tolerance: Decimal = existing_order_tolerance
        self.pause: timedelta = pause
        self.stop_requested = False

    def start(self):
        # On startup there should be no existing orders. If we didn't exit cleanly last time though,
        # there may still be some hanging around. Cancel any existing orders so we start fresh.
        self.cleanup()

        while not self.stop_requested:
            self.logger.info("Starting fresh iteration.")

            try:
                # Update current state
                price = self.oracle.fetch_price(self.context)
                inventory = self.fetch_inventory()

                # Calculate what we want the orders to be.
                bid, ask = self.calculate_order_prices(price)
                buy_size, sell_size = self.calculate_order_sizes(price, inventory)

                current_orders = self.market_operations.load_my_orders()
                buy_orders = [order for order in current_orders if order.side == mango.Side.BUY]
                if self.orders_require_action(buy_orders, bid, buy_size):
                    self.logger.info("Cancelling BUY orders.")
                    for order in buy_orders:
                        self.market_operations.cancel_order(order)

                    buy_order = self.market_operations.place_order(
                        mango.Side.BUY, mango.OrderType.POST_ONLY, bid, buy_size)
                    self.logger.info(f"Placed order {buy_order} to BUY {buy_size} at {bid}")

                sell_orders = [order for order in current_orders if order.side == mango.Side.SELL]
                if self.orders_require_action(sell_orders, ask, sell_size):
                    self.logger.info("Cancelling SELL orders.")
                    for order in sell_orders:
                        self.market_operations.cancel_order(order)

                    sell_order = self.market_operations.place_order(
                        mango.Side.SELL, mango.OrderType.POST_ONLY, ask, sell_size)
                    self.logger.info(f"Placed order {sell_order} to SELL {sell_size} at {ask}")
            except Exception as exception:
                self.logger.warning(
                    f"Pausing and continuing after problem running market-making iteration: {exception} - {traceback.format_exc()}")

            # Wait and hope for fills.
            self.logger.info(f"Pausing for {self.pause} seconds.")
            time.sleep(self.pause.seconds)

        self.cleanup()

    def stop(self):
        self.stop_requested = True

    def cleanup(self):
        self.logger.info("Cleaning up.")
        orders = self.market_operations.load_my_orders()
        for order in orders:
            self.market_operations.cancel_order(order)

    def fetch_inventory(self) -> typing.Sequence[typing.Optional[mango.TokenValue]]:
        group = mango.Group.load(self.context)
        accounts = mango.Account.load_all_for_owner(self.context, self.wallet.address, group)
        if len(accounts) == 0:
            raise Exception("No Mango account found.")

        account = accounts[0]
        return account.net_assets

    def calculate_order_prices(self, price: mango.Price):
        bid = price.mid_price - (price.mid_price * self.spread_ratio)
        ask = price.mid_price + (price.mid_price * self.spread_ratio)

        return (bid, ask)

    def calculate_order_sizes(self, price: mango.Price, inventory: typing.Sequence[typing.Optional[mango.TokenValue]]):
        base_tokens: typing.Optional[mango.TokenValue] = mango.TokenValue.find_by_token(inventory, price.market.base)
        if base_tokens is None:
            raise Exception(f"Could not find market-maker base token {price.market.base.symbol} in inventory.")

        quote_tokens: typing.Optional[mango.TokenValue] = mango.TokenValue.find_by_token(inventory, price.market.quote)
        if quote_tokens is None:
            raise Exception(f"Could not find market-maker quote token {price.market.quote.symbol} in inventory.")

        total = (base_tokens.value * price.mid_price) + quote_tokens.value
        position_size = total * self.position_size_ratio

        buy_size = position_size / price.mid_price
        sell_size = position_size / price.mid_price
        return (buy_size, sell_size)

    def orders_require_action(self, orders: typing.Sequence[mango.Order], price: Decimal, size: Decimal) -> bool:
        def within_tolerance(target_value, order_value, tolerance):
            tolerated = order_value * tolerance
            return (order_value < (target_value + tolerated)) and (order_value > (target_value - tolerated))
        return len(orders) == 0 or not all([(within_tolerance(price, order.price, self.existing_order_tolerance)) and within_tolerance(size, order.size, self.existing_order_tolerance) for order in orders])

    def __str__(self) -> str:
        return f"""« 𝚂𝚒𝚖𝚙𝚕𝚎𝙼𝚊𝚛𝚔𝚎𝚝𝙼𝚊𝚔𝚎𝚛 for market '{self.market.symbol}' »"""

    def __repr__(self) -> str:
        return f"{self}"
