# sketchKeras
An u-net with some algorithm to take the sketch from a painting.

# download mod
see release
(우측의 release 탭에서 mod.h5 파일을 다운 받아 소스 코드와 동일한 디렉토리에 저장해주세요)

# image size
- 이미지를 읽어 256 * 256 크기로 resize 해, 256 * 256 크기로 최종 이미지가 생성됩니다.
- 원본 사진이 1:1이 아닌 경우에는 사진이 눌린 상태로 생성이 됩니다.
- main.py의 line 15~17에서 생성 이미지의 크기를 수정할 수 있습니다.

# directory
- 생성되는 파일의 이름은 원본 파일의 이름과 동일합니다.
- directory 이름은 명령어 인자로 원본 폴더, 결과 폴더 순으로 입력하면 됩니다. 명령 인자를 입력하지 않을 경우, toon 폴더에서 모든 이미지를 받아와 sketch 폴더에 저장되도록 작성되어있습니다.
  (*결과 이미지가 저장되는 폴더를 빈 폴더이더라도 미리 생성해두어야 정상 작동합니다.*)
  
# run
  ```
  python main.py {원본파일디렉토리명} {결과파일디렉토리명}
  ```
  또는 
   ```
  python main.py
  ```
  
  ex) toon -> sketch
  ```
  python main.py ./toon ./sketch
  ```
# error
"Could not load dynamic library 'cudart64_110.dll'~" 과 같은 에러 메시지가 뜨면 아래 링크에서 NVIDIA CUDA 설치를 해주세요
https://ghostweb.tistory.com/839
