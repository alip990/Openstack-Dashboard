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
