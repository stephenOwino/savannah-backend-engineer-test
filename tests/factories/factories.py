# api/tests/factories.py
import uuid
from decimal import Decimal

import factory
from django.contrib.auth.models import User
from faker import Faker

from api.models import Category, Customer, Order, OrderItem, Product

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    # Generate truly unique usernames to avoid duplicates
    username = factory.LazyFunction(lambda: f"user_{uuid.uuid4().hex[:12]}")
    email = factory.LazyFunction(lambda: f"user_{uuid.uuid4().hex[:8]}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Handle the case where Customer is automatically created by a signal
        when User is created. This prevents duplicate customer creation.
        """
        user = kwargs.get("user")
        if not user:
            user = UserFactory()
            kwargs["user"] = user

        # Check if customer already exists for this user (created by signal)
        try:
            customer = model_class.objects.get(user=user)
            # Update the customer with any provided kwargs (except user)
            update_kwargs = {k: v for k, v in kwargs.items() if k != "user"}
            for key, value in update_kwargs.items():
                setattr(customer, key, value)
            if update_kwargs:
                customer.save()
            return customer
        except model_class.DoesNotExist:
            return super()._create(model_class, *args, **kwargs)

    user = factory.SubFactory(UserFactory)
    # Generate shorter phone number to fit varchar(20) constraint
    phone_number = factory.LazyFunction(lambda: f"+1{fake.random_int(min=1000000000, max=9999999999)}")
    address = factory.Faker("address")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    parent = None


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    description = factory.Faker("text")
    price = Decimal("10.00")
    stock = 10
    category = factory.SubFactory(CategoryFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(CustomerFactory)
    total_amount = Decimal("0.00")


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
