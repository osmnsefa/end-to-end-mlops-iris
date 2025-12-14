import os
import sys
import joblib  # Modeli diske kaydetmek ve geri yüklemek için standart kütüphane
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# --- IMPORT AYARI ---
# Python normalde çalıştığı klasörü baz alır. src klasörünün içindeyken 
# bir üst dizindeki modülleri görebilmesi için proje kök dizinini yola ekliyoruz.
# Bu sayede 'from src.utils' komutu hata vermez.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import measure_resources

@measure_resources  # <-- KENDİ YAZDIĞIMIZ DECORATOR. CPU/RAM ölçümü yapar.
def train_model():
    """
    Iris veri seti üzerinde RandomForest modeli eğitir, metrikleri MLflow'a kaydeder
    ve eğitilen modeli diske yazar.
    """
    print("🚀 Eğitim pipeline'ı başlatılıyor...")
    
    # MLflow Autolog: Biz tek tek yazmasak bile, kullanılan parametreleri 
    # ve model başarısını otomatik yakalar.
    mlflow.sklearn.autolog()

    # 1. Veri Yükleme (Data Ingestion)
    print("📦 Veri seti yükleniyor...")
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    
    # 2. Veri Bölme (Splitting)
    # Verinin %20'sini test için ayırıyoruz. random_state=42 sayesinde
    # her çalıştırdığımızda aynı şekilde bölünür (Tekrarlanabilirlik).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 3. MLflow Deney Başlatma (Experiment Tracking)
    # 'with' bloğu, deneyin başlayıp güvenli bir şekilde bitmesini sağlar.
    with mlflow.start_run() as run:
        
        # Hiperparametre Tanımı
        n_estimators = 100
        
        # Parametreyi Logla: İleride "Hangi parametre ile eğitmiştim?" dememek için.
        mlflow.log_param("n_estimators", n_estimators)
        
        # 4. Model Eğitimi (Training)
        print(f"⚙️  RandomForest eğitiliyor (Ağaç Sayısı: {n_estimators})...")
        clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        clf.fit(X_train, y_train)
        
        # 5. Değerlendirme (Evaluation)
        print("📊 Model test ediliyor...")
        predictions = clf.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        # Metriği Logla: Başarı skorunu MLflow'a gönder.
        mlflow.log_metric("accuracy", accuracy)
        print(f"✅ Model Doğruluğu (Accuracy): {accuracy:.4f}")

        # 6. Modeli Kaydetme (Model Registry / Artifacts)
        # Model dosyasını kaydedeceğimiz klasörü belirliyoruz.
        model_dir = os.path.join(os.path.dirname(__file__), 'model')
        
        # Eğer klasör yoksa oluştur (Defensive Programming)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
            print(f"📂 Klasör oluşturuldu: {model_dir}")
            
        model_path = os.path.join(model_dir, 'iris_model.joblib')
        
        # Modeli fiziksel dosya olarak kaydet (.joblib)
        joblib.dump(clf, model_path)
        print(f"💾 Model diske kaydedildi: {model_path}")
        
        # Modeli MLflow Artifact olarak da kaydet (Yedekleme ve versiyonlama için)
        mlflow.sklearn.log_model(clf, "model")
        
        return accuracy

if __name__ == "__main__":
    try:
        # Fonksiyonu çalıştır
        acc = train_model()
        print(f"\n🎉 Pipeline başarıyla tamamlandı! Final Skor: {acc:.4f}")
        
    except Exception as e:
        # Eğer bir hata olursa, sistem (CI/CD) bunu bilsin diye hata kodu ile çık.
        print(f"\n❌ Pipeline hatası: {e}")
        sys.exit(1)