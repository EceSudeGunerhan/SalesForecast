
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
uvicorn northwind:app --reload
```

Aşağıdaki adreslerden API dokümantasyonuna erişebilirsiniz:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Uç Noktaları

| Endpoint                | Method | Açıklama                              |
|-------------------------|--------|----------------------------------------|
| `/products`             | GET    | Tüm ürünleri listeler                 |
| `/products/{id}`        | GET    | Belirli bir ürünü getirir             |
| `/sales_summary`        | GET    | Ürün ve müşteri bazlı satış özetini döner |
| `/sales_summary_plot`   | GET    | Ürün ve müşteri bazlı satış özeti heatmap tablosunu indirir |
| `/predict`              | POST   | Tahmin yapar (ürün, müşteri, tarih bilgisi ile) |
| `/retrain`              | POST   | Modeli yeniden eğitir (isteğe bağlı)  |

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
  "predicted_quantity": 7.0,
  "input_details": {
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
