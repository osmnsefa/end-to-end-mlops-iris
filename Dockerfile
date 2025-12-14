# 1. Base Image: Python 3.9'un hafif sürümünü kullanıyoruz (Slim)
FROM python:3.9-slim

# 2. Çalışma Dizini: Konteyner içindeki ana klasörümüz
WORKDIR /app

# 3. Bağımlılıkları Kopyala ve Kur
# Önce SADECE requirements.txt'yi kopyalıyoruz.
# Neden? Çünkü kodun değişse bile kütüphanelerin değişmezse Docker bu adımı "Cache"ten okur.
# Bu, "Docker Layer Caching" denilen mühendislik hilesidir. Build süresini hızlandırır.
COPY requirements.txt .

# Kütüphaneleri kur (--no-cache-dir ile imajı küçültüyoruz)
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kaynak Kodları Kopyala
# src klasörünü ve model dosyasını konteynerin içine atıyoruz.
COPY src/ ./src/

# 5. Portu Dışarı Aç
# FastAPI varsayılan olarak 8000 portunu kullanır.
EXPOSE 8000

# 6. Başlatma Komutu
# Konteyner çalıştığında API'yi başlatsın.
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]