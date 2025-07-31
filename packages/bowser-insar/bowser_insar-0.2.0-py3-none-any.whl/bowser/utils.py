import json
import subprocess
from functools import cache


class CredentialsError(Exception):
    """Raised when AWS credentials have expired."""


def list_bucket(
    bucket: str | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
    full_bucket_glob: str | None = None,
    aws_profile: str | None = None,
    num_workers: int = 10,
) -> list[str]:
    """Use `s5cmd` to quickly list items in a bucket.

    Parameters
    ----------
    bucket : str
        Name of the bucket.
    prefix : str, optional
        Prefix to filter by, by default "".
    suffix : str, optional
        Suffix to filter by, by default "".
    full_bucket_glob : str, optional
        Alternate to prefix/suffix. Full glob to filter by, by default None.
    aws_profile : str, optional
        AWS profile to use, by default None.
    num_workers : int, default = 10
        Number of workers to use for parallel downloads.

    Returns
    -------
    list[str]
        List of items in the bucket.
    """
    cmd = ["s5cmd", "--json", "--numworkers", str(num_workers)]
    if aws_profile:
        cmd += ["--profile", aws_profile]

    if full_bucket_glob:
        bucket_str = full_bucket_glob
    else:
        bucket_str = f"s3://{bucket}"
        if prefix:
            bucket_str += f"/{prefix}"
        if suffix:
            bucket_str += f"*{suffix}"
    cmd += ["ls", bucket_str.strip()]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=90)
    except subprocess.CalledProcessError as e:
        if "ExpiredToken" in e.stderr:
            raise CredentialsError(
                "Error downloading files: AWS credentials have expired."
            ) from e
        raise RuntimeError(f"Error listing bucket {bucket_str}: {e.stderr}") from e

    out: list[str] = []
    for line in p.stdout.splitlines():
        item = json.loads(line)
        if item["type"] == "directory":
            continue
        out.append(item["key"])
    return out


@cache
def generate_colorbar(cmap_name: str) -> bytes:
    """Generate a colorbar image using a specified matplotlib colormap.

    Parameters
    ----------
    cmap_name : str
        Name of the colormap to be used.

    Returns
    -------
    bytes
        WEBP image data as bytes
    """
    from io import BytesIO

    import matplotlib.pyplot as plt
    import numpy as np

    gradient = np.array([[0, 1]])
    fig, ax = plt.subplots(figsize=(9, 1.5))
    ax.imshow(gradient, cmap=cmap_name)
    ax.set_visible(False)

    # Create colorbar in a tightly fitted axis
    cax = fig.add_axes([0.05, 0.2, 0.9, 0.6])
    colorbar = plt.colorbar(
        ax.imshow(gradient, cmap=cmap_name), cax=cax, orientation="horizontal"
    )
    colorbar.set_ticks([])

    # Adjust subplot parameters and apply tight layout
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    buf = BytesIO()
    plt.savefig(buf, format="webp", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def desensitize_mpl_case():
    """Make `cmap` case insensitive by registering repeated cmap names."""
    import matplotlib as mpl

    cmap_names = list(mpl.colormaps)
    for name in cmap_names:
        if name.lower() in mpl.colormaps:
            continue
        mpl.colormaps.register(mpl.colormaps[name], name=name.lower())
