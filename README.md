# 🚀 End-to-End MLOps Pipeline (Iris Project)

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Container-blue?style=for-the-badge&logo=docker)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-orange?style=for-the-badge&logo=mlflow)

## 📖 Proje Özeti
Bu proje, klasik bir Makine Öğrenmesi problemini (Iris Sınıflandırma) **Production-Grade (Canlıya Hazır)** standartlarda bir MLOps boru hattına dönüştürmeyi amaçlar. 

Sadece model eğitimine değil, modelin **servis edilmesi (Deployment)**, **izlenmesi (Monitoring)**, **yük testleri (Load Testing)** ve **maliyet simülasyonuna (FinOps)** odaklanılmıştır.

## 🛠️ Kullanılan Teknolojiler

| Alan | Araçlar | Amaç |
| :--- | :--- | :--- |
| **Backend & API** | `FastAPI`, `Uvicorn`, `Pydantic` | Yüksek performanslı asenkron API ve veri doğrulama. |
| **ML & MLOps** | `Scikit-Learn`, `MLflow` | Model eğitimi ve deney takibi (Experiment Tracking). |
| **Containerization** | `Docker` | Uygulamanın izole ve taşınabilir çalışması. |
| **Testing** | `Locust`, `Pytest` | Yük testi (Load Test) ve birim testler. |
| **Monitoring** | `Psutil`, `Custom Decorators` | CPU/RAM kullanımı ve Latency ölçümü. |

---

## ⚙️ Özellikler ve Mühendislik Yaklaşımları

### 1. Resource Monitoring (Kaynak İzleme) 📊
Sistemdeki her tahmin isteği (`/predict`), özel yazılmış bir **Python Decorator** tarafından izlenir.
- **Latency (Gecikme):** İşlemin kaç ms sürdüğü.
- **Memory Footprint:** İşlem sırasında RAM kullanımındaki değişim (MB).

### 2. Defensive Programming (Savunmacı Programlama) 🛡️
- `try-except` blokları ile API çökmez, anlamlı hata kodları (503, 500) döner.
- `Pydantic` şemaları ile hatalı veri girişleri (örn: string yerine float) en başta engellenir.
- Model, uygulama başlarken (`startup event`) belleğe yüklenir (Caching), böylece disk I/O maliyeti düşürülür.

### 3. Load Testing & Stability (Saldırı Testi) ⚔️
Sistem **Locust** ile test edilmiştir.
- **Senaryo:** 50 Eşzamanlı Kullanıcı (Concurrent Users).
- **Sonuç:** %0 Hata oranı ile saniyede ortalama 22 istek (RPS) karşılanmıştır.
*(Test sonuçları ekran görüntüleri aşağıdadır)*

---

## 🚀 Kurulum ve Çalıştırma

Projeyi çalıştırmak için iki yöntem vardır:

### Yöntem 1: Docker ile (Önerilen) 🐳
Bilgisayarınızda hiçbir kütüphane kurmadan, izole ortamda çalıştırın.

```bash
# 1. İmajı oluşturun
docker build -t iris-mlops-app .

# 2. Konteyneri başlatın
docker run -p 8000:8000 iris-mlops-app