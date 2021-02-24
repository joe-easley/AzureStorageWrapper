# AzureStorageWrapper
[![Actions Status](https://github.com/joe-easley/AzureStorageWrapper/workflows/Behave%20Tests/badge.svg)](https://github.com/joe-easley/AzureStorageWrapper/actions)


A wrapper for azure storage tools

Tests currently failing due to azure test account being temporarily unavailable. Blob functions and most file functions have been recently tested and are working as expected.

## Using the storagewrapper

This repo includes a library ('storagewrapper') that wraps around azure storage sdks. In time it will contain all methods contained within the standard SDKs, as well as some bespoke functions, for example recursively deleting on a file share, which is currently unsupported directly by azure python SDK.

Its intent is to simplify the SDK's further so that you only ever need to interact with one client per storage type. Currently this library supports operations with blob, file share and queue storeage.

For further information on how to use this library, and see what functions are currently supported click [here](https://github.com/joe-easley/AzureStorageWrapper/blob/main/main/README.md)

## Other

Pull requests and feedback are welcome. 