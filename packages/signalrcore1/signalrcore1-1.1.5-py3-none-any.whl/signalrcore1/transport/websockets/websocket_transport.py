import websocket
import threading
import requests
import traceback
import time
import ssl

from websocket import WebSocketBadStatusException

from .reconnection import ConnectionStateChecker
from .connection import ConnectionState
from ...messages.ping_message import PingMessage
from ...hub.errors import HubError, UnAuthorizedHubError
from ...protocol.messagepack_protocol import MessagePackHubProtocol
from ..base_transport import BaseTransport
from ...helpers import Helpers


class WebsocketTransport(BaseTransport):
    def __init__(self,
                 url="",
                 headers=None,
                 keep_alive_interval=15,
                 reconnection_handler=None,
                 verify_ssl=False,
                 skip_negotiation=False,
                 enable_trace=False,
                 get_bearer_token=None,
                 on_error=None,
                 **kwargs):
        super(WebsocketTransport, self).__init__(**kwargs)
        self._ws = None
        self.enable_trace = enable_trace
        self._thread = None
        self.skip_negotiation = skip_negotiation
        self.url = url
        self._on_error = on_error
        if headers is None:
            self.headers = dict()
        else:
            self.headers = headers
        self.get_bearer_token = get_bearer_token
        self.handshake_received = False
        self.token = None  # auth
        self.state = ConnectionState.disconnected
        self.connection_alive = False
        self._thread = None
        self._ws = None
        self.verify_ssl = verify_ssl
        self._keep_alive_interval = keep_alive_interval
        self.connection_checker = ConnectionStateChecker(
            lambda: self.send(PingMessage()),
            keep_alive_interval
        )
        self.reconnection_handler = reconnection_handler
        self.reconnect_in_any_case = True

        if len(self.logger.handlers) > 0:
            websocket.enableTrace(self.enable_trace, self.logger.handlers[0])

    def is_running(self):
        return self.state != ConnectionState.disconnected

    def initialize_auth_header(self):
        if self.get_bearer_token is not None:
            try:
                token = self.get_bearer_token()
                self.logger.debug(f"Token: {token}")
                self.headers["Authorization"] = "Bearer " + token
            except Exception as e:
                self.logger.error(f"Error during initializing auth ex:{e}")

    def stop(self, reconnect_in_any_case=False):
        self.logger.warning(f'stop: connection_checker.running {self.connection_checker.running}')
        self.connection_checker.stop()
        self.reconnect_in_any_case = reconnect_in_any_case
        if self._ws is not None:
            self._ws.close()
        self.state = ConnectionState.disconnected
        self.handshake_received = False

    def start(self):
        if not self.skip_negotiation:
            self.negotiate()

        if self.state == ConnectionState.connected:
            self.logger.warning("Already connected unable to start")
            return False

        self.state = ConnectionState.connecting
        self.logger.debug("start url:" + self.url)

        self.initialize_auth_header()
        self.logger.debug(f"Function start Authorization:{self.headers['Authorization']}")
        self._ws = websocket.WebSocketApp(
            self.url,
            header=self.headers,
            on_message=self.on_message,
            on_error=self.on_socket_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )
        self._ws.run_forever(
            sslopt={"cert_reqs": ssl.CERT_NONE} if not self.verify_ssl else {}
        )
        return True

    def negotiate(self):
        negotiate_url = Helpers.get_negotiate_url(self.url)
        self.logger.debug("Negotiate url:{0}".format(negotiate_url))

        self.initialize_auth_header()
        self.logger.debug("Authorization:{0}".format(self.headers["Authorization"]))
        response = requests.post(
            negotiate_url, headers=self.headers, verify=self.verify_ssl)
        self.logger.debug(
            "Response status code{0}".format(response.status_code))

        if response.status_code != 200:
            raise HubError(response.status_code) if response.status_code != 401 else UnAuthorizedHubError()

        data = response.json()

        if "connectionId" in data.keys():
            self.url = Helpers.encode_connection_id(
                self.url, data["connectionId"])

        # Azure
        if 'url' in data.keys() and 'accessToken' in data.keys():
            Helpers.get_logger().debug(
                "Azure url, reformat headers, token and url {0}".format(data))
            self.url = data["url"] \
                if data["url"].startswith("ws") else \
                Helpers.http_to_websocket(data["url"])
            self.token = data["accessToken"]
            self.headers = {"Authorization": "Bearer " + self.token}

    def evaluate_handshake(self, message):
        self.logger.debug("Evaluating handshake {0}".format(message))
        msg, messages = self.protocol.decode_handshake(message)
        if msg.error is None or msg.error == "":
            self.handshake_received = True
            self.state = ConnectionState.connected
            if self.reconnection_handler is not None:
                self.reconnection_handler.reconnecting = False
                if not self.connection_checker.running:
                    self.connection_checker.start()
        else:
            self.logger.error(f"evaluate_handshake message: {msg.error}")
            self.on_socket_error(self._ws, msg.error)
            self.stop(True)
            self.state = ConnectionState.disconnected
            # reconnect
            # self.send(PingMessage())
        return messages

    def on_open(self, _):
        self.logger.debug("-- web socket open --")
        msg = self.protocol.handshake_message()
        self.send(msg)

    def on_close(self, callback, close_status_code, close_reason):
        self.logger.warning("-- web socket close --")
        self.logger.warning(f'connection_checker.running {self.connection_checker.running}')
        self.logger.info(close_status_code)
        self.logger.info(close_reason)
        self.state = ConnectionState.disconnected
        if self._on_close is not None and callable(self._on_close):
            self._on_close()
        if callback is not None and callable(callback):
            callback()
        if close_status_code is None and self.reconnect_in_any_case:
            self.logger.debug("Send ping for reconnect")
            self.send(PingMessage())

    def on_reconnect(self):
        self.logger.debug("-- web socket reconnecting --")
        self.state = ConnectionState.disconnected
        if self._on_close is not None and callable(self._on_close):
            self._on_close()

    def on_socket_error(self, app, error):
        """
        Args:
            _: Required to support websocket-client version equal or greater than 0.58.0
            error ([type]): [description]

        Raises:
            HubError: [description]
        """
        self.logger.debug("-- web socket error --")
        self.logger.error(traceback.format_exc(10, True))
        self.logger.error("{0} {1}".format(self, error))
        self.logger.error("{0} {1}".format(error, type(error)))
        if self._on_error:
            self._on_error(error)

        # self._on_close()
        # self.state = ConnectionState.disconnected
        # raise HubError(error)

    def on_message(self, app, raw_message):
        self.logger.debug("Message received{0}".format(raw_message))
        if not self.handshake_received:
            messages = self.evaluate_handshake(raw_message)
            if self._on_open is not None and callable(self._on_open):
                self.state = ConnectionState.connected
                self._on_open()

            if len(messages) > 0:
                return self._on_message(messages)

            return []

        return self._on_message(
            self.protocol.parse_messages(raw_message))

    def send(self, message, **kwargs):
        self.logger.debug("Sending message {0}".format(message))
        try:
            self._ws.send(
                self.protocol.encode(message),
                opcode=0x2
                if type(self.protocol) == MessagePackHubProtocol else
                0x1)
            self.connection_checker.last_message = time.time()
            if self.reconnection_handler is not None:
                self.reconnection_handler.reset()
        except (
                websocket._exceptions.WebSocketConnectionClosedException,
                websocket._exceptions.WebSocketBadStatusException,
                OSError, WebSocketBadStatusException) as ex:
            self.handshake_received = False
            self.logger.warning("Connection closed 1 {}".format(ex))
            self.logger.warning(f"Connection closed {ex}")
            self.state = ConnectionState.disconnected
            if self.reconnection_handler is None:
                if self._on_close is not None and \
                        callable(self._on_close):
                    self._on_close()
                raise ValueError(str(ex))
            # Connection closed
            self.handle_reconnect()
        except Exception as ex:
            self.logger.error(f"Error during sending message: {ex}")
            raise ex

    def handle_reconnect(self):
        if not self.reconnection_handler.reconnecting and self._on_reconnect is not None and \
                callable(self._on_reconnect):
            self._on_reconnect()
        self.reconnection_handler.reconnecting = True
        try:
            try:
                self.stop(True)
            except Exception as e:
                self.logger.error(f"Error during stop ex: {e}")
            self.start()
        except Exception as ex:
            self.logger.error(f"Error during start ex: {ex}")
            sleep_time = self.reconnection_handler.next()
            self.logger.error("reconnection_handler.next")
            self.deferred_reconnect(sleep_time)

    def deferred_reconnect(self, sleep_time):
        time.sleep(sleep_time)
        try:
            self.logger.warning("deferred_reconnect")
            if not self.connection_alive:
                self.logger.debug("connection_alive")
                self.send(PingMessage())
        except Exception as ex:
            self.logger.error(ex)
            self.reconnection_handler.reconnecting = False
            self.connection_alive = False
