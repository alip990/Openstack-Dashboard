from .models import Flavor
from .api.nova import get_flavor_list


def seed_flavors():
    print('Start seeding flavors ...')

    flavors = get_flavor_list()

    for flavor_data in flavors:
        flavor_id = flavor_data['id']

        try:
            # Check if the flavor already exists in the database
            flavor = Flavor.objects.get(id=flavor_id)

            # Check if any parameter of the flavor has changed
            if (
                flavor.name != flavor_data['name'] or
                flavor.cpu_core != flavor_data['cpu_core'] or
                flavor.ram != flavor_data['ram'] or
                flavor.disk != flavor_data['disk']
            ):
                # Update the flavor parameters
                flavor.name = flavor_data['name']
                flavor.cpu_core = flavor_data['cpu_core']
                flavor.ram = flavor_data['ram']
                flavor.disk = flavor_data['disk']

                flavor.save()
                print(f"Updated flavor '{flavor.name}'")
            else:
                print(f"No changes for flavor '{flavor.name}'")

        except Flavor.DoesNotExist:
            # Flavor does not exist in the database, create a new one
            flavor = Flavor(
                id=flavor_data['id'],
                name=flavor_data['name'],
                cpu_core=flavor_data['cpu_core'],
                ram=flavor_data['ram'],
                disk=flavor_data['disk'],
                rating_per_hour=0,
            )
            flavor.save()
            print(f"Created flavor '{flavor.name}'")
    print('Seeding flavors Finished !')
