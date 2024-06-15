class BlacklistTokenError(Exception):
    """
    블랙리스트 토큰 처리 관련 오류
    """


class GoogleModuleError(Exception):
    """
    구글 모듈 관련 오류
    """


class KakaoModuleError(Exception):
    """
    카카오 모듈 관련 오류
    """


class UserAlreadyExistsError(Exception):
    """
    유저가 이미 존재할 때 발생하는 오류
    """


class DeleteColoringResultError(Exception):
    """
    컬러링 결과 삭제 실패 오류
    """


class RemoveColoringHashFromUserError(Exception):
    """
    유저 정보에서 해시 아이디 삭제 실패 오류
    """
