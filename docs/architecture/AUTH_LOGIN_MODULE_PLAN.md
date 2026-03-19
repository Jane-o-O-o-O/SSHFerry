# SSHFerry Auth Login Module Plan

## Purpose

杩欎唤鏂囨。涓撻棬瀹氫箟閮ㄧ讲鐗?SSHFerry 鐨勭櫥褰曚笌閴存潈妯″潡銆?
鐜版湁浠撳簱閲岀殑璁よ瘉鏂瑰紡浠嶇劧鏄€滄湰鍦板悗绔惎鍔ㄥ悗杩斿洖涓€涓唴瀛?token锛屽墠绔妸瀹冨杩涜姹傚ご鈥濄€傝繖濂楁満鍒跺彧閫傚悎鏈満寮€鍙戯紝涓嶉€傚悎閮ㄧ讲鍒扮綉椤典笂鐨勬寮忔湇鍔°€?
鍥犳锛岀櫥褰曟ā鍧楀繀椤讳粠绗竴鏈熺殑鈥滈檮鍔犻」鈥濇彁鍗囦负涓昏矾寰勮兘鍔涖€?
## Why Current Auth Is Not Enough

褰撳墠妯″瀷鐨勪富瑕侀棶棰橈細

- `GET /api/auth/session` 杩斿洖鏈湴 token锛屽彧閫傚悎 `127.0.0.1` 鏈満鍓嶅悗绔€?- 鍓嶇 `useBackendSession()` 渚濊禆鍚姩鍚庣洿鎺ユ嬁 token锛屼笉瀛樺湪鐪熸鐧诲綍鎬併€?- 娌℃湁鐢ㄦ埛韬唤姒傚康锛屽氨鏃犳硶鍋氬伐浣滃尯闅旂銆佺珯鐐归殧绂汇€佸璁″拰鏉冮檺鎺у埗銆?- WebSocket 浠嶆部鐢?query token 妯″紡锛岄儴缃插悗椋庨櫓鍋忛珮銆?- 濡傛灉绯荤粺閮ㄧ讲鍒板叕缃戞垨鍐呯綉鍏变韩鐜锛屼换浣曟嬁鍒?token 鐨勪汉閮借兘鐩存帴鎿嶄綔鍏ㄩ儴 SSH 璧勬簮銆?
## Reference Template Summary

宸插弬鑰?`E:\full_stack_template` 鐨勮璇佸疄鐜帮紝閲嶇偣鍏虫敞鐨勬槸瀹冪殑鈥滃畨鍏ㄦ祦绋嬧€濓紝鑰屼笉鏄〉闈㈡牱寮忋€?
閲嶇偣鍙傝€冩ā鍧楋細

- `backend/app/auth/login/login_handler.py`
- `backend/app/auth/login/login_service.py`
- `backend/app/auth/token_logic/token_cookie_handler.py`
- `backend/app/auth/token_logic/jwt_service.py`
- `backend/app/auth/refresh_token_logic/refresh_token_service.py`
- `backend/app/auth/refresh_token_logic/refresh_token_handler.py`
- `backend/app/auth/current_user/current_user_handler.py`
- `backend/app/auth/security/login_protection_service.py`
- `backend/app/auth/security/rate_limiter_service.py`
- `frontend/src/api/axiosInstance.ts`
- `frontend/src/api/auth_api.ts`
- `frontend/src/auth/ProtectedRoute.tsx`

## What To Reuse From The Template

妯℃澘閲屽€煎緱鍊熼壌鐨勭偣锛?
1. 鐧诲綍鎴愬姛鍚庝笉鎶?access token 鏆撮湶缁欏墠绔姸鎬侊紝鑰屾槸浼樺厛鏀捐繘 HTTP-only cookie銆?2. 閲囩敤 `access token + refresh token` 鍙?token 妯″瀷锛岃€屼笉鏄崟涓€闀挎湡 token銆?3. 鎻愪緵 `GET /auth/me` 浣滀负鍓嶇鍚姩鍚庣殑鐪熷疄鐧诲綍鎬佸垽鏂帴鍙ｃ€?4. 鎻愪緵 refresh token 杞崲涓庡悐閿€鑳藉姏锛岃€屼笉鏄鏃?token 涓€鐩存湁鏁堛€?5. 瀵圭櫥褰曞拰 refresh 鍋氶檺娴佷笌澶辫触閿佸畾淇濇姢銆?6. 鍓嶇閫氳繃璺敱瀹堝崼鍒ゆ柇鏄惁宸茬櫥褰曪紝鑰屼笉鏄亣璁惧簲鐢ㄤ竴鎵撳紑灏辨湁鏉冮檺銆?
## What Not To Copy From The Template

