# Nedir?
PDF halinde yayınlanan [UDIM](http://www.koeri.boun.edu.tr/sismo/ "Ulusal Deprem İzleme Merkezi") aylık bültenlerinden veri çıkarma, veritabanına kaydedip üzerinde sorgu yapabilmek için yazılmış bir araç seti.

# Sistem Gereksinimleri
 * Python 2.7
 * pypoppler (PDF'den veri çıkarmak için)
 * mongodb & pymongo (Veritabanı işlemleri için)

# Kullanım

  ` python extract.py bulten.pdf -s BASLANGIC_SAYFASI -e SON_SAYFA`

  `                               -t #parse işlemi için geçen zamanı hesapla`

  `                               -p #veriyi yaz`

  `                               -m MONGODB_DB_ADI`

  `                               -j JSON_DOSYA_ADI`

# Lisans
Rıdvan Örsvuran (C) 2012

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

