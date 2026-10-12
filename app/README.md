# 랜덤인생 앱 (Capacitor)

게임 본체는 저장소 루트의 `index.html` 하나입니다. 이 폴더는 그것을 안드로이드·iOS 앱으로 감싸는 껍데기이며 게임 코드는 여기서 고치지 않습니다.

```
cd app
npm ci
npm run sync          # 루트 index.html -> www/ 복사 후 cap sync
npx cap open android  # Android Studio
npx cap open ios      # Xcode (맥 필요)
```

- 앱 ID: `com.randomlifegame.app` (스토어 등록 후에는 바꿀 수 없음)
- 안드로이드 디버그 APK는 GitHub Actions(`Android 앱 빌드`)가 만들어 줍니다.
- 서명 키(.jks)와 비밀번호는 절대 커밋하지 마세요.