妯℃澘閲岃繖浜涢儴鍒嗕笉搴旂洿鎺ユ惉杩?SSHFerry锛?
- Chakra UI 椤甸潰鏍峰紡
- 妯℃澘榛樿鐨勯€氱敤 SaaS 椋庢牸甯冨眬
- Redux 璁よ瘉鍒囩墖缁勭粐鏂瑰紡
- 鍏叡娉ㄥ唽 `signup` 浣滀负绗竴鏈熼粯璁ゅ叆鍙?- Google OAuth2 浣滀负绗竴鏈熼粯璁ゅ叆鍙?- 瀵嗙爜鎵惧洖銆侀偖绠遍獙璇佺瓑瀹屾暣璐﹀彿浣撶郴浣滀负绗竴鏈熷繀鍋氶」

鍘熷洜锛?
- SSHFerry 鐜板湪鏇村儚鍐呴儴杩愮淮/浼犺緭宸ヤ綔鍙帮紝涓嶆槸闈㈠悜鍏紑鐢ㄦ埛鐨勬敞鍐屽瀷浜у搧銆?- 褰撳墠鍓嶇鎶€鏈爤鍜岃瑙夎瑷€宸茬粡褰㈡垚锛屽簲缁х画浣跨敤鐜版湁 React + Zustand + TanStack Query + `tokens.css`銆?- 鎴戜滑闇€瑕佸鐢ㄧ殑鏄璇佹満鍒讹紝涓嶆槸妯℃澘 UI銆?
## SSHFerry Auth Decisions

### 1. Deployment Assumption

閮ㄧ讲鐗堥粯璁ら噰鐢ㄢ€滃悓鍩熼儴缃测€濇柟妗堬細

- 鍓嶇椤甸潰鍜屽悗绔?API 灏介噺璧板悓涓€涓诲煙
- 娴忚鍣ㄩ€氳繃瀹夊叏 cookie 鎸佹湁鐧诲綍鎬?- 閬垮厤璺ㄥ煙涓?`localStorage token` 鍜屽鏉傚墠绔寔涔呭寲

杩欎篃鏄渶閫傚悎 SSHFerry 鐨勬柟妗堬紝鍥犱负瀹冩棦鍑忓皯娉勯湶闈紝涔熺畝鍖栧墠绔帴鍏ャ€?
### 2. Token Strategy

寤鸿閲囩敤锛?
- 鐭湡 `access token`
- 闀挎湡 `refresh token`
- 涓よ€呴兘閫氳繃 `HttpOnly + Secure` cookie 涓嬪彂

寤鸿榛樿鍊硷細

- access token锛?5 鍒嗛挓
- refresh token锛? 澶╁埌 14 澶?
寤鸿 cookie 灞炴€э細

- `HttpOnly=true`
- `Secure=true`
- `SameSite=Lax`

濡傛灉鍚庣画寮曞叆璺ㄧ珯 OAuth 鍥炶皟锛屽啀璇勪及鏄惁闇€瑕佸崟鐙皟鏁?SameSite 绛栫暐锛涚涓€鏈熶笉闇€瑕佷负浜嗘湭鏉ュ亣璁炬妸榛樿瀹夊叏杈圭晫鏀炬澗銆?
### 3. User Model

鎺ㄨ崘鐨勮鑹查鐣欙細

