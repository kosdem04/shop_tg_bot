from sqlalchemy import BigInteger, String, create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, sessionmaker
from typing import List
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import datetime

engine = create_engine("sqlite:///tg-shop.db")

Session = sessionmaker(engine)


# declarative base class
class Base(DeclarativeBase):
    pass


# an example mapping using the base
class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String(25))
    basket: Mapped[List["Basket"]] = relationship(back_populates="user")
    order: Mapped[List["Order"]] = relationship(back_populates="user")


class Basket(Base):
    __tablename__ = "basket"

    basket_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id", ondelete='CASCADE'))
    basket_count: Mapped[int]
    basket_date: Mapped[datetime.datetime]
    user: Mapped["User"] = relationship(back_populates="basket", cascade='all, delete')
    product: Mapped["Product"] = relationship(back_populates="basket", cascade='all, delete')


class Type(Base):
    __tablename__ = "type"

    type_id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(25))
    producer: Mapped[List["Producer"]] = relationship(back_populates="type")


class Producer(Base):
    __tablename__ = "producer"

    producer_id: Mapped[int] = mapped_column(primary_key=True)
    producer_name: Mapped[str] = mapped_column(String(25))
    type_id: Mapped[int] = mapped_column(ForeignKey("type.type_id", ondelete='CASCADE'))
    type: Mapped["Type"] = relationship(back_populates="producer", cascade='all, delete')
    product: Mapped[List["Product"]] = relationship(back_populates="producer")


class Product(Base):
        __tablename__ = "product"

        product_id: Mapped[int] = mapped_column(primary_key=True)
        producer_id: Mapped[int] = mapped_column(ForeignKey("producer.producer_id", ondelete='CASCADE'))
        product_name: Mapped[str] = mapped_column(String(25))
        product_desc: Mapped[str] = mapped_column(String(500))
        product_price: Mapped[int]
        product_image: Mapped[str] = mapped_column(String(200))
        producer: Mapped["Producer"] = relationship(back_populates="product", cascade='all, delete')
        basket: Mapped[List["Basket"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "order"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete='CASCADE'))
    order_value: Mapped[str] = mapped_column(String(500))
    order_sum: Mapped[int]
    order_payment: Mapped[str] = mapped_column(String(50))
    order_delivery: Mapped[str] = mapped_column(String(50))
    pointissue_address: Mapped[str] = mapped_column(ForeignKey("pointissue.pointissue_id", ondelete='CASCADE'), default='нет')
    order_address: Mapped[str] = mapped_column(String(200), default='нет')
    order_status: Mapped[str] = mapped_column(String(50))
    order_date: Mapped[datetime.datetime]
    user: Mapped["User"] = relationship(back_populates="order", cascade='all, delete')
    pointissue: Mapped["Pointissue"] = relationship(back_populates="order", cascade='all, delete')


class Pointissue(Base):
    __tablename__ = "pointissue"

    pointissue_id: Mapped[int] = mapped_column(primary_key=True)
    pointissue_address: Mapped[str] = mapped_column(String(200))
    order: Mapped[List["Order"]] = relationship(back_populates="pointissue")


async def db_main():
    Base.metadata.create_all(bind=engine)