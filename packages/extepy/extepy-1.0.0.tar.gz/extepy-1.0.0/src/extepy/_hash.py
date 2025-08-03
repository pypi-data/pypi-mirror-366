import hashlib


def filehash(path, method="sha256", batchsize=4096):
    """Get the hash value of a file.

    Parameters:
        path (str): Path of the file.
        method (str): Hash method. Default is "sha256".
        batchsize (int): Size of each read chunk. Default is 4096 bytes.

    Returns:
        str:

    Example:
        Create a temporary file, and get its hash.

        >>> from tempfile import NamedTemporaryFile
        >>> tfile = NamedTemporaryFile(delete=False)
        >>> _ = tfile.write(b'Hello world!')  # Write 12 bytes to the file
        >>> filepath = tfile.name
        >>> filehash(filepath, method="sha256")
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    hasher = getattr(hashlib, method)()
    with open(path, "rb") as f:
        def fun():
            return f.read(batchsize)
        for chunk in iter(fun, b""):
            hasher.update(chunk)
    result = hasher.hexdigest()
    return result
