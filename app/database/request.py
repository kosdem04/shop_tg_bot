from sqlalchemy import select
from app.database.models import Session, User, Basket, Type, Producer, Product, engine, Order
from datetime import datetime


def add_new_user(tg_id, name):
    with Session.begin() as session:
        #user = session.query(User).filter(User.user_tg_id == tg_id).scalar()
        user = session.scalar(select(User).where(User.user_tg_id == tg_id))
        if not user:
            session.add(User(user_tg_id=tg_id, user_name=name))
            session.commit()


def show_catalog():
    with Session.begin() as session:
        catalog = session.query(Type).all()
        session.expunge_all()
        session.close()
        return catalog


def select_producer(name):
    with Session.begin() as session:
        producer = session.scalar(select(Producer.producer_id).where(Producer.producer_name == name))
        if not producer:
            exist = False
        else:
            exist = producer
        return exist


def add_product(producer_id, name, desc, price, image):
    with Session.begin() as session:
        session.add(Product(producer_id=producer_id, product_name=name,
                            product_desc=desc, product_price=price, product_image=image))
        session.commit()


def show_product(id_producer):
    with Session.begin() as session:
        products = session.query(Product).filter(Product.producer_id == id_producer).all()
        session.expunge_all()
        session.close()
        return products


def show_types(id_producer):
    with Session.begin() as session:
        producer = session.scalar(select(Producer.type_id).where(Producer.producer_id == id_producer))
        types = session.scalar(select(Type.type_id).where(Type.type_id == producer))
        session.expunge_all()
        session.close()
        return types


def show_phone_item(sq_id):
    with Session.begin() as session:
        phone = session.scalar(select(Product).where(Product.product_id == sq_id))
        session.expunge_all()
        session.close()
        return phone


def show_producer(id_type):
    with Session.begin() as session:
        producer = session.query(Producer).filter(Producer.type_id == id_type).all()
        session.expunge_all()
        session.close()
        return producer


def add_basket(user_id, product_id, basket_count):
    with Session.begin() as session:
        basket = session.scalar(select(Basket).where(Basket.user_id == user_id, Basket.product_id == product_id))
        if not basket:
            session.add(Basket(user_id=user_id, product_id=product_id, basket_count=basket_count, basket_date=datetime.now()))
            session.commit()
        else:
            return False


def is_basket(user_id, product_id):
    with Session.begin() as session:
        basket = session.scalar(select(Basket).where(Basket.user_id == user_id, Basket.product_id == product_id))
        if not basket:
            return True
        else:
            return False


def del_basket(user_id, product_id):
    with Session.begin() as session:
        basket = session.scalar(select(Basket).where(Basket.user_id == user_id, Basket.product_id == product_id))
        if not basket:
            return False
        else:
            session.query(Basket).filter(Basket.user_id == user_id, Basket.product_id == product_id).delete()
            #session.delete(basket)
            session.commit()


def show_basket(user_id):
    with Session.begin() as session:
        baskets = session.query(Basket.basket_id, Product.product_name, Product.product_price,
                                Product.product_id, Basket.basket_count).join(Product).filter(Basket.user_id == user_id).all()
        session.expunge_all()
        session.close()
        return baskets


def search(stroka):
    with Session.begin() as session:
        searches = session.query(Product).filter(Product.product_name.like(f'%{stroka}%'))
        #searches = session.scalars(select(Product).where(Product.product_name.like(f'%{stroka}%')))
        #if searches == None:
            #return False
        #else:
        return searches


def add_order(user_id, payment, delivery, sum):
    with Session.begin() as session:
        baskets = show_basket(user_id)
        stroka = ''
        for sq in baskets:
            stroka = stroka + f'{sq[1]}\n'
        session.add(Order(user_id=user_id, order_value=stroka, order_sum=sum, order_payment=payment,
                          order_delivery=delivery,
                          order_status='Заказ принят на обработку', order_date=datetime.now()))
        session.commit()


def show_orders(user_id):
    with Session.begin() as session:
        orders = session.query(Order.order_id).filter(Order.user_id == user_id).all()
        #orders = session.query(Order.order_id, Order.order_value, Order.order_status,
                              # Order.order_date, Basket.basket_id, Basket.user_id,
                              # Product.product_name, Product.product_price
                               #).join(Basket).join(Product).filter(Order.basket_id == basket.basket_id).all()
        session.expunge_all()
        session.close()
        return orders


def show_order(order_id):
    with Session.begin() as session:
        #orders = session.query(Order.order_id, Order.user_id, Order.order_value,
                               #Order.order_sum, Order.order_payment, Order.order_delivery,
                               #Order.order_status, Order.order_date).filter(Order.order_id == order_id).all()
        orders = session.scalar(select(Order).where(Order.order_id == order_id))
        print(orders)
        session.expunge_all()
        session.close()
        return orders


def is_order(user_id):
    with Session.begin() as session:
        order = session.query(Order.order_id).filter(Order.user_id == user_id).all()
        if not order:
            return False
        else:
            return True


def send_all():
    with Session.begin() as session:
        users = session.query(User).all()
        session.expunge_all()
        session.close()
        return users