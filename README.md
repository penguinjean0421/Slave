# Slave
**Slave**는 서버 관리를 중심으로 실시간 로그 모니터링, 유틸리티 기능을 제공하는 다기능 디스코드 봇입니다. `config.json`을 통한 자동 서버 설정을 지원하며, `환경 변수(.env)`를 사용하여 보안성을 극대화했습니다.

## 초대하기
- **[ 🔗 Slave 초대하기 ](https://buly.kr/D3g9oYV)** 
    - ⚠️ 주의: 봇이 정상 작동하려면 서버 내에서 '관리자' 권한이 필요합니다.

## ✨ 주요 기능 (Key Features)
### 1. 🛠️ 서버 관리 (Moderation)
- 음성 채널 제어: 유저 뮤트/데픈(시간 설정 가능), 음성 채널 강제 퇴장(vckick).
- 유저 제재: 타임아웃(채팅 금지), 추방(Kick), 차단(Ban/Unban).
- 스마트 파싱: 10s, 5m, 1h, 1d 등 직관적인 시간 단위 지원.

### 2. 📝 실시간 로그 시스템 (Logging)
- 활동 로그: 멤버 입퇴장, 메시지 수정/삭제 내용 실시간 추적.
- 음성 로그: 채널 입장/퇴장 및 이동 경로 기록.
- 처벌 전용 로그: punish 채널을 별도로 지정하여 관리 내역만 따로 보관 가능.

### 3. ⚙️ 설정 (System)
- 자동 구성: 봇 입장 시 서버 정보를 config.json에 자동 등록 및 갱신.
- 접두사 관리: .env에서 설정한 여러 개의 접두사(Prefix)를 동시에 지원

### 4. 🔗 유틸리티 & 정보 (Utility)
- Github 검색: 등록된 프로젝트나 프로필로 바로가는 링크 제공.
- 결정 도우미: choose 명령어로 여러 선택지 중 하나를 무작위 선택.
- 메뉴 추천: 상황(아침/점심/저녁/야식)이나 종류(한식/중식 등)별 메뉴 추천.

## 🚀 시작하기 (Getting Started)
### 1. 요구 사항 (Requirements)
- Python 3.8 이상
- Discord Developer Portal에서 발급받은 봇 토큰

### 2. 설치 및 실행 (Installation)
```Bash
# 저장소 복제
git clone https://github.com/penguinjean0421/Slave.git
cd Slave

# 필수 라이브러리 설치
pip install -r requirements.txt

# 봇 실행
python main.py
```

### 3. 환경 변수 설정 (.env)
`.env.example`을 참고하여 프로젝트 루트에 `.env` 파일을 생성하세요.
```Ini, TOML
# Discord Token (절대 공유 금지)
BOT_TOKEN=your_token_here_do_not_share

# Prefixes (여러 개 설정 시 콤마(,)로 구분)
BOT_PREFIXES=!

# API 
# WEATHER_API_KEY=your_api_key_here
```

### ⚠️ 중요 보안 및 운영 팁
- **보안**: `.env`와 `config.json`은 민감한 정보가 포함되어 있으므로 **절대 GitHub에 업로드하지 마세요.** (이미 `.gitignore`에 등록되어 있는지 꼭 확인하세요!)
- **권한**: 봇이 로그 추적 및 멤버 관리 기능을 정상적으로 수행하려면 서버 내에서 **'관리자(Administrator)'** 권한이 필요합니다.

## ⚙️ 서버 설정 및 구조 (Server Configuration)
Slave는 각 서버의 독립적인 운영을 위해 `config.json` 파일을 사용합니다. 봇이 서버에 입장하거나 명령어를 수신하면 해당 서버의 고유 ID(GID)를 키로 하는 설정 데이터가 자동으로 생성됩니다.

### 1. 채널 설정 명령어 (Admin Only)
최초 생성 시 채널 관련 ID값은 None으로 설정됩니다. 관리자 권한을 가진 사용자가 아래 명령어를 입력하여 각 기능을 활성화하세요.

- `!set log [#채널]` : 메시지 수정/삭제 등 일반 활동 로그 채널 지정
- `!set punish [#채널]` : 뮤트, 타임아웃, 차단 등 제재 내역 로그 채널 지정
- `!set bot [#채널]` : 봇 명령어 사용이 허용되는 전용 채널 지정

### 2. `config.json` 상세 데이터 구조
구조 파악을 돕기 위해 `config.example.json`을 제공합니다. 봇 내부에서 관리되는 데이터 스키마는 다음과 같습니다.
| 필드명 (Key) |  초기값 (Default) |  설명 |  업데이트 방법 |
| :---: | :---: | :---: | :---: |
| `server_name` |  `guild.name` |  서버의 현재 이름 |  서버 이름 변경 시 자동 갱신 |
| `owner_id` |  `guild.owner_id` |  서버 소유자의 고유 ID |  자동 관리 |
| `owner_name` |  `str(guild.owner)` |  서버 소유자의 이름 및 태그 |  자동 갱신 |
| `log_channel_id` |  `None` |  일반 활동 로그 채널 ID |  `!set log` 명령어 |
| `punish_log_channel_id` |  `None` |  제재(처벌) 내역 로그 채널 ID |  `!set punish` 명령어 |
| `command_channel_id` |  `None` |  봇 명령어 전용 채널 ID |  `!set bot` 명령어 |

### 3. 데이터 관리 특징
- 자동 생성 및 갱신: 봇이 서버 정보를 감지하여 기본 틀을 생성하며, 서버 이름이나 소유자 변경 시 실시간으로 데이터를 동기화합니다.
- 영속성 유지: 설정된 값은 즉시 파일에 저장(`save_config`)되어 봇이 재시작되어도 설정이 유지됩니다.
- ⚠️ 보안 주의: `config.json`에는 서버 고유 ID와 상세 채널 정보가 담겨 있습니다. 개인정보 보호 및 보안을 위해 절대 외부에 공유하거나 GitHub에 업로드하지 마세요. (본 프로젝트는 `.gitignore`를 통해 해당 파일을 추적 대상에서 제외하고 있습니다.)

## 📋 명령어 요약 (Command Summary)
| 명령어 | 설명 | 예시 | 권한 |
| :---: | :---: | :---: | :---: |
| `!help` | 전체 명령어 가이드 확인 | `!help, !help 관리자` | 유저 |
| `!mute` | 음성 뮤트 (시간제 가능) | `!mute @유저 10m` | **관리자** |
| `!timeout` | 유저 타임아웃 적용 | `!timeout @유저 1h 사유` | **관리자**
| `!github` | 등록된 깃허브 링크 출력 | `!github 과제` | 유저 |
| `!choose` | 선택지 중 하나를 무작위 선택 | `!choose 자장면 짬뽕` | 유저 |
| `!menu` | 상황/종류별 메뉴 추천 | `!menu 점심`, `!menu 일식` | 유저 |
| `!credit` | 개발자 정보 확인 | `!credit` | 유저 |

## 📂 프로젝트 구조 (Project Structure)
```Plaintext
.
├── cogs/
│   ├── github.py       # 깃허브 링크 및 검색 로직
│   ├── info.py         # 도움말, 크레딧, 입장 알림
│   ├── system.py       # 로그 시스템 및 관리 명령어
│   └── utility.py      # 기타 유틸리티 기능 (choose 등)
├── .env                # [보안] 봇 토큰 및 환경 변수 설정 (GitHub 제외)
├── .env.example        # 환경 변수 설정 샘플 파일
├── .gitignore          # Git 추적 제외 목록 설정 파일
├── config.json         # [자동생성] 서버별 상세 설정 데이터 (GitHub 제외)
├── config.example.json # 서버 설정 데이터 샘플 파일
├── main.py             # 봇 실행 메인 파일
├── README.md           # 프로젝트 안내 및 사용법
└── requirements.txt    # 설치 필요한 라이브러리 목록
```

## 👤 Credits
- **Developer**: [penguinjean0421](https://github.com/penguinjean0421)
- Illustrator: aram
- Supporter: 목대 겜소과 친목 디코

## 📬 연락처 (Contact)
프로젝트에 대한 문의나 피드백은 아래 채널을 통해 연락주세요!

- **Email:** `penguinjean0421@gmail.com`
- **Discord:** `penguinjean0421`
- **GitHub:** [penguinjean0421](https://github.com/penguinjean0421)

## 📜 라이선스 (License)
Copyright 2026. **penguinjean0421** All rights reserved.
이 프로젝트의 코드와 리소스를 무단으로 복제, 수정, 배포하는 것을 금지합니다. 
개인적인 학습 목적으로만 참고해 주시기 바랍니다.