# Get Webtoon Image
If you want to use the webtoon data, run 'get_actual_toon_data.py'
## Prerequisites
It needs to download driver.exe.
If you use the chrome, you might use chromedriver.exe.
In this here, you can download chromedriver with your same chrome version.

    pip install selenium
    pip install opencv-python
    pip install natsort
    pip install pillow

## Customization
### Chrome Driver:
https://chromedriver.chromium.org/downloads 에서 크롬 드라이버를 다운 받는다.
이때 버전은 본인의 크롬 버전과 동일한 버전을 다운받아야 한다. (크롬 우측 상단의 더보기->도움말->Chrome 정보에서 확인 가능)
아래와 같은 19번째 줄 코드에서 설치된 크롬드라이버의 경로를 넣어준다. 

    driver = webdriver.Chrome(r"c:\Users박정은\chromedriver.exe")
    
해당 부분에서 오류가 날 경우 https://emessell.tistory.com/148 를 참고하거나 크롬 드라이버를 get_actual_toon_data.py 파일과 같은 디렉토리에 위치하도록 하여 해결한다.
### Episode: 
225번째, 227번째, 229번째 코드의 default값 수정
ex) 1화~100화 추출한다면 start는 100화, end는 1화
- 225번째 코드: default = ‘100화 링크’
- 227번째 코드: default = ‘1화 제목’
- 229번째 코드: default = 100
### Image size: 
아래와 같은 181번째 줄 코드에서 512가 이미지의 가로, 세로 크기(정사각형)

    scale = cv2.resize(dst,(512,512),interpolation=cv2.INTER_LINEAR)

## Run

    python get_actual_toon_data.py

## Output Directory
- actual(원래 크기의 이미지)
- crop(지정한 크기에 맞춰 자른 이미지)

## File Name
EpisodeNumber_CutNumber.png
