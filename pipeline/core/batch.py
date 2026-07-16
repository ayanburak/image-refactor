"""
Tek bir dosya ya da bir klasör verildiğinde, içindeki tüm görselleri bulup
her biri için pipeline'ın çalıştırılmasını sağlayan otomasyon katmanı.

Her çalıştırma kendi zaman damgalı klasörüne yazılır, böylece farklı
çalıştırmaların çıktıları birbirinin üzerine yazılmaz. Bir görselin
işlenmesi başarısız olursa o görsel loglanıp atlanır; toplu işlemin
geri kalanı durmaz.
"""

from .pipeline import Pipeline
from .context import PipelineContext

from datetime import datetime
import os

class BatchRunner():
    """Bir dosyayı ya da bir klasörü tarayıp her görsel için pipeline'ı çalıştıran sınıf."""

    def __init__(self, pipeline: Pipeline, output_dir = "output"):
        """
        Args:
            pipeline: Her görsel için sırayla çalıştırılacak `Pipeline` nesnesi.
            output_dir: Çıktıların yazılacağı ana klasör. Bu klasörün altına,
                bu çalıştırmaya özel, zaman damgalı bir alt klasör oluşturulur.
        """
        # Zaman damgası burada, __init__'te bir kere hesaplanır; bu sayede
        # aynı BatchRunner ile işlenen tüm görseller aynı çalıştırma
        # klasörüne yazılır, her görsel için ayrı bir zaman damgası oluşmaz.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.pipeline = pipeline

        # Bu çalıştırmaya özel klasörün tam yolu, ana klasör ile zaman
        # damgasının birleştirilmesiyle oluşturulur.
        self.run_output_dir = f"{output_dir}/{timestamp}"

        # Yol sadece bir metin; diskte gerçekten var olması için klasörün
        # oluşturulması gerekir. exist_ok=True, klasör zaten varsa hata
        # verilmemesini sağlar.
        os.makedirs(self.run_output_dir, exist_ok=True)

    def discover_images(self, folder: str) -> list[str]:
        """Bir klasörü ve tüm alt klasörlerini gezip desteklenen uzantılı
        dosyaların tam yollarını listeler.

        Args:
            folder: Taranacak klasörün yolu.

        Returns:
            Bulunan görsel dosyalarının tam yollarından oluşan bir liste.
        """
        results = []

        # os.walk(folder), verilen klasörü ve tüm alt klasörlerini gezer;
        # her adımda o an bulunulan klasörün yolu (dirpath) ve o
        # klasördeki dosya adları (filenames) verilir.
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                # Uzantı küçük/büyük harf farkı gözetmeden kontrol edilir.
                if filename.lower().endswith((".jpg", ".jpeg", ".heic", ".png")):
                    # dirpath ve filename ayrı ayrı geldiği için, ikisi
                    # birleştirilerek dosyanın tam yolu elde edilir.
                    results.append(os.path.join(dirpath, filename))

        return results

    def run(self, input_path: str) -> None:
        """Girdiyi işler: tek bir dosyaysa onu, bir klasörse içindeki tüm
        görselleri sırayla pipeline'dan geçirir.

        Her görsel için sırasıyla: aynı isimli dosyaların birbirinin
        üzerine yazmaması için görselin klasör içindeki göreli konumu
        korunarak çıktı yolu hesaplanır; gerekli alt klasörler diskte
        oluşturulur; o görsele ait bir `PipelineContext` oluşturulur;
        pipeline çalıştırılır. Bir hata oluşursa hata ekrana yazdırılır,
        o görsel atlanır ve kalan görsellerin işlenmesine devam edilir.

        Args:
            input_path: Tek bir görsel dosyasının ya da bir görsel
                klasörünün yolu.

        Raises:
            ValueError: input_path ne bir dosya ne de bir klasörse.
        """
        # Girdi tek bir dosyaysa, tek elemanlı bir liste yeterli. Bir
        # klasörse, içindeki tüm görseller discover_images ile bulunur.
        if os.path.isfile(input_path):
            image_paths = [input_path]
        elif os.path.isdir(input_path):
            image_paths = self.discover_images(input_path)
        else:
            raise ValueError(f"Geçersiz yol: {input_path}")

        for image_path in image_paths:
            # "stem", dosyanın uzantısız kısmı; çıktı dosyalarının adının
            # temeli olarak kullanılır.
            #
            # Girdi bir klasörse, aynı isimli iki dosya farklı alt
            # klasörlerde olabilir. Bu yüzden stem, görselin klasör
            # içindeki göreli konumunu da içerir; böylece ikisi farklı
            # çıktı yollarına yazılır, birbirinin üzerine yazmazlar.
            #
            # Girdi tek bir dosyaysa, böyle bir çakışma riski yoktur;
            # sadece dosyanın kendi adı yeterlidir.
            if os.path.isdir(input_path):
                stem = os.path.splitext(os.path.relpath(image_path, start=input_path))[0]
            else:
                stem = os.path.splitext(os.path.basename(image_path))[0]

            # Bu çalıştırmanın klasörü ile stem birleştirilerek, bu
            # görsele özel, uzantısız çıktı öneki elde edilir.
            output_base_path = os.path.join(self.run_output_dir, stem)

            # stem alt klasör adları da içerebildiği için, o alt klasörün
            # diskte var olduğundan emin olunur. Sadece os.path.dirname ile
            # elde edilen klasör kısmı oluşturulur, dosya öneki değil.
            os.makedirs(os.path.dirname(output_base_path), exist_ok=True)

            sidecar_path = output_base_path + ".sidecar.json"

            # Bu görsele özel bilgileri taşıyacak, henüz boş context oluşturulur.
            context = PipelineContext(
                source_path=image_path,
                output_base_path=output_base_path,
                sidecar_path=sidecar_path,
            )

            # Bir görselin işlenmesi başarısız olursa, hata ekrana
            # yazdırılır ve bu görsel atlanır; toplu işlemin geri kalanı durmaz.
            try:
                self.pipeline.run(context)
            except Exception as e:
                print(f"Başarısız: {image_path} — {e}")
                continue
