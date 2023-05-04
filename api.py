import requests
from requests import Session
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
def getMasjidTerdekat(x,y):
    url = 'https://pusaka.kemenag.go.id/public/agama/islam/tempat_ibadah/data_masjid?page=1&rows=10&latitude={}&longitude={}'.format(x,y)
    response = requests.get(url)
    bs_content =bs(response.content,"html.parser")
    return bs_content
def getJadwalSholat(kota):
    jadwal='Tidak ditemukan jadwal sholat !'
    url = 'https://api.banghasan.com/sholat/format/json/kota/nama/'+kota
    response = requests.get(url)
    kotaid=json.loads(response.content)
    if kotaid['status']=="ok":
        new_today_date = datetime.today().strftime('%Y-%m-%d')
        url = 'https://api.banghasan.com/sholat/format/json/jadwal/kota/'+kotaid['kota'][0]['id']+'/tanggal/'+new_today_date
        response = requests.get(url)
        dtjdwl=json.loads(response.content)
        if dtjdwl['status']=="ok":
            jadwal='⏰ Jadwal Sholat Tanggal *'+kota.upper()+'*\n\n📆 Hari ini,*'+dtjdwl['jadwal']['data']['tanggal']+'*\n├ Imsak :'+dtjdwl['jadwal']['data']['imsak']+'\n├ Subuh :'+dtjdwl['jadwal']['data']['subuh']+'\n├ Terbit :'+dtjdwl['jadwal']['data']['terbit']+'\n├ Dhuha :'+dtjdwl['jadwal']['data']['dhuha']+'\n├ Dzuhur :'+dtjdwl['jadwal']['data']['dzuhur']+'\n├ Ashar :'+dtjdwl['jadwal']['data']['ashar']+'\n├ Maghrib :'+dtjdwl['jadwal']['data']['maghrib']+'\n├ Isya :'+dtjdwl['jadwal']['data']['isya']
    return jadwal
def getWeather():
    if request.method == 'POST':
        city = request.form['city']
    else:
        # for default name mathura
        city = 'mathura'
  
    # your API key will come here
    api = api_key_here
  
    # source contain json data from api
    source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q =' + city + '&appid =' + api).read()
  
    # converting JSON data to a dictionary
    list_of_data = json.loads(source)
  
    # data for variable list_of_data
    data = {
        "country_code": str(list_of_data['sys']['country']),
        "coordinate": str(list_of_data['coord']['lon']) + ' ' 
                    + str(list_of_data['coord']['lat']),
        "temp": str(list_of_data['main']['temp']) + 'k',
        "pressure": str(list_of_data['main']['pressure']),
        "humidity": str(list_of_data['main']['humidity']),
    }
    #print(data)
    return render_template('index.html', data = data)
def getPorsiHaji(no):
    dtporsi='Informasi Nomor Porsi Haji '+no+'*, tidak kami temukan informasinya..'
    return dtporsi