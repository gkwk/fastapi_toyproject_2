from starlette import status

http_exception_params = {
    "already_user_name_existed": {
        "status_code": status.HTTP_409_CONFLICT,
        "detail": "동일한 이름을 사용중인 유저가 이미 존재합니다.",
    },
    "already_user_email_existed": {
        "status_code": status.HTTP_409_CONFLICT,
        "detail": "동일한 이메일을 사용중인 유저가 이미 존재합니다.",
    },
    "user_not_existed": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "유저가 존재하지 않습니다.",
    },
    "user_not_matched": {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "권한이 없습니다.",
    },
    "scopes_not_matched": {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "접근 권한이 없습니다.",
    },
    "ai_model_not_found": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "AI 모델이 존재하지 않습니다.",
    },
    "ai_log_not_found": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "AI 로그가 존재하지 않습니다.",
    },
    
    "not_user": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "유저가 존재하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "not_admin": {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "관리자 권한이 존재하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "not_verified_password": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "패스워드가 일치하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "not_verified_token": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "토큰이 유효하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "banned": {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "차단되었습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
}