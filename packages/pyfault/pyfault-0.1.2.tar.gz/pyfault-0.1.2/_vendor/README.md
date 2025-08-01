# Vendoring info

This package uses the [`vendorize`](https://pypi.org/project/vendorize/) package
to simplify vendoring of the tblib dependency.

To re-vendor, install vendorize and run `python-vendorize` in the root
directory.

If you have the `uv` package manager installed, you can run
`uvx --from vendorize python-vendorize`.

You may need to remove the `_vendor/tblib*` directories first...
[rerunnable python-vendorize](https://github.com/mwilliamson/python-vendorize/issues/9)
