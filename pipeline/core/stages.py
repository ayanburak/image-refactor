"""
Pipeline'ın aşamalarını (Aşama 1, Aşama 2) tanımlayan modül.

Her aşama, bir `PipelineContext`'i alıp üzerinde değişiklik yapar; dönüş
değeri yoktur. `pipeline.py`, bu aşamaları hangi somut sınıf olduklarını
bilmeden, sırayla `run(context)` diye çağırır.
"""

from abc import abstractmethod, ABC
from .context import PipelineContext
from ..io.writers import OutputWriter
from ..io.sidecar import SidecarStore

from ..strategies.sizing import TargetSize
from ..strategies.hashing import HashingStrategy
from ..strategies.loading import ImageLoader
from ..strategies.decimator import Decimator

# --- Soyut Sınıf ---

class PipelineStage(ABC):
    """Pipeline aşamaları için soyut sınıf."""

    @abstractmethod
    def run(self, context: PipelineContext) -> None:
        """Aşamanın işini yapar, context üzerinde değişiklik yapar.

        Args:
            context: İşlenen görsele ait, aşamalar arası taşınan veri paketi.
        """
        pass

# --- Somut aşamalar ---

class IngestionStage(PipelineStage):
    """Aşama 1: dosya hashlenir, piksel matrisine çevrilir, sidecar'a yazılır."""

    def __init__(self, 
                 hash_strategy: HashingStrategy, 
                 image_loader: ImageLoader, 
                 sidecar_store: SidecarStore):
        """
        Args:
            hash_strategy: Dosyayı hashlemek için kullanılacak `HashingStrategy`.
            image_loader: Görseli piksel matrisine çevirmek için `ImageLoader`.
            sidecar_store: Sonucu json'a yazmak için `SidecarStore`.
        """
        self.hash_strategy = hash_strategy
        self.image_loader = image_loader
        self.sidecar_store = sidecar_store

    def run(self, context: PipelineContext) -> None:
        # Dosya hashlenir, sonuç context'e yazılır. Bu hash, Aşama 2'nin
        # sonunda tekrar hesaplanıp bununla karşılaştırılacak.
        context.original_hash = self.hash_strategy.hash_file(context.source_path)

        # Aynı dosya EXIF düzeltmeli piksel matrisine çevrilir, context'e yazılır.
        context.pixel_matrix = self.image_loader.load(context.source_path)

        # Şu ana kadar bilinen tek şey sidecar dosyasına yazılır;
        # dosya henüz yoksa burada oluşturulur.
        self.sidecar_store.update(context.sidecar_path, {"original_hash": context.original_hash})


class TransformStage(PipelineStage):
    """Aşama 2: küçültülür, çıktılar yazılır, bütünlük doğrulanır, sidecar'a yazılır."""

    def __init__(self,
                 decimator: Decimator,
                 target_size: TargetSize,
                 hashing_strategy: HashingStrategy,
                 sidecar_store: SidecarStore,
                 writers: list[OutputWriter]):
        """
        Args:
            decimator: Piksel matrisini küçültmek için kullanılacak `Decimator`.
            target_size: Hedef boyutu hesaplayacak `TargetSize` — tüm
                çalıştırma boyunca sabittir, context'te değil burada tutulur.
            hashing_strategy: Bütünlük kontrolü için dosyayı yeniden
                hashlemekte kullanılacak `HashingStrategy`.
            sidecar_store: Sonucu json'a yazmak için `SidecarStore`.
            writers: Küçültülmüş matrisi hangi formatlarda (`.npy`, `.png`)
                yazacağını belirleyen `OutputWriter` listesi. Yeni bir format
                eklemek için bu listeye yeni bir yazıcı eklemek yeterlidir.
        """
        self.decimator = decimator
        self.target_size = target_size
        self.hashing_strategy = hashing_strategy
        self.sidecar_store = sidecar_store
        self.writers = writers

    def run(self, context: PipelineContext) -> None:
        # Hedef boyut, o an işlenen görselin gerçek orijinal boyutuna göre
        # hesaplanır. RatioTargetSize bunu kullanır, FixedTargetSize yok sayar.
        size = self.target_size.get_size(
            context.pixel_matrix.shape[0],
            context.pixel_matrix.shape[1]
            )

        # Piksel atlanarak (interpolasyonsuz) küçültülmüş matris üretilir.
        decimated_matrix = self.decimator.decimate(context.pixel_matrix, size)

        # self.writers liste [NpyWriter(), PngWriter()] Listedeki
        # her yazıcı tek tek çalıştırılır; hangi yazıcılar olduğu ya da kaç
        # tane olduğu bu kod tarafından hiç bilinmez, sadece sırayla çağrılır.
        for writer in self.writers:
            # Her yazıcıyla kendi formatına yazılır, gerçekten yazılan tam yol döndürülür.
            path = writer.write(decimated_matrix, context.output_base_path)
            # Dönen yolun uzantısına bakılarak, bunun context'in hangi
            # alanına kaydedileceği belirlenir.
            if path.endswith(".npy"):
                context.npy_output_path = path
            elif path.endswith(".png"):
                context.png_output_path = path

        # Bütünlük kontrolü. Dosya tekrar hashlenir. Aşama 1'deki
        # hash ile aynı çıkarsa, dosya işlem boyunca hiç değişmemiş demektir.
        if context.original_hash == self.hashing_strategy.hash_file(context.source_path):
            context.integrity_ok = True
        else:
            context.integrity_ok = False

        # Aşama 2'nin ürettiği üç bilgi de sidecar dosyasına eklenir.
        # Aşama 1'de yazılan original_hash silinmez, üstüne eklenir.
        self.sidecar_store.update(context.sidecar_path, {"npy_output_path": context.npy_output_path,
                                                         "png_output_path": context.png_output_path,
                                                         "integrity_ok": context.integrity_ok})