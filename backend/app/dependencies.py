from backend.app.adapters.memory import InMemoryFoodProviderRepository
from backend.app.adapters.sfgov_client import SFGovFoodProviderDataClient
from backend.app.data_manager import DataManager

repository = InMemoryFoodProviderRepository()

# Export a named client for tests to patch
sfgov_datasource = SFGovFoodProviderDataClient()

data_clients = [sfgov_datasource]

data_manager = DataManager(repository, data_clients)

async def initialize():
    # Start background data manager loop
    data_manager.start()

async def shutdown():
    await data_manager.stop()


def get_repository():
    return repository