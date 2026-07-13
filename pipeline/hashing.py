"""
Dosya orjinalliğini doğrulamak için kullanılan hash stratejileri.

Bir dosyanın bayt içeriğinden özeti üretmek için gereken
sınıfları tanımlar. Yeni bir hash algoritması eklemek istendiğinde mevcut
kodun hiçbiri değişmez: 

- Yeni bir HashingStrategy alt sınıfı yazılır
- HashAlgorithm içersine typo için algoritma eklenir
- _REGISTRY sözlüğüne bir satır eklenir.
"""

import hashlib
from abc import abstractmethod, ABC
from enum import Enum

class HashAlgorithm(Enum):
    """
    Desteklenen hash algoritmalarının sabit listesi.

    Elle string yazmak yerine bu sabitlerin kullanılması yazım hatalarını
    engeller ve `_REGISTRY`'nin anahtarlarını tek bir yerde toplar.
    """

    SHA256 = "sha256"

# Soyut sınıf tanımlaması, bütün hashleme algoritmaları sınıftan türetilir.
# Yeni bir algoritma eklenmek istediğinde kalıtım al, _REGISTRY'e ekle.
class HashingStrategy(ABC):
    """
    Hash stratejileri için soyut sözleşme.

    Bu sınıfın kendisi örneklenemez. Sadece alt sınıfların uyması gereken
    kuralı tanımlar. Orjinallik kontrolü hangi somut strateji kullanıldığını 
    bilmeden, sadece bu sözleşmeye güvenerek çalışır.
    """

    @abstractmethod
    def hash_file(self, path) -> str:
        """Verilen yoldaki dosyanın hash'ini hesaplar.

        Args:
            path: Hash'i hesaplanacak dosyanın yolu.

        Returns:
            Dosyanın bayt içeriğinden üretilen hash, onaltılık (hex) bir
            string olarak.
        """
        pass

class Sha256Strategy(HashingStrategy):
    """`HashingStrategy` sözleşmesini SHA-256 algoritmasıyla dolduran sınıf."""

    def hash_file(self, path: str) -> str:
        # Dosya binary modda açılır 
        # hash fonksiyonu ham bitelar üzerinde çalışır.
        with open(path, "rb") as file:
            image_bytes = file.read()                             # Biteları okunabilir formatta al
            hashed_image = hashlib.sha256(image_bytes)            # Okunabilir biteları hashle
            hashed_string = hashed_image.hexdigest()              # Hashlenmiş formatı okunabilir hale getir

            return hashed_string


# Hangi HashAlgorithm değerinin hangi somut HashingStrategy sınıfına karşılık
# geldiğini tutar. Yeni bir algoritma eklerken tek değişiklik burasıdır.
_REGISTRY = {
    HashAlgorithm.SHA256 : Sha256Strategy
}

def create_hash_strategy(algorithm: HashAlgorithm):
    """Verilen algoritmaya karşılık gelen HashingStrategy örneğini üretir.

    Args:
        algorithm: Kullanılacak hash algoritmasını belirten HashAlgorithm üyesi.

    Returns:
        `_REGISTRY`'de o algoritmaya karşılık gelen sınıfın yeni bir örneği.
    """
    return _REGISTRY[algorithm]()
