import sys
from pathlib import Path

from conan import ConanFile

# Cache recipes import e/_shared. Checkout recipes import packages/_shared.
_recipe_dir = Path(__file__).resolve().parent
for _base in (_recipe_dir, _recipe_dir.parent):
    if (_base / "_shared").is_dir() and str(_base) not in sys.path:
        sys.path.insert(0, str(_base))
        break

from _shared import recipe_support


class matterRecipe(ConanFile):
    """Matter stack package. See recipe_support.MATTER for what it collects."""

    name = recipe_support.MATTER.name
    user = recipe_support.PACKAGE_USER
    license = recipe_support.PACKAGE_LICENSE
    author = recipe_support.PACKAGE_AUTHOR
    homepage = recipe_support.PACKAGE_HOMEPAGE
    url = recipe_support.PACKAGE_URL
    topics = recipe_support.PACKAGE_TOPICS
    python_requires = recipe_support.PYTHON_REQUIRES
    release_stream_channel = recipe_support.read_package_metadata(
        "release_stream_channel", recipe_file=__file__
    )
    description = recipe_support.MATTER.description
    sl_metadata = recipe_support.SL_METADATA
    revision_mode = "hash"
    _spec = recipe_support.MATTER

    options = recipe_support.slt_options()
    default_options = recipe_support.slt_default_options()

    def set_version(self):
        recipe_support.set_version(self)

    def requirements(self):
        recipe_support.apply_requirements(self)

    def slt_requirements(self):
        return {"zap": "~", "slc-cli": "~"}

    def layout(self):
        recipe_support.apply_layout(self)

    def export(self):
        recipe_support.export_recipe_files(self)

    def package_id(self):
        self.info.clear()

    def package(self):
        recipe_support.package_from_spec(self)

    def build(self):
        recipe_support.write_filelists(self)

    def package_info(self):
        recipe_support.apply_package_info(self)