- `owner`锛氱郴缁熸墍鏈夎€咃紝鍙鐞嗙敤鎴枫€佺珯鐐广€佺郴缁熼厤缃?- `operator`锛氬彲鎿嶄綔宸ヤ綔鍖恒€佺珯鐐硅繛鎺ャ€佷换鍔′紶杈?- `viewer`锛氬彧璇绘煡鐪嬩换鍔°€佹椿鍔ㄦ祦銆侀儴鍒嗚祫婧?
绗竴鏈熷彲浠ュ厛鍙氦浠樺崟涓?`owner` 璐﹀彿锛屼絾鍚庣鏁版嵁缁撴瀯鍜?`GET /api/auth/me` 杩斿洖鍊奸噷搴旈鐣?`role` 瀛楁锛岄伩鍏嶅悗缁噸鍋氥€?

## Recommended API Contract

绗竴鏈熷缓璁彁渚涜繖浜涙帴鍙ｏ細

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `POST /api/auth/logout/all` 鍙€?
寤鸿澧炲姞涓€涓垵濮嬪寲鑳藉姏锛屼絾涓嶈鍋氭垚姘歌繙鏆撮湶鐨勫叕寮€娉ㄥ唽鍏ュ彛锛?
- CLI锛歚sshferry bootstrap-owner`
- 鎴栦粎棣栨閮ㄧ讲鍙敤鐨勫彈鎺у垵濮嬪寲鎺ュ彛

涓嶅缓璁涓€鏈熺洿鎺ュ紑鏀撅細

- `POST /api/auth/signup`
- `GET /api/auth/oauth2/*`
- `POST /api/auth/password-reset/*`

## Backend Flow

鎺ㄨ崘娴佺▼濡備笅锛?
### Login

1. 鐢ㄦ埛鍦?`/login` 鎻愪氦璐﹀彿瀵嗙爜銆?2. 鍚庣鏍￠獙璐﹀彿銆佸瘑鐮併€侀攣瀹氱姸鎬併€?3. 鍚庣鐢熸垚 access token 鍜?refresh token銆?4. 鍚庣鎶婁袱涓?token 鍐欏叆 HTTP-only cookie銆?5. 鍓嶇涓嶄繚瀛樺師濮?token锛屽彧璇锋眰 `GET /api/auth/me` 鑾峰彇褰撳墠鐢ㄦ埛銆?
### App Bootstrap

1. 椤甸潰鍚姩鍏堣姹?`GET /api/health`銆?2. 鍐嶈姹?`GET /api/auth/me`銆?3. 鑻ヨ繑鍥?`200`锛岃繘鍏ュ簲鐢ㄣ€?4. 鑻ヨ繑鍥?`401`锛岃烦杞埌 `/login`銆?
### Silent Refresh

1. 涓氬姟鎺ュ彛杩斿洖 `401` 鏃讹紝鍓嶇鍙仛涓€娆￠潤榛?refresh 灏濊瘯銆?2. 璋冪敤 `POST /api/auth/refresh`銆?3. refresh 鎴愬姛鍒欓噸璇曞師璇锋眰涓€娆°€?4. refresh 澶辫触鍒欐竻绌哄墠绔璇佺姸鎬佸苟璺宠浆 `/login`銆?
### Logout

1. 鐢ㄦ埛鐐瑰嚮閫€鍑恒€?2. 鍓嶇璋冪敤 `POST /api/auth/logout`銆?3. 鍚庣鍚婇攢 refresh token锛屽苟娓呯┖ access/refresh cookies銆?4. 鍓嶇璺冲洖 `/login`銆?
## WebSocket Auth

SSHFerry 鏈変换鍔″拰娲诲姩娴?websocket锛屽洜姝ょ櫥褰曟ā鍧楀繀椤昏鐩?websocket銆?
鎺ㄨ崘绛栫暐锛?
- 绗竴闃舵锛氬悓鍩熼儴缃蹭笅鐩存帴澶嶇敤 cookie 鐧诲綍鎬?- 濡傚弽鍚戜唬鐞嗘垨娴忚鍣ㄥ吋瀹规€у瓨鍦ㄩ棶棰橈紝鍐嶈ˉ涓€涓煭鏃?`ws_ticket`

涓嶅缓璁户缁妸闀挎湡 token 鏆撮湶鍦?websocket query string 涓綔涓轰富鏂规銆?
## Data Ownership Boundaries

鐧诲綍妯″潡钀藉湴鍚庯紝杩欎簺瀵硅薄閮藉繀椤荤粦瀹氱敤鎴疯韩浠斤細

- 涓婁紶宸ヤ綔鍖?- 绔欑偣閰嶇疆
- SSH 浼氳瘽涓婁笅鏂?- 浠诲姟鍒楄〃
- 娲诲姩娴?
鏈€灏戣姹傦細

- 宸ヤ綔鍖虹洰褰曟寜鐢ㄦ埛闅旂锛屼緥濡?`workspace/{user_id}/...`
- `GET /api/sessions` 鍙兘杩斿洖褰撳墠鐢ㄦ埛鐨?session
- `GET /api/tasks` 榛樿鍙繑鍥炲綋鍓嶇敤鎴风浉鍏充换鍔?- `GET /api/activity` 榛樿鍙繑鍥炲綋鍓嶇敤鎴峰彲瑙佷簨浠?
濡傛灉鍚庣画鏀寔鍏变韩绔欑偣锛屼篃搴旈€氳繃鏄庣‘ ACL锛岃€屼笉鏄粯璁ゆ墍鏈変汉鍏变韩涓€濂楃珯鐐广€?
## Secret Handling Requirements

鐧诲綍妯″潡涓€鏃﹀紩鍏ョ敤鎴蜂綋绯伙紝绔欑偣鏁忔劅鏁版嵁鐨勫鐞嗗氨蹇呴』涓€璧峰崌绾с€?
蹇呴』琛ュ厖锛?
- 淇濆瓨鐨?SSH 瀵嗙爜鍔犲瘑瀛樺偍
- 绉侀挜鍙ｄ护鍔犲瘑瀛樺偍
- 鍒锋柊 token 鍙瓨鍦ㄥ悗绔彲鎺у瓨鍌紝涓嶈繘鍏ュ墠绔湰鍦版寔涔呭寲
- 娲诲姩娴佸拰鏃ュ織閲岀姝㈡墦鍗版槑鏂囧瘑鐮併€佺閽ュ唴瀹广€乺efresh token

寤鸿锛?
- 鍗曞疄渚嬮儴缃插彲鐢ㄦ湇鍔＄涓诲瘑閽ュ姞瀵?- 鐢熶骇閮ㄧ讲浼樺厛鑰冭檻澶栭儴 secret manager 鎴栬嚦灏戠幆澧冩敞鍏ヤ富瀵嗛挜

褰撳墠鏈€灏忓疄鐜拌鏄庯細

- 宸插疄鐜扮珯鐐瑰瘑鐮佷笌绉侀挜鍙ｄ护鐨勯潤鎬佸姞瀵嗗瓨鍌?- 閮ㄧ讲鐗堥€氳繃 `SSHFERRY_SITE_SECRET` 鎻愪緵鏈嶅姟绔富瀵嗛挜
- `local-dev` 鍏佽鐢熸垚瀹炰緥鏈湴 `.site_store.key` 浣滀负寮€鍙戜究鍒╁洖閫€锛屼笉浣滀负姝ｅ紡閮ㄧ讲鏂规
- 绔欑偣缂栬緫鏃惰嫢瀵嗙爜鎴栫閽ュ彛浠ゅ瓧娈电暀绌猴紝浼氫繚鐣欏師鏈夊凡淇濆瓨瀵嗘枃锛屼笉浼氳娓呯┖

## Audit And Security Events

寤鸿鎶婁互涓嬩簨浠剁撼鍏ュ璁℃垨娲诲姩娴侊細

- 鐧诲綍鎴愬姛
- 鐧诲綍澶辫触
- 璐﹀彿閿佸畾
- refresh 鎴愬姛 / 澶辫触
- 鎵嬪姩閫€鍑?- 鍏ㄧ閫€鍑?- 绔欑偣鍒涘缓 / 淇敼 / 鍒犻櫎
- 杩滅 session 鎵撳紑 / 鍏抽棴
- 浠诲姟鍒涘缓 / 澶辫触 / 鍙栨秷

杩欐牱鈥滅櫥褰曟ā鍧椻€濆拰鈥滄椿鍔ㄦ祦鏇挎崲鍘熷鏃ュ織鈥濅袱浠朵簨灏辫兘鐩存帴鎵撻€氥€?
## Frontend Integration Rules

妯℃澘閲岀敤浜?`axios + withCredentials + /auth/me + ProtectedRoute`锛岃繖浜涙€濊矾鍙互鐩存帴鍊燂紝浣嗗疄鐜板簲淇濇寔 SSHFerry 褰撳墠鏍堬細

- 淇濈暀 `axios` 璇锋眰灞?- 淇濈暀 Zustand 浣滀负鍏ㄥ眬浼氳瘽鐘舵€?- 淇濈暀 React Router 璺敱缁撴瀯
- 淇濈暀鐜版湁椤甸潰楠ㄦ灦鍜岃瑙夊彉閲?
鍓嶇闇€瑕佹柊澧炴垨閲嶆瀯锛?
- `/login` 璺敱
- 鍙椾繚鎶よ矾鐢卞畧鍗?- `useBackendSession()` 鏀归€犳垚 `useAuthBootstrap()`
- `http` 鎷︽埅鍣ㄥ鍔?refresh 閲嶈瘯閫昏緫
- 鐢ㄦ埛璧勬枡鐘舵€侊紝渚嬪 `user`, `role`, `isAuthenticated`

## UI Constraints

鐧诲綍椤靛彧鍙傝€冩ā鏉跨殑浜や簰娴佺▼锛屼笉鍙傝€冩ā鏉跨殑瑙嗚灞傘€?
SSHferry 鐧诲綍椤靛繀椤婚伒寰幇鏈夌珯鐐归鏍硷細

- 浣跨敤褰撳墠鏆栫伆搴曡壊鍜岃摑闈掑己璋冭壊
- 浣跨敤 `IBM Plex Sans` / `IBM Plex Mono`
- 寤剁画 `bootstrap-panel`銆乣panel-shell` 杩欑被娌夌ǔ宸ュ叿鎰熷鍣?- 涓嶄娇鐢ㄦā鏉块噷鐨?Chakra 榛樿鍗＄墖鍜岄€氱敤 SaaS 娆㈣繋椤垫牱寮?
绗竴鏈熺櫥褰曢〉寤鸿鍙繚鐣欙細

- 璐﹀彿杈撳叆
- 瀵嗙爜杈撳叆
- 鐧诲綍鎸夐挳
- 鐧诲綍閿欒鎻愮ず
- 浼氳瘽杩囨湡鎻愮ず

绗竴鏈熶笉寤鸿榛樿鍑虹幇锛?
- 鍏叡娉ㄥ唽鍏ュ彛
- OAuth2 鐧诲綍鎸夐挳
- 蹇樿瀵嗙爜鍏ュ彛

## Extra Global Changes Needed

浠庡叏灞€鐪嬶紝闄や簡鈥滃姞鐧诲綍椤碘€濅箣澶栵紝杩樺繀椤诲悓鏃惰ˉ杩欏嚑浠朵簨锛屾墠鑳介伩鍏嶅悗闈㈣繑宸ワ細

1. 绔欑偣鍑嵁浠庘€滄湰鍦伴厤缃€濈淮鈥濆崌绾т负鈥滄湇鍔＄鏁忔劅璧勬簮绠＄悊鈥濄€?2. 鎵€鏈夊伐浣滃尯銆乻ession銆佷换鍔℃帴鍙ｉ兘瑕佸甫鐢ㄦ埛褰掑睘杈圭晫銆?3. 鍘熷鏃ュ織鎺ュ彛榛樿涓嶅啀瀵规櫘閫氱櫥褰曠敤鎴峰紑鏀俱€?4. 闇€瑕佹湁棣栦釜绠＄悊鍛樺垵濮嬪寲鏂规锛岃€屼笉鏄紑鏀炬敞鍐屻€?5. 闇€瑕佸湪閮ㄧ讲鏂囨。閲屾槑纭?Redis 鏄惁浣滀负 refresh / 闄愭祦 / 閿佸畾鐨勬帹鑽愪緷璧栥€?

## Phase 1 Scope For Auth

绗竴鏈熷繀椤昏惤鍦帮細

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- 鐧诲綍闄愭祦
- 鐧诲綍澶辫触閿佸畾
- 鍙椾繚鎶よ矾鐢?- cookie 閴存潈鐨?websocket 鎺ュ叆
- 鍗曚釜 `owner` 璐﹀彿鍒濆鍖栬兘鍔?
绗竴鏈熷缓璁鐣欎絾鍙悗缃細

- `POST /api/auth/logout/all`
- 澶氳鑹叉潈闄愮煩闃?- 绠＄悊鍛樼敤鎴风鐞嗛〉闈?
绗竴鏈熶笉鍋氾細

- 鍏叡娉ㄥ唽
- OAuth2
- 瀵嗙爜鎵惧洖
- 閭楠岃瘉

## Implementation Notes Relative To The Template

瀵?`full_stack_template` 鐨勫彇鑸嶅師鍒欙細

- 鍊熷悗绔璇佹祦绋嬶紝涓嶅€熷畠鐨?UI 椋庢牸銆?- 鍊?`withCredentials` 鍜?`/me` 鏍￠獙鎬濊矾锛屼笉鐓ф惉 Redux 缁撴瀯銆?- 鍊?refresh token rotation 鍜?revoke 鎬濊矾锛屼笉寮鸿鎶婃暣濂楁ā鏉垮熀纭€璁炬柦涓€娆℃€ф惉杩涙潵銆?- 鍊?rate limit / lockout 鏈哄埗锛屼絾 SSHFerry 鍙互鍏堟寜鍗曞疄渚嬮儴缃插仛鏇磋交閲忓疄鐜帮紝鍙鎺ュ彛杈圭晫鍒璁℃銆?
## Related Docs

閰嶅闃呰锛?
- [WEB_DEPLOYMENT_PLAN.md](./WEB_DEPLOYMENT_PLAN.md)
- [WEB_PHASE1_TASKLIST.md](./WEB_PHASE1_TASKLIST.md)
- [../frontend/Frontend-Design.md](../frontend/Frontend-Design.md)

杩欎唤鏂囨。鐨勪綔鐢ㄦ槸鎶娾€滅櫥褰曟ā鍧椻€濅粠涓€涓硾娉涚殑闇€姹傦紝鏀舵暃鎴?SSHFerry 閮ㄧ讲鐗堢殑姝ｅ紡鏋舵瀯绾︽潫銆?

## Current Milestone 1 Implementation Note

褰撳墠浠撳簱閲岀殑 Milestone 1 鏈€灏忓疄鐜伴噰鐢ㄤ互涓嬭惤鍦版柟寮忥細

- 鏂板 `SSHFERRY_RUNTIME_MODE`锛屽尯鍒?`local-dev` 涓?`deployed-web`
- `deployed-web` 閫氳繃 `SSHFERRY_OWNER_USERNAME` + `SSHFERRY_OWNER_PASSWORD` 鎴?`SSHFERRY_OWNER_PASSWORD_HASH` 鍒濆鍖栭涓?owner
- 棣栨鍚姩鏃?owner 浼氬啓鍏?`SSHFERRY_OWNER_FILE`锛岄粯璁よ矾寰勪负 `.backend_runtime/auth/owner.json`
- access token 涓虹煭鏈熺鍚?cookie锛宺efresh token 涓烘湇鍔＄鍙帶 session + HttpOnly cookie
- `local-dev` 涓轰簡淇濇寔鏈湴寮€鍙戞晥鐜囷紝`GET /api/auth/me` 浼氳嚜鍔ㄥ缓绔嬫湰鍦板紑鍙戜細璇濓紝浣嗗墠绔富鍚姩娴佷粛缁熶竴涓?`health -> me`
- websocket 宸叉敼涓轰紭鍏堝鐢?cookie 鐧诲綍鎬侊紝query token 鍙繚鐣?local-dev 鍏煎璺緞
