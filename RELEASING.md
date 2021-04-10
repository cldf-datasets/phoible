# Releasing PHOIBLE

1. Update the data in `raw/` running
   ```shell
   cldfbench download cldfbench_phoible.py
   ```
2. Re-create the CLDF data running
   ```shell
   cldfbench makecldf cldfbench_phoible.py
   ```
3. Make sure the CLDF is valid:
   ```shell
   pytest
   ```
4. Create metadata for Zenodo:
   ```shell
   cldfbench zenodo cldfbench_phoible.py
   ```
5. Create the release commit:
   ```shell
   git commit -a -m "release <VERSION>"
   ```
6. Create a release tag:
   ```
   git tag -a v<VERSION> -m"<VERSION> release"
   ```
7. Create a release from this tag on https://github.com/cldf-datasets/phoible/releases
8. Verify that data and metadata has been picked up by Zenodo correctly,
   and copy the citation information into the GitHub release description.
