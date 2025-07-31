import localstack.pro.core.config as config
from localstack.http import Router
from localstack.http.dispatcher import Handler as RouteHandler
from localstack.pro.core.eventstudio.database.database import get_eventstudio_db_manager
from localstack.pro.core.eventstudio.utils import EVENTSTUDIO_LOG
from localstack.pro.core.runtime.plugin import ProPlatformPlugin
class EventStudioPlugin(ProPlatformPlugin):
	name='eventstudio'
	def should_load(A):
		if not config.EVENTSTUDIO_DEV_ENABLE:return False
		EVENTSTUDIO_LOG.debug('EventStudioPlugin is enabled via EVENTSTUDIO_DEV_ENABLE');return super().should_load()
	def update_localstack_routes(B,router):from localstack.pro.core.eventstudio.api.router import EventStudioRouter as A;A(router).register_routes()
	def on_platform_ready(A):get_eventstudio_db_manager().initialize_db()
	def on_platform_shutdown(A):get_eventstudio_db_manager().shutdown_database()