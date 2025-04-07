import io
from flask import app
import joblib
from matplotlib import pyplot as plt
from sklearn.metrics import root_mean_squared_error,r2_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger, Date, Float, ForeignKey, Text, LargeBinary, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, aliased
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import seaborn as sns
from fastapi.responses import StreamingResponse

# SQLAlchemy Base class
Base = declarative_base()

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/gyk2Northwind"  

# Veritabanı bağlantısı
engine = create_engine(DATABASE_URL, echo=True)  # echo=True logları görmek için

# Veritabanını oluşturma
Base.metadata.create_all(engine)

# Oturum açma
Session = sessionmaker(bind=engine)
session = Session()                 #SELECT, INSERT, UPDATE gibi işlemler yapılabilir.

# Categories Sınıfı
class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(SmallInteger, primary_key=True)
    category_name = Column(String(15), nullable=False)
    description = Column(Text)
    picture = Column(LargeBinary)

    # Relationship with Product
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(category_id={self.category_id}, category_name={self.category_name})>"

# Customers Sınıfı
class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(String(5), primary_key=True)
    company_name = Column(String(40), nullable=False)
    contact_name = Column(String(30))
    contact_title = Column(String(30))
    address = Column(String(60))
    city = Column(String(15))
    region = Column(String(15))
    postal_code = Column(String(10))
    country = Column(String(15))
    phone = Column(String(24))
    fax = Column(String(24))

    # Relationship with Order
    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, company_name={self.company_name})>"

# OrderDetails Sınıfı
class OrderDetail(Base):
    __tablename__ = 'order_details'

    order_id = Column(SmallInteger, ForeignKey('orders.order_id'), primary_key=True)
    product_id = Column(SmallInteger, ForeignKey('products.product_id'), primary_key=True)
    unit_price = Column(Float, nullable=False)
    quantity = Column(SmallInteger, nullable=False)
    discount = Column(Float, nullable=False)

    # Relationships with Order and Product
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")

    def __repr__(self):
        return f"<OrderDetail(order_id={self.order_id}, product_id={self.product_id})>"

# Orders Sınıfı
class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(SmallInteger, primary_key=True)
    customer_id = Column(String(5), ForeignKey('customers.customer_id'))
    employee_id = Column(SmallInteger)
    order_date = Column(Date)
    required_date = Column(Date)
    shipped_date = Column(Date)
    ship_via = Column(SmallInteger)
    freight = Column(Float)
    ship_name = Column(String(40))
    ship_address = Column(String(60))
    ship_city = Column(String(15))
    ship_region = Column(String(15))
    ship_postal_code = Column(String(10))
    ship_country = Column(String(15))

    # Relationship with Customer and OrderDetail
    customer = relationship("Customer", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, customer_id={self.customer_id})>"

# Products Sınıfı
class Product(Base):
    __tablename__ = 'products'

    product_id = Column(SmallInteger, primary_key=True)
    product_name = Column(String(40), nullable=False)
    supplier_id = Column(SmallInteger)
    category_id = Column(SmallInteger, ForeignKey('categories.category_id'))
    quantity_per_unit = Column(String(20))
    unit_price = Column(Float)
    units_in_stock = Column(SmallInteger)
    units_on_order = Column(SmallInteger)
    reorder_level = Column(SmallInteger)
    discontinued = Column(Integer, nullable=False)

    # Relationship with Category and OrderDetail
    category = relationship("Category", back_populates="products")
    order_details = relationship("OrderDetail", back_populates="product")

    def __repr__(self):
        return f"<Product(product_id={self.product_id}, product_name={self.product_name})>"

# Veritabanına örnek veri sorgulama
customer = session.query(Customer).filter_by(customer_id='ALFKI').first()
print(customer)

order = session.query(Order).filter_by(order_id=1).first()
print(order)


"""
SELECT o.customer_id, o.order_date, p.category_id, p.product_id, od.unit_price, od.quantity, od.discount
FROM orders AS o
INNER JOIN order_details AS od ON o.order_id = od.order_id
INNER JOIN products AS p ON p.product_id = od.product_id
"""

stmt = select(
    Order.customer_id,
    Order.order_date,
    Product.category_id,
    Product.product_id,
    OrderDetail.unit_price,
    OrderDetail.quantity,
    OrderDetail.discount
).select_from(Order).join(
    OrderDetail, Order.order_id == OrderDetail.order_id
).join(
    Product, OrderDetail.product_id == Product.product_id
)
result = session.execute(stmt).fetchall()
for row in result:
    print(row)

df = pd.DataFrame(result, columns=['customer_id', 'order_date', 'category_id', 'product_id', 'unit_price', 'quantity', 'discount'])
df['order_date'] = pd.to_datetime(df['order_date'])
df['order_month'] = df['order_date'].dt.month
df['order_day'] = df['order_date'].dt.day
df['total_spent'] = df['unit_price'] * df['quantity'] * (1 - df['discount'])
df['product_id'] = df['product_id'].astype(str)
#df['customer_id'] = df['customer_id'].astype(str)
df['original_customer_id'] = df['customer_id']  # orijinal string ID
df['customer_id'] = df['customer_id'].astype('category').cat.codes
#df = pd.get_dummies(df, columns=['product_id', 'customer_id'], drop_first=True)

def train_model(df):
    X = df.drop(columns=['quantity', 'order_date','original_customer_id'])
    y = df['quantity']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    joblib.dump(model, "hw.pkl")
    print("Model kaydedildi.")

    return rmse, r2


