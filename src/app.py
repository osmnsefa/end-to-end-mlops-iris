import os
import sys
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- IMPORT AYARI ---
# src klasöründeki modülleri (utils.py gibi) görebilmek için kök dizini ekliyoruz.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import measure_resources

# --- KONFİGÜRASYON ---
# Sabit değerleri en tepede tanımlamak "Best Practice"tir.
# Yarın klasör yapısı değişirse sadece burayı düzeltiriz.
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'iris_model.joblib')
CLASS_MAP = {0: "setosa", 1: "versicolor", 2: "virginica"}

# --- UYGULAMA BAŞLATMA ---
# FastAPI uygulamasını yaratıyoruz. Title ve version, Swagger dökümanında görünür.
app = FastAPI(title="Iris MLOps API", version="1.0.0")

# --- GLOBAL MODEL DEĞİŞKENİ ---
# Modeli burada 'None' olarak başlatıyoruz.
# Amacımız: Modeli uygulama açılırken 1 kere yüklemek ve hep RAM'de tutmak.
model = None

@app.on_event("startup")
def load_model():
    """
    Uygulama başladığında (Docker ayağa kalktığında) çalışır.
    Modeli diskten RAM'e yükler. Bu sayede her gelen istekte tekrar tekrar
    disk okuması yapmayız (Latency Optimization).
    """
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print(f"✅ Model başarıyla yüklendi: {MODEL_PATH}")
        else:
            print(f"⚠️ UYARI: Model dosyası bulunamadı: {MODEL_PATH}")
            print("   -> '/predict' endpoint'i çalışmayacak.")
    except Exception as e:
        print(f"❌ Kritik Hata: Model yüklenirken sorun oluştu: {e}")

# --- VERİ DOĞRULAMA (DATA CONTRACT) ---
# Pydantic kütüphanesi sayesinde, kullanıcı bize "sepal_length" yerine "uzunluk"
# yollarsa veya string yollarsa sistem otomatik hata verir.
# Bu, veri kalitesini koruyan kapı bekçisidir.
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# --- ENDPOINTLER (API UÇLARI) ---

@app.get("/")
def health_check():
    """
    Sağlık kontrolü endpoint'i.
    Kubernetes veya AWS Load Balancer, servisin çöküp çökmediğini anlamak için
    sürekli buraya ping atar.
    """
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/predict")
@measure_resources  # <-- MÜHENDİSLİK DOKUNUŞU: Her isteğin maliyetini (CPU/RAM) ölçer.
def predict(data: IrisInput):
    """
    Çiçek özelliklerini alır ve tür tahmini yapar.
    """
    # 1. Model Kontrolü (Fail Fast)
    if not model:
        raise HTTPException(status_code=503, detail="Model şu an yüklü değil, servis hizmet veremiyor.")
    
    try:
        # 2. Veri Dönüştürme (Preprocessing)
        # Scikit-learn modelleri genellikle 2 boyutlu array bekler [[...]].
        # Gelen veriyi modelin anlayacağı formata çeviriyoruz.
        input_data = [[
            data.sepal_length,
            data.sepal_width,
            data.petal_length,
            data.petal_width
        ]]
        
        # 3. Tahmin (Inference)
        # model.predict bize [0] gibi bir liste döner, biz ilk elemanı alıyoruz.
        prediction_class = model.predict(input_data)[0]
        
        # 4. Sonuç Haritalama (Post-processing)
        # 0, 1, 2 sayılarını insanin anlayacağı "setosa" ismine çeviriyoruz.
        class_name = CLASS_MAP.get(int(prediction_class), "unknown")
        
        return {
            "prediction": int(prediction_class),
            "class_name": class_name
        }
        
    except Exception as e:
        # Beklenmedik bir hata olursa 500 koduyla detay ver.
        raise HTTPException(status_code=500, detail=f"Tahmin hatası: {str(e)}")

# --- LOCAL ÇALIŞTIRMA ---
# Bu dosya doğrudan 'python src/app.py' diye çalıştırılırsa burası devreye girer.
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" -> Dış ağdan erişime izin verir (Docker için şart).
    uvicorn.run(app, host="0.0.0.0", port=8000)