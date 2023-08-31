from service.api.keystone import get_admin_session
from .models import Flavor
from .api.nova import get_flavor_list

import logging

LOG = logging.getLogger(__name__)


def seed_flavors():
    LOG.debug('Start seeding flavors ...')
    session = get_admin_session()

    flavors = get_flavor_list(session)

    for flavor_data in flavors:
        flavor_id = flavor_data['id']
        LOG.debug(f"Flavor id '{flavor_id}'")

        try:
            # Check if the flavor already exists in the database
            flavor = Flavor.objects.get(id=flavor_id)

            # Check if any parameter of the flavor has changed
            if (
                flavor.name != flavor_data['name'] or
                flavor.cpu_core != flavor_data['cpu']['size'] or
                flavor.ram != flavor_data['ram']['size'] or
                flavor.disk != flavor_data['disk']['size']
            ):
                # Update the flavor parameters
                flavor.name = flavor_data['name']
                flavor.cpu_core = flavor_data['cpu']['size']
                flavor.ram = flavor_data['ram']['size']
                flavor.disk = flavor_data['disk']['size']

                flavor.save()
                LOG.debug(f"Updated flavor '{flavor.name}'")
            else:
                LOG.debug(f"No changes for flavor '{flavor.name}'")

        except Flavor.DoesNotExist:
            # Flavor does not exist in the database, create a new one
            LOG.debug('----------------------------------------------------')
            LOG.debug(flavor_data)
            LOG.debug('----------------------------------------------------')

            flavor = Flavor(
                id=flavor_data['id'],
                name=flavor_data['name'],
                cpu_core=flavor_data['cpu']['size'],
                ram=flavor_data['ram']['size'],
                disk=flavor_data['disk']['size'],
                rating_per_hour=0,
            )
            flavor.save()
            LOG.debug(f"Created flavor '{flavor.name}'")
    LOG.debug('Seeding flavors Finished !')
