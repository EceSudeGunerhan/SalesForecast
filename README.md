
# Satış Tahmini API (Northwind)

Bu proje, Northwind veritabanını kullanarak ürün bazlı satış miktarlarını tahmin eden bir makine öğrenmesi modeli içerir. Model, geçmiş satış verileri ile eğitilmiş olup, REST API aracılığıyla tahmin sorguları alabilir.

---

## Proje Özellikleri

- PostgreSQL bağlantılı Northwind veritabanı
- Satış verileri üzerinden özellik mühendisliği
- Decision Tree tabanlı satış tahmin modeli
- FastAPI ile REST API
- Swagger ile otomatik dokümantasyon

---

## Kurulum

### 1. Gerekli kütüphaneleri yükleyin

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL Veritabanı Bağlantısı

`.py` dosyasındaki şu satırı kendi sistemine göre güncelle:

```python
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/gyk2Northwind"
```
---

## API Nasıl Çalıştırılır?

```bash
uvicorn main:app --reload --port 8000
```

Aşağıdaki adreslerden API dokümantasyonuna erişebilirsiniz:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API endpointları

| Endpoint                | Method | Açıklama                              |
|-------------------------|--------|----------------------------------------|
| `/products`             | GET    | Tüm ürünleri listeler                 |
| `/products/{id}`        | GET    | Belirli bir ürünü getirir             |
| `/sales_summary`        | GET    | Ürün ve müşteri bazlı satış özetini döner |
| `/sales_summary_plot`   | GET    | Ürün ve müşteri bazlı satış özeti heatmap tablosunu indirir |
| `/predict`              | POST   | Tahmin yapar (ürün, müşteri, tarih bilgisi ile) |
| `/retrain`              | POST   | Modeli yeniden eğitir (isteğe bağlı)  |

---

## EndPoints

### 1. `/` - Ana Sayfa

**Yöntem:** `GET`

API'nin ana sayfasına erişmek için bu endpointyı kullanabilirsiniz. Bu endpoint API'nin çalıştığını doğrulamak için kullanılabilir.

**Yanıt:**
```json
{
  "message": "Sales Prediction API"
}
```

### 2. `/products/{product_id}` - Ürün Bilgisi Al

**Yöntem:** `GET`

Bu endpoint, belirli bir `product_id`'ye sahip ürünün bilgilerini getirir.

**Parametreler:**
- `product_id` (int): Ürünün kimlik numarası.

**Örnek İstek:**
```
GET /products/1
```

**Yanıt:**
```json
{
  "product": "<Product(product_id=1, product_name=Product 1)>"
}
```

Eğer ürün bulunamazsa, şu şekilde bir mesaj döner:
```json
{
  "message": "Product not found"
}
```

### 3. `/products` - Tüm Ürünleri Listele

**Yöntem:** `GET`

Bu endpoint, sistemdeki tüm ürünleri listelemenizi sağlar.

**Yanıt:**
```json
[
  {
    "product_id": 1,
    "product_name": "Product 1"
  },
  {
    "product_id": 2,
    "product_name": "Product 2"
  },
  ..
]
```

### 4. `/predict` - Satış Tahmini Yap

**Yöntem:** `POST`

Bu endpoint, belirli bir ürün için satış tahmini yapar. İstek gövdesinde ürünle ilgili veriler gönderilmelidir.

**İstek Gövdesi:**
```json
{
  "product_id": 1,
  "customer_id": 10,
  "category_id": 2,
  "unit_price": 14.0,
  "quantity": 10.0,
  "discount": 0.1,
  "order_month": 3,
  "order_day": 15,
  "total_spent": 126.0
}
```

**Yanıt:**
```json
{
  "prediction": "Rejected",
  "details": {
    "product_id": 1,
    "customer_id": 10
  }
}
```

Tahmin sonucu, `"Approved"` veya `"Rejected"` olabilir. Bu sonuç, modelin tahminine bağlı olarak değişir.

### 5. `/retrain` - Modeli Yeniden Eğit

**Yöntem:** `POST`

Bu endpoint, modelin yeniden eğitilmesi için kullanılır. Eğitim sırasında, modelin hata oranı ve doğruluk skoru döndürülür.

**Yanıt:**
```json
{
  "message": "Model retrained successfully.",
  "rmse": 0.2345,
  "r2_score": 0.89
}
```

### 6. `/sales_summary` - Satış Özeti Al

**Yöntem:** `GET`

Bu endpoint, müşteri ve ürün bazında toplam satış miktarlarının özetini döndürür. Veriler bir pivot tablo formatında sunulur.

**Yanıt:**
```json
{
  "sales_table": {
    "1": { "1": 10, "2": 5 },
    "2": { "1": 3, "3": 7 },
    ..
  }
}
```

Bu yanıt, her müşteri için satılan her ürünün miktarını gösteren bir tabloyu içerir.

### 7. `/sales_summary_plot` - Satış Özeti Görseli Al

**Yöntem:** `GET`

Bu endpoint, satış özetini bir heatmap olarak döndürür. Görsel, `PNG` formatında bir dosya olarak sağlanır.

**Yanıt:** (Dosya olarak)
- Bir `PNG` dosyası döndürülür, bu dosya satış özetinin heatmap içerir.

---

## Tahmin Örneği

### `/predict` (POST) isteği örneği:

```json
{
  "product_id": 1,
  "customer_id": 10,
  "category_id": 2,
  "unit_price": 14.0,
  "discount": 0.1,
  "order_month": 3,
  "order_day": 15,
  "total_spent": 126.0
}
```

### Yanıt:

```json
{
  "prediction": "Rejected",
  "details": {
    "product_id": 1,
    "customer_id": 10
  }
}
```

---

## Model Bilgisi

- Model tipi: `DecisionTreeRegressor`
- Hedef değişken: `quantity`
- Performans metrikleri:
  - RMSE: 6.125713178802605
  - R² Skoru: 0.9128970679447462

---

## Geliştirici

- Hatice Kübra TEKİN
- Ece Sude GÜNERHAN
