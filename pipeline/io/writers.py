"""
Küçültülmüş piksel matrisini diske yazan yazıcılar.

Sonuç iki farklı formatta yazılır: 
- `.npy` ML modeline verilecek ham matris 
- `.png` kayıpsız, görsel doğrulama için.
"""

from abc import abstractmethod, ABC
import numpy as np
from PIL import Image

# --- Soyut Sınıf ---

class OutputWriter(ABC):
    """Çıktı yazıcıları için soyut sınıf."""

    @abstractmethod
    def write(self, matrix: np.array, base_path: str) -> str:
        """Piksel matrisi diske yazılır.

        Args:
            matrix: Yazılacak piksel matrisi.
            base_path: Uzantısız temel dosya yolu, örneğin "output/image".
                Uzantı, hangi somut sınıf kullanılıyorsa onun tarafından eklenir.

        Returns:
            Dosyanın gerçekten yazıldığı tam uznatılı yol.
        """
        pass

# --- Somut stratejiler ---

class NpyWriter(OutputWriter):
    """`OutputWriter` soyut sınıfını, `.npy` formatına yazarak dolduran sınıf."""

    def write(self, matrix: np.array, base_path: str) -> str:
        # np.save zaten .npy ile bitmeyen isimlere uzantıyı kendisi ekliyor,
        # ama burada elle eklenir ki dönen yol, gerçekte
        # yazılan dosyayla birebir aynı olsun.
        if not base_path.endswith(".npy"):
            base_path += ".npy"

        np.save(base_path, matrix)
        return base_path

class PngWriter(OutputWriter):
    """`OutputWriter` soyut sınıfını, `.png` formatına yazarak dolduran sınıf."""

    def write(self, matrix: np.array, base_path: str) -> str:
        # Image.fromarray, numpy dizisini bir Image nesnesine çevirir;
        # uint8'e çevirmek ve mode="RGB" vermek ile, matrisin her zaman
        # 0-255 aralığında 3 renk kanallı olarak yorumlanması garanti edilir.
        img = Image.fromarray(matrix.astype(np.uint8), mode="RGB")

        # Pillow, .save() çağrısında formatı dosya uzantısından anlar;
        # uzantı yoksa hata verir, bu yüzden burada elle ekleniyor.
        if not base_path.endswith(".png"):
            base_path += ".png"
        img.save(base_path)
        return base_path
            