#Geotagx-twitter-sourcerer   
Collects images from the realtime global twitter feed based on some keywords that you supply, and pushes them to geotagx via geotagx-sourcerer-proxy   

#Usage   
```bash
git clone --recursive https://github.com/geotagx/geotagx-twitter-sourcerer.git
cd geotagx-twitter-sourcerer
pip install -r requirements.txt
cp settings.py.default settings.py
# Edit settings.py to setup the twitter keys, and the keywords that you want to use to filter the twitter stream
python geotagx-twitter-sourcerer.py 
```

#Author   
S.P. Mohanty <sp.mohanty@cern.ch>   
