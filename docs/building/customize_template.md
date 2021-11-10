# Customizing the OSbuild templates

The manifests currently include a number of variables, which appear in the `mpp-vars` section of the OSbuild template manifests.

The variables definitions in `mpp-vars` may look like the following example:
```
  "mpp-vars": {
    "rootfs_uuid": {"mpp-format-string": "{__import__('uuid').uuid1()}"},
    "bootfs_uuid": {"mpp-format-string": "{__import__('uuid').uuid1()}"},
    "rootfs_size": 4294967296,
    "homefs_size": {"mpp-format-string": "{rootfs_size}"}
  },
```

This section defines four variables: `rootfs_uuid`, `bootfs_uuid`, `rootfs_size`
and `homefs_size`.

* `rootfs_uuid` and `bootfs_uuid` dynamically generate when you run the equivalent of the following
  python code:

     ``` python
        import uuid
        uuid.uuid1()
     ```

* `rootfs_size` is hardcoded to `4294967296` bytes.

* `homefs_size` is equal to `rootfs_size`.

You can customize these variables one of two ways:

* Directly edit the template and set their respected values.

* Specify the variable to the `osbuild-mpp` tool using the `-D` argument. See `--help` for more information.
