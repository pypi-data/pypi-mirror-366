import random
from decimal import Decimal

import factory
from faker import Faker

from wbportfolio.models import Order

fake = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    order_proposal = factory.SubFactory("wbportfolio.factories.OrderProposalFactory")
    currency_fx_rate = Decimal(1.0)
    fees = Decimal(0.0)
    underlying_instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    shares = factory.Faker("pydecimal", min_value=10, max_value=1000, right_digits=4)
    price = factory.LazyAttribute(lambda o: random.randint(10, 10000))
