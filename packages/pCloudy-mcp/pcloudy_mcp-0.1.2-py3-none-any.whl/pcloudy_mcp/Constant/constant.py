from urllib.parse import urlparse

from ..utils.config import Config

config = Config()
base_url = config.userdetail.pcloudy_cloud_url


class McpServer:
    """
    This class represents the MCP server configuration for the pCloudy MCP application.
    It includes server name and version.
    """

    SERVER_NAME = "pCloudy-mcp-tool"
    SERVER_VERSION = "0.1.0"


class QpilotServerEndpoints:
    """This class contains the QPilot server endpoints."""

    QPILOT_SERVER_URL = "https://prod-backend.qpilot.pcloudy.com"

    production_host = [
        "ind-west.pcloudy.com",
        "us.pcloudy.com",
        "sg.pcloudy.com",
        "ind-west2.pcloudy.com",
        "uae.pcloudy.com",
    ]

    @classmethod
    def get_qpilot_origin(cls):
        parsed_url = urlparse(base_url)
        return (
            "https://device.pcloudy.com"
            if parsed_url.hostname in cls.production_host
            else base_url
        )


class PcloudyApiEndpoints:
    """
    This class contains the API endpoints for pCloudy.
    """

    AUTHENTICATE = f"{base_url}/api/access"
    GET_DEVICE_LIST = f"{base_url}/api/devices"
    BOOK_DEVICE = f"{base_url}/api/book_device"
    LIVE_VIEW_URL = f"{base_url}/api/get_device_url"
    RELEASE_DEVICE = f"{base_url}/api/release_device"
    UPLOAD_APP = f"{base_url}/api/upload_file"
    AVALIABLE_APPS = f"{base_url}/api/drive"
    INSTALL_AND_LAUNCH_APP = f"{base_url}/api/install_app"
    INITIATE_IOS_RESIGN = f"{base_url}/api/resign/initiate"
    PROGRESS_IOS_RESIGN = f"{base_url}/api/resign/progress"
    DOWNLOAD_IOS_RESIGN = f"{base_url}/api/resign/download"

    # QPilot Endpoints
    GET_CREDIT_BALANCE = f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/get-qpilot-credits-left"
    GET_PROJECT_LIST = (
        f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/project/fetch"
    )
    CREATE_PROJECT = (
        f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/project/create"
    )
    GET_TESTSUITE_LIST = (
        f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/get-test-suites"
    )
    CREATE_TESTSUITE = (
        f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/create-test-suite"
    )
    GET_TESTCASE_LIST = (
        f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/get-tests"
    )
    CREATE_TESTCASE = (
        f"{QpilotServerEndpoints.QPILOT_SERVER_URL}/api/v1/qpilot/create-test-case"
    )
    START_WDA_IOS = f"{base_url}/api/v2/qpilot/wda/control"
    START_APPIUM = f"{base_url}/api/v2/qpilot/appium/control"
    GENERATE_CODE = f"{base_url}/api/v2/qpilot/generate-code"


class HttpRetryConfig:
    """
    This class contains the retry configuration for HTTP requests.
    """

    MAX_RETRIES = 3
    WAIT_SECONDS = 2
    TIMEOUT = 180.0  # timeout in seconds


class Constant:
    """
    This class contains constant values used throughout the pCloudy MCP application.
    """

    mcpServer = McpServer()
    pclodyApiEndpoint = PcloudyApiEndpoints()
    httpRetryConfig = HttpRetryConfig()
    qpilot = QpilotServerEndpoints()
    TOKEN_CACHE_NAMESPACE = "pcloudy_tokens"
    TOKEN_CACHE_TTL = 5 * 24 * 60 * 60
    DURATION_TO_BOOK_DEVICE = 30  # in minutes, can be changed as per requirement
    MAXIMUM_RETRIES_RESIGN_PROGRESS = 20
