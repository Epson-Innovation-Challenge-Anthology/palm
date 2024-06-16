# README

인증을 위해 제공되는 API 문서입니다.

인증 이후 [서비스 API](/docs) 및 기타 인증이 필요한 API를 사용할 수 있습니다.

| 로그인 방식 | 경로 | 설명 |
| --- | --- | --- |
| 구글 웹 | [/auth/google/login](#/google/google_web_login_google_login_get) | 서버사이드에서 모두 처리합니다. (웹뷰 및 기타 리다이렉션 처리 필요) |
| 구글 OAuth | [/auth/google/token/signin](#/google/google_signin_google_token_signin_post)| 클라이언트에서 구글에 요청한 뒤 받은 ID Token 을 서버로 전송하면 처리합니다. |

## 사용법

`/auth/google/login` 혹은 `/auth/google/token/signin`을 통해 로그인을 수행하신 뒤 발급받은 `access_token`을 Header에 `Authorization`로 포함하여 요청하면 인증이 필요한 API를 사용할 수 있습니다.

### 발급된 토큰 유효기간

| 토큰 | 유효기간 |
| --- | --- |
| access_token | 1시간 |
| refresh_token | 6개월 |

### 토큰 갱신

[`/auth/token/refresh`](#/auth/refresh_refresh_post)를 통해 `refresh_token`을 이용하여 `access_token`을 갱신할 수 있습니다.

```bash
curl -X 'POST' \
  'https://palm.fly.dev/auth/refresh' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "grant_type": "refresh_token",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}'

{
  "message": "토큰이 갱신되었습니다",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 사용예시: 로그인한 사용자가 본인 프로필 정보 조회

```bash
curl -X 'GET' \
  'https://palm.fly.dev/api/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1Ni...'

{
  "message": "사용자 정보를 조회합니다.",
  "data": {
    "id": "r90q2bqf",
    "name": null,
    "auth_provider": "google",
    "email": "fakeuser@gmail.com",
    "email_newsfeed": null,
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-06-15T13:56:39.487000",
    "deactivated_at": null,
    "updated_at": null,
    "bio_links": [],
    "sex": "O",
    "profile_image": null
  }
}
```

### 로그아웃

[/auth/logout](#/auth/logout_logout_get)을 통해 로그아웃 할 수 있습니다.

```bash
curl -X 'GET' \
  'https://palm.fly.dev/auth/logout' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFjaWRkdXN0MjBAZ21haWwuY29tIiwiYXV0aF9wcm92aWRlciI6Imdvb2dsZSIsImV4cCI6MTcxODQ2NDk0OSwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.UZvoMaoLM-3fimNZ-9qROb8fipcnilq6HwuZ-zQCHIA'

{
  "message": "로그아웃 되었습니다",
  "data": null
}
```

사용하던 `access_token`은 블랙리스트에 추가되어 더 이상 사용할 수 없습니다.

<!-- markdownlint-configure-file { "MD051": false } -->
