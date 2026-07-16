"""
Komut satırı argümanlarını okuyup pipeline'ı kurar ve çalıştırır.
"""

import argparse
import sys

from pipeline.core.batch import BatchRunner
from pipeline.core.pipeline import Pipeline
from pipeline.core.stages import IngestionStage, TransformStage
from pipeline.strategies.hashing import Sha256Strategy
from pipeline.strategies.loading import LoadByExif
from pipeline.strategies.decimator import NearestPixelDecimator
from pipeline.strategies.sizing import parse_target_size
from pipeline.io.writers import NpyWriter, PngWriter
from pipeline.io.sidecar import SidecarStore


def build_pipeline(target_size):
    """İki aşamayı, ihtiyaç duydukları somut bağımlılıklarla kurup birleştirir.

    Aşama 1'i temsil eden IngestionStage, dosyayı hashlemek ve piksel
    matrisine çevirmek için bir hash stratejisine ve bir görsel
    yükleyiciye ihtiyaç duyar. Aşama 2'yi temsil eden TransformStage,
    küçültme ve çıktı yazma işini yapmak için bir decimation
    stratejisine, hedef boyuta, tekrar bir hash stratejisine ve bir
    yazıcı listesine ihtiyaç duyar. İkisi de sonucu sidecar dosyasına
    yazmak için bir sidecar deposuna ihtiyaç duyar.

    Burada seçilen somut sınıflar, SHA-256, EXIF-düzeltmeli yükleme, en
    yakın piksel decimation, npy ve png yazıcıları, bu projenin şu anki
    tek uygulamaları. Farklı bir hash algoritması ya da farklı bir
    decimation yöntemi eklenirse, değişecek tek yer burasıdır.

    Args:
        target_size: Küçültme sırasında ulaşılacak hedef boyutu hesaplayan
            strateji.

    Returns:
        Aşama 1'i ve Aşama 2'yi sırayla çalıştıracak bir Pipeline.
    """
    ingestion = IngestionStage(Sha256Strategy(), LoadByExif(), SidecarStore())
    transform = TransformStage(
        NearestPixelDecimator(),
        target_size,
        Sha256Strategy(),
        SidecarStore(),
        [NpyWriter(), PngWriter()],
    )
    return Pipeline([ingestion, transform])


def main():
    """Komut satırı argümanlarını okur ve pipeline'ı çalıştırır.

    Üç argüman okunur: işlenecek dosyanın ya da klasörün yolu; yüzde, oran
    ya da sabit genişlik x yükseklik formatında bir metin olan hedef
    boyut; ve çıktıların yazılacağı ana klasör. Hedef boyut metni, hangi
    somut hedef-boyut stratejisine karşılık geldiğine karar verilerek
    işlenir. Sonrasında pipeline kurulur ve verilen girdi üzerinde
    çalıştırılır; girdi bir klasörse içindeki tüm görseller sırayla
    işlenir.
    """
    parser = argparse.ArgumentParser()
    # Zorunlu, konumsal argüman: tek bir görsel dosyasının
    # ya da bir görsel klasörünün yolu.
    parser.add_argument("input", help="İşlenecek görsel dosyasının ya da görsel klasörünün yolu")
    # Zorunlu argüman: "25%" gibi bir oran ya da "512x384" gibi sabit bir boyut.
    parser.add_argument("--target", required=True, help="Hedef boyut: '25%%' gibi bir oran ya da '512x384' gibi sabit genişlik x yükseklik")
    # Opsiyonel argüman; verilmezse output klasörü kullanılır.
    parser.add_argument("--output", default="output", help="Çıktıların yazılacağı ana klasör (varsayılan: output)")
    args = parser.parse_args()

    # Girdi yolu ya da hedef boyut formatı geçersizse, ValueError fırlatılır.
    # Bu, görsel başına hata izolasyonundan önce, daha işlem başlamadan
    # oluşan bir hata olduğu için burada ayrıca yakalanır; kullanıcıya
    # tam bir traceback yerine tek satır temiz bir mesaj gösterilir.
    try:
        # Metin olarak gelen hedef boyut, uygun somut stratejiye çevrilir.
        target_size = parse_target_size(args.target)

        # Composition root çağrılarak, tüm bileşenlerle kurulmuş pipeline elde edilir.
        pipeline = build_pipeline(target_size)

        # BatchRunner, kendi zaman damgalı çalıştırma klasörünü oluşturur ve
        # verilen girdiyi, ister tek dosya ister klasör olsun, tarayıp her
        # görsel için pipeline'ı çalıştırır.
        runner = BatchRunner(pipeline, args.output)
        runner.run(args.input)
    except ValueError as e:
        print(f"Hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
