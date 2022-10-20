# COMMON
class UnknownError(Exception):
    """
    Try to repeat the request later.
    """
    pass


class AppDisabled(Exception):
    pass


class UnknownMethod(Exception):
    """
    Check if the name of the called method is correct: vk.com/dev/methods
    """
    pass


class InvalidSignature(Exception):
    pass


class UserAuthorizationError(Exception):
    """
    Make sure you are using the correct authorization scheme.
    """
    pass


class RequestLimitExceeded(Exception):
    """
    Set a longer interval between calls or use the execute method.
    For more information about the restrictions on the frequency of calls, see the page vk.com/dev/api_requests
    """
    pass


class InvalidAppPermissions(Exception):
    """
    Check whether the necessary access rights have been obtained during authorization.
    This can be done using the account.getAppPermissions method.
    """
    pass


class InvalidRequest(Exception):
    """
    Check the query syntax and the list of parameters used (you can find it on the method description page).
    """
    pass


class TooManySimilarActions(Exception):
    """
    It is necessary to reduce the number of similar requests. For more efficient work, you can use execute or JSONP.
    """
    pass


class InternalServerError(Exception):
    """
    Try to repeat the request later.
    """
    pass


class AppEnabledInTestMode(Exception):
    """
    In test mode, the application must be turned off or the user must be logged in.
    Turn off the app in settings https://vk.com/editapp?id ={Your API_ID}
    """
    pass


class CaptchaRequired(Exception):
    """
    The process of handling this error is described in detail on the page: https://dev.vk.com/api/captcha-error
    """
    pass


class AccessDenied(Exception):
    """
    Make sure that you are using the correct identifiers and that the full version of the site
    has access to the content for the current user.
    """
    pass


class HTTPSConnectionRequired(Exception):
    """
    Requests over HTTPS are required, because the user has enabled a setting that requires work via a secure connection.
    To avoid such an error, in a Standalone application,
    you can pre-check the status of this setting with the user using the account.getInfo method.
    """
    pass


class UserValidationRequired(Exception):
    """
    The action requires confirmation — it is necessary to redirect the user to the service page for validation.
    """
    pass


class UserDeletedOrBlocked(Exception):
    """
    The user's page has been deleted or blocked
    """
    pass


class ActionAllowedOnlyForStandaloneApp(Exception):
    """
    If the error occurs despite the fact that your application is of the Standalone type, make sure that when you log in
    , use redirect_uri=https://oauth.vk.com/blank.html . For more information, see vk.com/dev/auth_mobile .
    """
    pass


class ActionAllowedOnlyForStandaloneAndOpenAPIApp(Exception):
    pass


class MethodDisabled(Exception):
    """
    All the current VK API methods that are currently available are listed here: vk.com/dev/methods
    """
    pass


class UserConfirmationRequired(Exception):
    """
    Confirmation from the user is required
    """
    pass


class InvalidCommunityKey(Exception):
    """
    The community access key is invalid.
    """
    pass


class InvalidAppKey(Exception):
    """
    The community access key is invalid.
    """
    pass


class MethodCallLimitReached(Exception):
    """
    The quantitative limit on method invocation has been reached
    """
    pass


class PrivateUserProfile(Exception):
    """
    The information requested about the profile is not available with the access key used
    """
    pass


class ParamInvalidOrMissed(Exception):
    """
    One of the required parameters was not passed or incorrect.
    Check the list of required parameters and their format on the method description page.
    """
    pass


class InvalidApplicationAPIID(Exception):
    """
    Invalid API application ID.
    """
    pass


class InvalidUserID(Exception):
    """
    Make sure you are using the correct ID. You can get an ID by a short name using the utils.resolveScreenName method.
    """
    pass


class InvalidTimestamp(Exception):
    """
    You can get the current value using the utils.getServerTime method.
    """
    pass


class AlbumAccessDenied(Exception):
    """
    Make sure that you are using the correct identifiers (for users owner_id is positive, for communities — negative),
    and access to the requested content for the current user is in the full version of the site.
    """
    pass


class AudioAccessDenied(Exception):
    """
    Make sure that you are using the correct identifiers (for users owner_id is positive, for communities — negative),
    and access to the requested content for the current user is in the full version of the site.
    """
    pass


class GroupAccessDenied(Exception):
    """
    Make sure that the current user is a member or leader of the community (for private and private groups and meetings)
    """
    pass


class AlbumIsFull(Exception):
    """
    Before proceeding, you need to remove unnecessary objects from the album or use another album.
    """
    pass


class ActionIsProhibited(Exception):
    """
    The action is prohibited. You must enable voice translations in the app settings.
    Check the app settings: https://vk.com/editapp?id ={Your API_ID}&section=payments
    """
    pass


class AdvertiserCabinetNoRights(Exception):
    """
    There are no rights to perform these operations with the advertising cabinet.
    """
    pass


class AdvertiserCabinetError(Exception):
    """
    There are no rights to perform these operations with the advertising cabinet.
    """
    pass


ERROR_MAP = {
    1: UnknownError,
    2: AppDisabled,
    3: UnknownMethod,
    4: InvalidSignature,
    5: UserAuthorizationError,
    6: RequestLimitExceeded,
    7: InvalidAppPermissions,
    8: InvalidRequest,
    9: TooManySimilarActions,
    10: InternalServerError,
    11: AppEnabledInTestMode,
    14: CaptchaRequired,
    15: AccessDenied,
    16: HTTPSConnectionRequired,
    17: UserValidationRequired,
    18: UserDeletedOrBlocked,
    20: ActionAllowedOnlyForStandaloneApp,
    21: ActionAllowedOnlyForStandaloneAndOpenAPIApp,
    23: MethodDisabled,
    24: UserConfirmationRequired,
    27: InvalidCommunityKey,
    28: InvalidAppKey,
    29: MethodCallLimitReached,
    30: PrivateUserProfile,
    100: ParamInvalidOrMissed,
    101: InvalidApplicationAPIID,
    113: InvalidUserID,
    150: InvalidTimestamp,
    200: AlbumAccessDenied,
    201: AudioAccessDenied,
    203: GroupAccessDenied,
    300: AlbumIsFull,
    500: ActionIsProhibited,
    600: AdvertiserCabinetNoRights,
    603: AdvertiserCabinetError
}