def get_products():
    stmt = select(Product)
    result = session.execute(stmt).fetchall()
    return [product for product in result]

# FastAPI uygulaması

class predict(BaseModel):
    product_id: int
    customer_id: int
    category_id: int
    unit_price: float
    #quantity: int
    discount: float
    order_month: int   
    order_day: int
    total_spent: float

app = FastAPI(
title="Sales Forecast API",
version="1.0"
)

@app.get("/",summary="Main Page", tags=["SalesForecast"])
async def my_first_get_api():
    return {"message":"First FastAPI example"}

@app.get("/products/{product_id}", tags=["SalesForecast"])
def get_product(product_id: int):
    stmt = select(Product).where(Product.product_id == product_id)
    result = session.execute(stmt).fetchone()
    if result:
        return {"product": result[0].product_name}
    else:
        return {"message": "Product not found"}
    
@app.get("/products", tags=["SalesForecast"])
def get_all_products():
    stmt = select(Product)
    result = session.execute(stmt).fetchall()
    return [{"product_id": product[0].product_id, "product_name": product[0].product_name} for product in result]

'''
@app.post("/predict")
def predict_quantity(predict:predict):
    dt_model = joblib.load("hw.pkl")
    prediction = dt_model.predict([[predict.product_id, predict.category_id, predict.unit_price, predict.quantity, predict.discount, predict.order_month, predict.order_day, predict.total_spent]])[0]
    result = "Approved" if prediction == 1 else "Rejected"
    return {
        "prediction": result,
        "details":
        {
            "product_id": predict.product_id,
            "customer_id": predict.customer_id
        }
    }
'''

@app.post("/predict", tags=["SalesForecast"])
def predict_quantity(predict: predict):
    dt_model = joblib.load("hw.pkl")

    # customer_id sütunu zaten encoded (int), tekrar .cat.codes yapmaya gerek yok
    try:
        customer_id_code = df[df['original_customer_id'] == predict.customer_id]['customer_id'].values[0]
    except IndexError:
        customer_id_code = 0  # tahmin edilemeyen müşteri varsa varsayılan değer

    features = [
        predict.product_id,
        predict.category_id,
        predict.unit_price,
        predict.discount,
        predict.order_month,
        predict.order_day,
        predict.total_spent,
        customer_id_code
    ]

    prediction = dt_model.predict([features])[0]

    return {
        "predicted_quantity": round(prediction, 2),
        "details": {
            "product_id": predict.product_id,
            "customer_id": predict.customer_id
        }
    }

@app.post("/retrain", tags=["SalesForecast"])
def retrain_model():
    rmse, r2 = train_model(df)
    return {
        "message": "Model retrained successfully.",
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4)
    }

@app.get("/sales_summary", tags=["SalesForecast"])
def get_sales_summary():
    sales_summary = df.groupby(['customer_id', 'product_id']).agg({'quantity': 'sum'}).reset_index()

    # Create a pivot table where rows are customers, columns are products, and values are quantities
    pivot_table = sales_summary.pivot_table(index='customer_id', columns='product_id', values='quantity', aggfunc='sum', fill_value=0)
    
    # Convert the pivot table into a dictionary format for easy JSON response
    sales_table = pivot_table.to_dict(orient='index')
    
    # Return the table in JSON format for API response
    return {"sales_table": sales_table}

@app.get("/sales_summary_plot", tags=["SalesForecast"])
def get_sales_summary_plot():
    # Grouping and pivoting the data as per your logic
    sales_summary = df.groupby(['customer_id', 'product_id']).agg({'quantity': 'sum'}).reset_index()
    pivot_table = sales_summary.pivot_table(index='customer_id', columns='product_id', values='quantity', aggfunc='sum', fill_value=0)

    # Create a heatmap using seaborn
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_table, cmap="YlGnBu")
    plt.title("Sales Summary Heatmap")

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # Move the pointer to the start of the BytesIO object

    # Return the image as a downloadable file
    return StreamingResponse(img, media_type="image/png", headers={"Content-Disposition": "attachment; filename=sales_summary.png"})




# Aylık satış özeti:
monthly_sales = df.groupby('order_month')['quantity'].sum().reset_index()

# Ürün bazlı satış:
product_sales = df.groupby('product_id')[['quantity','total_spent']].sum().reset_index()

#musteri bazli satis
customer_sales = df.groupby('customer_id').size().reset_index(name='order_counts')

# Müşteri segmentasyonu (örnek kural)
customer_sales['Segment'] = pd.cut(customer_sales['order_counts'], bins=[0, 50, 100, 150],
                labels=['Bronz', 'Silver','Gold'])
    
print(" ")
print("MÜŞTERİ BAZLI SATIŞ ÖZETİ : ")
print(customer_sales)
print(" ")
print("AYLIK SATIŞ ÖZETİ : ")
print(monthly_sales)
print(" ")
print("ÜRÜN BAZLI SATIŞ ÖZETİ :")
print(product_sales)



# Hata yönetimi ve validasyon

# uvicorn main:app --reload
# http://localhost:8000/docs  -> Swagger UI
# http://localhost:8000/redoc -> ReDoc
# http://localhost:8000/openapi.json -> OpenAPI JSON
# Ctrl + C ile durdurabilirsiniz

# Projenin requirements.txt ile dışa aktarılması
# pip freeze > requirements.txt
