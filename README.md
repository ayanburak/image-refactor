# Image Refactor

Fotoğrafları bütünlük doğrulamasıyla birlikte, orijinal piksel değerlerine dokunmadan ML modellerine hazırlayan dönüştürme aracı.


## Kullanım

Proje, kendi sanal ortamı (`.venv`) içinden çalıştırılır. Bağımlılıklar bu ortama kurulu, sistem genelinde bir kuruluma ihtiyaç yoktur.

Kurulum:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Çalıştırma:

```bash
.venv/bin/python main.py <girdi> --target <hedef_boyut> --output <çıktı_klasörü>
```

Üç argüman kullanılır. `<girdi>`, ya tek bir görsel dosyasının ya da bir görsel klasörünün yoludur; klasör verilirse içindeki tüm alt klasörler de taranır. `--target` zorunludur ve iki şekilde verilebilir: yüzdelik bir oran, örneğin `25%`, ya da sabit bir genişlik x yükseklik değeri, örneğin `512x384`. `--output` zorunlu değildir, verilmezse `output` klasörü kullanılır; her çalıştırma bu klasörün altına kendi zaman damgalı alt klasörünü oluşturur, böylece farklı çalıştırmaların çıktıları birbirinin üzerine yazılmaz.

Desteklenen görsel uzantıları `.jpg`, `.jpeg`, `.heic` ve `.png`'dir.

Örnek kullanımlar:

```bash
.venv/bin/python main.py foto.jpg --target 25% --output output
.venv/bin/python main.py foto.jpg --target 512x384 --output output
.venv/bin/python main.py fotograflar/ --target 25% --output output
```

İşlenen her görsel için üç dosya üretilir: piksel matrisinin ham hâlini taşıyan bir `.npy` dosyası, aynı matrisin görsel olarak kontrol edilebilmesi için bir `.png` dosyası, ve dosyanın hash'ini, hedef çıktı yollarını ve bütünlük kontrolü sonucunu taşıyan bir `.sidecar.json` dosyası. Girdi bir klasörse, çıktı dosyaları da girdideki alt klasör yapısını koruyarak yazılır; bu sayede farklı alt klasörlerdeki aynı isimli iki dosya birbirinin çıktısının üzerine yazmaz.

Bir görselin işlenmesi sırasında hata oluşursa (bozulmuş bir dosya ya da desteklenmeyen bir format gibi), o görsel atlanır ve hata ekrana yazdırılır; toplu işlemin geri kalanı durmadan devam eder.

## Proje Hakkında

Bir makine öğrenmesi modeline fotoğraf verilirken, fotoğrafın orijinal çözünürlükte kalması genelde mümkün olmuyor; boyutunun küçültülmesi gerekiyor. Standart küçültme yöntemleri, komşu piksellerden ortalama alarak yeni bir değer hesaplar; bu, görüntüyü gözle fark edilemeyecek kadar az değiştirse de, piksel değerlerinin orijinal dosyadaki hâliyle birebir aynı kalmasını bozar.

Bu araç, küçültmeyi farklı bir yöntemle yapar: komşu piksellerden hiçbir ortalama almadan, belirli aralıklarla doğrudan orijinal pikselleri seçer, aradakileri atlar. Çıktıdaki her piksel, kaynak görselde birebir var olan bir pikseldir; hiçbir değer yeniden hesaplanmaz.

Bunun yanında araç, dosyanın işlem boyunca bozulmadığını da kanıtlar. Orijinal dosya işlenmeden önce hashlenir, işlem bittikten sonra tekrar hashlenir; iki hash karşılaştırılır ve sonucu her görsel için ayrı yazılan bir sidecar dosyasına kaydedilir. Orijinal dosyanın kendisi hiçbir aşamada değiştirilmez, sadece salt-okunur olarak açılır.

## Nasıl çalışır

Araç, her görseli iki aşamadan geçirir.

### Hashleme 

Bu aşamada üç şey yapılır. Önce, orijinal dosyanın tüm bayt içeriği SHA-256 ile hashlenir; bu hash, işlemin sonunda tekrar hesaplanıp karşılaştırılacak referans değerdir. Sonra, dosya Pillow ile açılır; telefonlar bir fotoğrafı çekerken sensörü fiziksel olarak döndürmediği, bunun yerine dosyanın metadata bilgisine hangi yönde gösterilmesi gerektiğini yazdığı için, bu yön bilgisi okunup uygulanır ve sonuç bir piksel matrisine çevrilir. Son olarak, elde edilen hash, henüz oluşturulmamışsa yeni bir sidecar json dosyasına yazılır.

### Dönüştürme

Bu aşama, birinci aşamanın ürettiği piksel matrisini alıp devam eder. Önce, komut satırından verilen hedef boyut metni (`25%` ya da `512x384` gibi) yorumlanır ve görselin gerçek orijinal boyutuna göre hedef genişlik ve yükseklik hesaplanır. Sonra küçültme yapılır: orijinal boyut hedef boyuta bölünerek bir adım değeri bulunur, ve matristen bu adımla atlanarak piksel seçilir; aradaki pikseller hiç okunmaz, hiçbir ortalama alınmaz. Küçültülmüş matris hem `.npy` hem `.png` formatında diske yazılır. Son olarak, orijinal dosya tekrar hashlenir ve ilk aşamadaki hash ile karşılaştırılır; bu karşılaştırmanın sonucu, çıktı dosyalarının yollarıyla birlikte sidecar dosyasına eklenir.

### Toplu işleme

Komut satırından verilen girdi tek bir dosya olabileceği gibi bir klasör de olabilir. Klasör verildiğinde, içindeki ve tüm alt klasörlerindeki desteklenen uzantılı dosyalar bulunur ve her biri yukarıdaki iki aşamadan sırayla geçirilir. Her çalıştırma, verilen çıktı klasörünün altında kendi timestampli alt klasörünü oluşturur; bu sayede farklı çalıştırmaların sonuçları birbirinin üzerine yazılmaz. Aynı isimli iki dosya farklı alt klasörlerden geliyorsa, çıktı yolları da bu alt klasör yapısını koruyarak hesaplanır; böylece ikisi de kendi yerine yazılır, biri diğerinin üzerine yazmaz. Bir dosyanın işlenmesi herhangi bir noktada başarısız olursa, hata ekrana yazdırılır, o dosya atlanır ve kalan dosyaların işlenmesine devam edilir.

### Sidecar dosyası

Her görsel için, kendisiyle aynı adı taşıyan bir `.sidecar.json` dosyası üretilir. Bu dosya, görselin kendisine hiç dokunmadan, onun hakkındaki bilgileri taşır: orijinal dosyanın hash'i, üretilen `.npy` ve `.png` dosyalarının yolları, ve bütünlük kontrolünün sonucu. Dosya, birinci aşama bitince kısmen, son aşama bitince tam olarak doldurulur; önceki aşamada yazılan bilgiler silinmez, üzerine yeni bilgiler eklenir.

### Genişletilebilirlik

Projedeki değişebilir her davranış, hash algoritması, hedef boyut hesaplama, küçültme yöntemi, çıktı formatı, soyut bir sınıf üzerinden tanımlanır kullanılan somut sınıflar bu soyut sınıfların sadece birer uygulamasıdır. Yeni bir hash algoritması ya da yeni bir çıktı formatı eklemek istendiğinde, yeni bir somut sınıf yazılır ve ilgili kayıt listesine eklenir; aşamaların, pipeline'ın ya da toplu işleme mantığının kodu hiç değişmez.
