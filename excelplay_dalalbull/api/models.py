from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

# Details of the user


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    profile_picture = models.URLField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return "{} {}".format(self.email, self.name)


class Portfolio(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    cash_bal = models.DecimalField(
        max_digits=19, decimal_places=2, default=Decimal("100000")
    )
    net_worth = models.DecimalField(
        max_digits=19, decimal_places=2, default=Decimal("100000")
    )
    rank = models.IntegerField(default=131)
    no_trans = models.DecimalField(
        max_digits=19, decimal_places=0, default=Decimal("0")
    )
    margin = models.DecimalField(
        max_digits=19, decimal_places=2, default=Decimal("0.00")
    )
    last_transaction_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return " %10s | %10s | %10s " % (
            self.user_id,
            self.cash_bal,
            self.no_trans,
        )

    class Meta:
        ordering = [
            "-net_worth",
        ]


# Details of the company user owns
class TransactionBuy(models.Model):
    user_id = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(
        max_digits=19, decimal_places=0, validators=[MinValueValidator(Decimal("0.00"))]
    )
    value = models.DecimalField(max_digits=19, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%-30s| %10s | %10s | %10s " % (
            User.objects.get(user_id=self.user_id).user_id,
            self.time,
            self.quantity,
            self.value,
        )


class TransactionShortSell(models.Model):
    user_id = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(
        max_digits=19, decimal_places=0, validators=[MinValueValidator(Decimal("0.00"))]
    )
    value = models.DecimalField(max_digits=19, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%-30s| %10s | %10s | %10s " % (
            User.objects.get(user_id=self.user_id).user_id,
            self.time,
            self.quantity,
            self.value,
        )


class Stock_data(models.Model):
    symbol = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=200, null=True)
    current_price = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    open_price = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    change = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    change_per = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    trade_Qty = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    trade_Value = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    def __str__(self):
        return "%10s    |   %10s " % (
            self.symbol,
            self.current_price,
        )

    def as_dict(self):
        return {
            "name": self.name,
            "symbol": self.symbol,
            "current_price": float(self.current_price),
            "high": float(self.high),
            "low": float(self.low),
            "open_price": float(self.open_price),
            "change": float(self.change),
            "change_per": float(self.change_per),
            "trade_Qty": float(self.trade_Qty),
            "trade_Value": float(self.trade_Value),
        }


class StockDataHistory(models.Model):
    symbol = models.CharField(max_length=30)
    current_price = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%10s    |   %10s |   %10s" % (
            self.symbol,
            self.current_price,
            self.time,
        )


class History(models.Model):
    user_id = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)
    symbol = models.CharField(max_length=10)
    buy_ss = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=19, decimal_places=0, validators=[MinValueValidator(Decimal("0.00"))]
    )
    price = models.DecimalField(max_digits=19, decimal_places=2)

    def as_dict(self):
        return {
            "time": self.time,
            "symbol": self.symbol,
            "buy_ss": self.buy_ss,
            "quantity": float(self.quantity),
            "price": float(self.price),
        }

    def __str__(self):
        return "%-30s| %10s | %10s | %10s | %10s " % (
            User.objects.get(user_id=self.user_id).user_id,
            self.time,
            self.buy_ss,
            self.quantity,
            self.price,
        )


class Pending(models.Model):
    user_id = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    buy_ss = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=19, decimal_places=0, validators=[MinValueValidator(Decimal("0.00"))]
    )
    value = models.DecimalField(max_digits=19, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%-30s| %10s | %10s | %10s | %10s " % (
            User.objects.get(user_id=self.user_id).user_id,
            self.time,
            self.buy_ss,
            self.quantity,
            self.value,
        )
