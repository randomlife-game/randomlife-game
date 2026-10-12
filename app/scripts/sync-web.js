// 저장소 루트의 index.html을 앱용 www/ 로 복사한다. 게임 코드는 여기서 고치지 않는다.
const fs = require("fs"), path = require("path");
const root = path.join(__dirname, "..", "..");
const www = path.join(__dirname, "..", "www");
fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(www, { recursive: true });
fs.copyFileSync(path.join(root, "index.html"), path.join(www, "index.html"));
console.log("www/index.html 갱신됨");
