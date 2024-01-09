# Kashan University cloud

## Project Overview

This README provides instructions on how to install Docker Engine on an Ubuntu server for running the project locally. The project is a Django-based web application with a Celery task queue, using PostgreSQL as the database, Swagger UI for API documentation, and Redis as a message broker.

## Prerequisites
### Docker installation
Uninstall Old Versions:
1. Before installing Docker Engine, uninstall any conflicting packages:

```bash
sudo apt-get remove docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc
```
2. Set Up Docker's Apt Repository

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
3. Install Docker Packages

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Clone Project
    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

### Build and start project
    ```bash
    docker-compose up --build
    ```



if you upload and create new image in openstack you should set these meta for that image

متا دیتایی که به image های که در اپن ساخته میشه باید اضافه شوند و image ها باید public باشند.
os_admin_user,
os_distro,
photo,
Os_version,

```console
openstack image set \
    --property os_distro=scsi \
    --property os_version=ide \
    --property photo=https://cdn.freebiesupply.com/logos/large/2x/ubuntu-4-logo-png-transparent.png \
    --property os_admin_user=alireza \
    cirros
```

I use microstack to develop the app,

## Get microStack credential

```console
sudo snap get microstack config.credentials.keystone-password
```
