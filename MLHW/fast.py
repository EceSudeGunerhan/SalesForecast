import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from flask import Flask,request,jsonify
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error
from sklearn.tree import DecisionTreeRegressor
import pandas as pd

Base = declarative_base()

engine = create_engine("postgresql://postgres:1234@localhost:5432/gyk2Northwind", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(SmallInteger, primary_key=True)
    customer_id = Column(String(5), ForeignKey('customers.customer_id'))
    order_date = Column(Date)
    order_details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = 'order_details'
    order_id = Column(SmallInteger, ForeignKey('orders.order_id'), primary_key=True)
    product_id = Column(SmallInteger, ForeignKey('products.product_id'), primary_key=True)
    unit_price = Column(Float, nullable=False)
    quantity = Column(SmallInteger, nullable=False)
    discount = Column(Float, nullable=False)
    order = relationship("Order", back_populates="order_details")

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(SmallInteger, primary_key=True)
    category_id = Column(SmallInteger, ForeignKey('categories.category_id'))

query = session.query(Order.customer_id, Order.order_date, Product.category_id, Product.product_id, 
                      OrderDetail.unit_price, OrderDetail.quantity, OrderDetail.discount)
query = query.join(OrderDetail, Order.order_id == OrderDetail.order_id)
query = query.join(Product, OrderDetail.product_id == Product.product_id)

data = query.all()

df = pd.DataFrame(data, columns=['customer_id', 'order_date', 'category_id', 'product_id', 'unit_price', 'quantity', 'discount'])
df['order_date'] = pd.to_datetime(df['order_date'])
df['order_month'] = df['order_date'].dt.month
df['order_day'] = df['order_date'].dt.day
df['total_spent'] = df['unit_price'] * df['quantity'] * (1 - df['discount'])
df['product_id'] = df['product_id'].astype(str)
df['customer_id'] = df['customer_id'].astype(str)
df = pd.get_dummies(df, columns=['product_id', 'customer_id'], drop_first=True)

X = df.drop(columns=['quantity', 'order_date'])
y = df['quantity']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeRegressor(random_state=42)
model.fit(X_train, y_train)

#print("Root Mean Squared Error:", root_mean_squared_error(y_test, y_pred))
#print("R^2 Score:", r2_score(y_test, y_pred))

joblib.dump(model,"decisionTree_model.pkl")


app = Flask(__name__) 


model = joblib.load("decisionTree_model.pkl") 

@app.route("/") 
def home():
    return "DecisionTree API hazır "    

@app.route("/prediction", methods=["POST"]) 
def predict():
    data = request.get_json() 
    try:
        age = int(data["age"]) 
        income = int(data["income"])
        credit_score = int(data["credit_score"])
        has_default = int(data["has_default"])

        testData = np.array([[age, income,credit_score,has_default]])
        result = model.predict(testData)[0] 

        return jsonify({     
            "age": age,
            "income": income,
            "credit_score" :credit_score,
            "has_default" : has_default,
            "approved": "kabul edildi" if result == 1 else "kabul edilmedi"  
        })

    except Exception as e:
        return jsonify({"hata": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)