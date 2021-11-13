## Preprocessing

Preprocessing은 다음과 같은 4단계로 이루어집니다.

1. Web crawling : **서버에서 작동 불가능**
2. Cut to 512x512 images
3. Convert images to sketch
4. Resize the original and sketch if its size is not 512
5. Trapped-ball segmentation
6. Extract Region from segmentation and make subtract layer

서버에 크롬을 깔 수 없어서 sudo가 안 되는 컴공과 교육서버에서 바로 1을 쓰지는 못하는데, 2~6은 확실히 로컬보다 서버가 성능이 좋습니다. 빨리 걸리기도 하고, 로컬 용량 및 서버 업로드에 걸리는 시간적/공간적 오버헤드도 줄일 수 있습니다.

로컬에서 크롤링만 하고 서버에 올린 후 전처리를 하는 것도 괜찮으나 코드를 조금 고쳐야 하긴 합니다.

따라서 서버에서 크롤링하는 것을 직접 하는 게 아니라 다른 서버를 이용하는 등 우회법을 이용해서 서버에서 한번에 끝내는 방법을 생각하면 좋을 것 같습니다.
암튼 이렇게 하면 안정적으로 모델에 맞는 원하는 크기의 전처리 데이터를 생성할 수 있습니다.

근데 오래 걸려요 ㅠㅠㅠ



### Prequisites

1. 우선, ./preprocess 디렉토리로 가서

```
pip install -r requirements.txt 
```

2. ChromeDriver 설치 후 get_actual_toon_data.py에서 19번째 줄 수정. 이 때 ChromeDriver는 본인 크롬 버전과 일치해야 합니다.

   https://chromedriver.chromium.org/downloads 에서 크롬 드라이버를 다운 받는다. 이때 버전은 본인의 크롬 버전과 동일한 버전을 다운받아야 한다. (크롬 우측 상단의 더보기->도움말->Chrome 정보에서 확인 가능) 아래와 같은 19번째 줄 코드에서 설치된 크롬드라이버의 경로를 넣어준다.

   ```
   driver = webdriver.Chrome(r"c:\Users박정은\chromedriver.exe")
   ```

   해당 부분에서 오류가 날 경우 https://emessell.tistory.com/148 를 참고하거나 크롬 드라이버를 get_actual_toon_data.py 파일과 같은 디렉토리에 위치하도록 하여 해결한다.

3. mod.h5 설치

   https://github.com/Stonerdk/2021UGRP_SGRU/releases/download/v0.1/mod.h5

   위 파일을 다운로드 받아 preprocess와 같은 폴더에 넣는다.



### Methods

우선, 한 번에 로컬에서 크롤링 후 전처리까지 모두 해 주는 모듈 full_preprocessing.py를 실행합니다. 
그 전에 디렉토리는 preprocess로 이동해야 합니다.

```
python full_preprocessing.py --output_dir <아웃풋> --start_url <시작 웹툰 URL(가장 회차 수가 낮은)> --episode_num <반복할 횟수> --size <이미지 사이즈>
```

**주의) 아웃풋 --output_dir은 반드시 영어여야 합니다. "./연애혁명" 이런 식으로 할 시 중간에 오류가 납니다.**



```
python full_preprocessing.py --output_dir 'LR224' --start_url 'https://comic.naver.com/webtoon/detail?titleId=570503&no=320&weekday=thu' --episode_cnt 5 --size 224
```

예를 들어, preprocess/에서 경우 연애혁명에서 URL 기준으로 320화 (실제로는 320화가 아닐 수 있음)로부터 5화동안, 즉 320~324화 동안의 이미지를 모두 크롤링하여 224*224 크기로 전처리합니다.

이렇게 하면 './LR224' (LR은 Love Revolution의 줄임말입니다.)에 roughcut, crawling, original, segmented, segmented_color, segmented_sub, sketch 의 7가지 하위 폴더가 생기며, 프리프로세싱이 끝난 후 여기에 모든 데이터가 저장됩니다. 

(모든 작업이 끝나면 roughcut, crawling은 아마 빈 폴더이거나 없을 것입니다.)